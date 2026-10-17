"""
Dermastack Hybrid CNN + Vision Transformer Architecture.

Architecture Overview:
----------------------
1. CNN Backbone:
   Extracts high-resolution local spatial features, lesion margins, micro-textures,
   and pigment distribution patterns through residual convolutional stages.
   The final convolutional layer acts as the target layer for visual explanations (Grad-CAM).

2. Vision Transformer (ViT) Stage:
   Flattens and linearly projects intermediate spatial feature maps into sequence tokens,
   adds positional embeddings, and applies multi-head self-attention (MHSA) to model
   long-range semantic dependencies across the entire field of view.

3. Fusion & Classification Head:
   Combines local CNN pooled features and global transformer sequence representations
   via adaptive concatenation and normalized MLP projections for multi-class classification.

DISCLAIMER:
Defining or instantiating this architecture does NOT train the model. Untrained weights
produce random or uncalibrated representations. A verified, pre-trained checkpoint must
be supplied to enable clinical research inference; otherwise, the system runs in Demo Mode.
"""

from typing import Dict, Any, Optional, Tuple
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

from ml.labels import NUM_CLASSES, SKIN_CLASSES, CONFIDENCE_THRESHOLD, ENTROPY_THRESHOLD


def set_seed(seed: int = 42) -> None:
    """Set deterministic random seeds for PyTorch reproducibility."""
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class ConvBlock(nn.Module):
    """Residual convolutional block with Batch Normalization and SiLU activation."""

    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.act = nn.SiLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.shortcut(x)
        out = self.act(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += res
        return self.act(out)


class CNNBackbone(nn.Module):
    """
    Multi-stage convolutional feature extractor for skin images.
    Input:  (B, 3, 224, 224)
    Output: (B, 256, 14, 14) feature map
    """

    def __init__(self):
        super().__init__()
        # Stem: 224x224 -> 112x112
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.SiLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.SiLU(inplace=True)
        )
        # Stage 1: 112x112 -> 56x56
        self.stage1 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2),
            ConvBlock(64, 64),
            ConvBlock(64, 64)
        )
        # Stage 2: 56x56 -> 28x28
        self.stage2 = nn.Sequential(
            ConvBlock(64, 128, stride=2),
            ConvBlock(128, 128)
        )
        # Stage 3: 28x28 -> 14x14
        self.stage3 = nn.Sequential(
            ConvBlock(128, 256, stride=2),
            ConvBlock(256, 256)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.stem(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        return x


class TransformerEncoderBlock(nn.Module):
    """Standard pre-LayerNorm Multi-Head Attention block with MLP."""

    def __init__(self, embed_dim: int = 256, num_heads: int = 8, mlp_ratio: float = 4.0, dropout: float = 0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(embed_dim)
        self.mha = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, dropout=dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(embed_dim)
        mlp_hidden = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden, embed_dim),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-LN Self-Attention
        norm_x = self.ln1(x)
        attn_out, _ = self.mha(norm_x, norm_x, norm_x)
        x = x + attn_out
        # Pre-LN Feed-Forward
        x = x + self.mlp(self.ln2(x))
        return x


class HybridSkinNet(nn.Module):
    """
    Hybrid CNN + Vision Transformer for Dermastack skin image analysis.
    
    Inputs:
        x: Tensor of shape (Batch, 3, 224, 224)
    Outputs:
        logits: Tensor of shape (Batch, num_classes)
    """

    def __init__(self, num_classes: int = NUM_CLASSES, embed_dim: int = 256, num_heads: int = 8, num_transformer_layers: int = 3):
        super().__init__()
        set_seed(42)
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.is_trained = False
        self.checkpoint_status = "missing_weights"
        self.checkpoint_metadata: Dict[str, Any] = {}

        # 1. Local feature extraction backbone
        self.cnn = CNNBackbone()
        # Target layer for Grad-CAM
        self.target_conv_layer = self.cnn.stage3

        # 2. Vision Transformer module
        # 14x14 feature map = 196 tokens
        self.num_tokens = 14 * 14
        self.pos_embedding = nn.Parameter(torch.randn(1, self.num_tokens, embed_dim) * 0.02)
        self.transformer_layers = nn.ModuleList([
            TransformerEncoderBlock(embed_dim=embed_dim, num_heads=num_heads)
            for _ in range(num_transformer_layers)
        ])
        self.transformer_ln = nn.LayerNorm(embed_dim)

        # 3. Global pooling & Hybrid Fusion
        self.cnn_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Concat: CNN pooled (256) + Transformer mean pooled (256) = 512
        fusion_dim = embed_dim + embed_dim
        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.BatchNorm1d(256),
            nn.SiLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward_features(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Extract CNN feature map and Transformer token representation."""
        # CNN: (B, 3, 224, 224) -> (B, 256, 14, 14)
        feat_map = self.cnn(x)

        # Local representation: (B, 256)
        cnn_rep = self.cnn_pool(feat_map).flatten(1)

        # Transformer representation:
        # Permute (B, C, H, W) -> (B, H*W, C)
        b, c, h, w = feat_map.shape
        tokens = feat_map.flatten(2).transpose(1, 2)  # (B, 196, 256)
        tokens = tokens + self.pos_embedding

        for layer in self.transformer_layers:
            tokens = layer(tokens)
        tokens = self.transformer_ln(tokens)

        # Global average over tokens: (B, 256)
        vit_rep = tokens.mean(dim=1)

        return cnn_rep, vit_rep

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        cnn_rep, vit_rep = self.forward_features(x)
        fused = torch.cat([cnn_rep, vit_rep], dim=1)  # (B, 512)
        logits = self.classifier(fused)
        return logits

    def load_weights(self, checkpoint_path: str, device: str = "cpu") -> Tuple[bool, str, str]:
        """
        Validate and load a trained PyTorch model checkpoint.
        
        Args:
            checkpoint_path: Path to .pt or .pth weights file.
            device: 'cpu' or 'cuda'.
            
        Returns:
            Tuple of (success: bool, diagnostic_code: str, status_message: str)
            Diagnostic codes: 'verified', 'missing_weights', 'incompatible_checkpoint'
        """
        if not os.path.isfile(checkpoint_path):
            self.is_trained = False
            self.checkpoint_status = "missing_weights"
            return False, "missing_weights", f"Checkpoint file not found at '{checkpoint_path}'. Trained weights are absent."

        try:
            checkpoint = torch.load(checkpoint_path, map_location=device)
            if not isinstance(checkpoint, dict):
                self.is_trained = False
                self.checkpoint_status = "incompatible_checkpoint"
                return False, "incompatible_checkpoint", "Invalid checkpoint format: expected dictionary containing state_dict."

            state_dict = checkpoint.get("state_dict", checkpoint)
            # Validate output class count compatibility
            if "classifier.4.weight" in state_dict:
                ckpt_classes = state_dict["classifier.4.weight"].shape[0]
                if ckpt_classes != self.num_classes:
                    self.is_trained = False
                    self.checkpoint_status = "incompatible_checkpoint"
                    return False, "incompatible_checkpoint", f"Class count mismatch: model has {self.num_classes} classes, checkpoint has {ckpt_classes}."

            self.load_state_dict(state_dict, strict=True)
            self.eval()
            self.is_trained = True
            self.checkpoint_status = "verified"
            self.checkpoint_metadata = {
                "source": checkpoint_path,
                "version": checkpoint.get("version", "unknown"),
                "trained_date": checkpoint.get("trained_date", "unknown"),
                "architecture": "HybridSkinNet"
            }
            return True, "verified", f"Successfully loaded and verified weights from {checkpoint_path}."
        except Exception as e:
            self.is_trained = False
            self.checkpoint_status = "incompatible_checkpoint"
            return False, "incompatible_checkpoint", f"Failed to load checkpoint: {str(e)}."
