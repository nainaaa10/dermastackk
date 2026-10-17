# Dermastack Model Weights & Genuine Training Workflow

This directory is the designated location for verified PyTorch model weights (`best_hybrid_skin_model.pt`) for the Dermastack `HybridSkinNet` architecture.

---

> [!IMPORTANT]
> **Ethical & Scientific Clarification**:
> Defining the `HybridSkinNet` architecture in Python code does **NOT** train the model. Untrained neural network weights contain pseudo-random initialization parameters that output uncalibrated logits and nonsensical gradient heatmaps. Dermastack enforces an explicit **Simulated Demo Mode** until a verified, empirically trained checkpoint is supplied.
>
> Dermastack does **not** fabricate benchmark accuracy figures, dataset claims, or clinical validation metrics.

---

## 1. Diagnostic Status System

Dermastack's inference engine and Grad-CAM explainer report one of six explicit diagnostic states:

| Diagnostic Code | Meaning | System Action |
| :--- | :--- | :--- |
| `demo_mode_active` | `DEMO_MODE=true` is set in configuration. | Returns simulated illustrative results; suppresses Grad-CAM to prevent misleading visualizations. |
| `missing_weights` | `DEMO_MODE=false`, but no weights file exists at `MODEL_WEIGHTS_PATH`. | Gracefully falls back to demo mode; flags missing checkpoint path. |
| `incompatible_checkpoint` | File exists, but fails `state_dict` structure, key names, or `(7, 256)` classifier head shape. | Rejects checkpoint; falls back to demo mode with explicit error message. |
| `unsupported_gradcam_layer` | Target convolutional layer (`cnn.stage3`) is not found on model instance. | Model runs classification, but Grad-CAM is marked unavailable. |
| `inference_error` | Runtime error encountered during forward or backward gradient propagation. | Logs full traceback; returns error diagnostic code. |
| `generated` | Valid trained weights verified; forward & backward passes succeed. | Renders calibrated scores and blended Grad-CAM attention heatmap. |

---

## 2. Checkpoint Specification & Expected Format

When saving a trained model checkpoint for Dermastack, save it as a PyTorch dictionary (`.pt` or `.pth`) with the following structure:

```python
import torch

checkpoint = {
    "version": "v1.0.0",
    "architecture": "HybridSkinNet",
    "num_classes": 7,
    "trained_date": "2026-10-17T00:00:00Z",
    "state_dict": model.state_dict(),
    "class_names": [
        "Benign Keratosis-like Lesions",
        "Melanocytic Nevi (Common Moles)",
        "Dermatofibroma",
        "Vascular Lesions",
        "Acne / Inflammatory Comedones",
        "Eczematous / Atopic Dermatitis",
        "Unremarkable / Normal Skin Surface"
    ],
    "metrics": {
        "val_macro_f1": 0.0,    # Real measured validation metric
        "val_auroc": 0.0        # Real measured validation metric
    }
}

torch.save(checkpoint, "ml/weights/best_hybrid_skin_model.pt")
```

### Verification Checks Performed by the Loader:
1. **Dictionary Format**: File must be a Python dictionary containing `"state_dict"` or raw model state.
2. **Output Head Shape**: Layer `classifier.4.weight` must match exactly `torch.Size([7, 256])`.
3. **Layer Alignment**: CNN backbone (`cnn.stem`, `cnn.stage1`, `cnn.stage2`, `cnn.stage3`) and ViT layers (`transformer_layers`, `pos_embedding`) must match `HybridSkinNet` definitions.

---

## 3. End-to-End Workflow to Train a Genuine Model

To transition from Demo Mode to a genuinely trained machine learning system:

### Phase A: Dataset Acquisition & Ethical Balancing
1. **Dermoscopic & Clinical Datasets**:
   - Acquire de-identified dermatological research archives such as the **International Skin Imaging Collaboration (ISIC)** 2018/2019/2020 archives, the **BCN20000** dataset, and the **Fitzpatrick17k** dataset.
2. **Representation & Phototype Distribution**:
   - Ensure adequate representation across all Fitzpatrick skin phototypes (I through VI) to prevent demographic bias in lesion and erythematous border detection.
3. **Data Splits**:
   - Partition data into patient-independent train (70%), validation (15%), and test (15%) splits to avoid data leakage across multiple lesion crops from the same individual.

### Phase B: Preprocessing & Data Augmentation
- Target input resolution: $224 \times 224 \times 3$.
- Color space: RGB.
- Normalization: ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
- Augmentations during training: Random horizontal/vertical flip, color jitter (subtle hue $\pm 0.05$, saturation $\pm 0.1$, brightness $\pm 0.1$), affine rotation ($\pm 45^\circ$), and CutOut / Random Erasing.

### Phase C: Training Strategy
```python
# Illustrative training setup
import torch
import torch.nn as nn
from ml.model import HybridSkinNet

model = HybridSkinNet(num_classes=7)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)  # Or Focal Loss for imbalanced classes
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
```

### Phase D: Empirical Evaluation & Validation
- **Classification Metrics**: Measure multi-class AUROC, class-balanced accuracy, Cohen's Kappa, and per-class Sensitivity and Specificity.
- **Expected Calibration Error (ECE)**: Calibrate probabilities via Temperature Scaling so output scores reliably represent prediction probabilities.
- **Grad-CAM Pointing Game**: Validate that Grad-CAM attention maps align with dermatologist-annotated lesion masks (pointing game hit rate $\ge 85\%$).

### Phase E: Enabling Trained Inference in Dermastack
1. Place the verified checkpoint at `ml/weights/best_hybrid_skin_model.pt`.
2. Edit `backend/.env`:
   ```ini
   DEMO_MODE=false
   MODEL_WEIGHTS_PATH=ml/weights/best_hybrid_skin_model.pt
   ```
3. Restart the backend service:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Verify `/api/v1/health` reports `inference_mode: "trained_inference"` and `checkpoint_status: "verified"`.

---

## 4. Rejection & Uncertainty Policy

When trained weights are active, Dermastack applies a calibrated rejection policy:
- **Confidence Floor**: If the top predicted class probability is $< 0.50$ (50%), the result is marked `is_uncertain: true` with a clear explanation.
- **Shannon Entropy Ceiling**: If output distribution entropy exceeds $1.35\text{ nats}$, the prediction is marked ambiguous.
- Inconclusive results prevent over-confident misclassification of ambiguous or out-of-distribution skin presentations.
