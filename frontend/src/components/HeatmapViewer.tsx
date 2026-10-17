"use client";

import React, { useState } from "react";
import { Eye, EyeOff, Layers, Info, AlertTriangle } from "lucide-react";

interface HeatmapViewerProps {
  originalImagePreviewUrl?: string | null;
  heatmapDataUri?: string | null;
  status: string;
  explanation?: string | null;
}

export const HeatmapViewer: React.FC<HeatmapViewerProps> = ({
  originalImagePreviewUrl,
  heatmapDataUri,
  status,
  explanation
}) => {
  const [viewMode, setViewMode] = useState<"side_by_side" | "slider" | "overlay">("side_by_side");
  const [sliderPosition, setSliderPosition] = useState<number>(50);

  const hasHeatmap = status === "generated" && !!heatmapDataUri;

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-semibold text-stone-900 tracking-tight">
              Grad-CAM Visual Explainability
            </h3>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                hasHeatmap
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                  : "bg-amber-100 text-amber-800 border border-amber-200"
              }`}
            >
              {hasHeatmap ? "Heatmap Active" : "Unavailable in Demo"}
            </span>
          </div>
          <p className="text-xs text-stone-500 mt-1">
            Gradient-weighted Class Activation Mapping of convolutional feature activations.
          </p>
        </div>

        {/* View Mode Switcher (if heatmap is available) */}
        {hasHeatmap && (
          <div className="flex items-center bg-stone-100 p-1 rounded-lg text-xs self-start">
            <button
              onClick={() => setViewMode("side_by_side")}
              className={`px-3 py-1 rounded-md font-medium transition ${
                viewMode === "side_by_side" ? "bg-white text-stone-900 shadow-xs" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Side by Side
            </button>
            <button
              onClick={() => setViewMode("slider")}
              className={`px-3 py-1 rounded-md font-medium transition ${
                viewMode === "slider" ? "bg-white text-stone-900 shadow-xs" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Comparison Slider
            </button>
          </div>
        )}
      </div>

      {/* Main Visual Display */}
      {hasHeatmap && heatmapDataUri ? (
        <div className="space-y-4">
          {viewMode === "side_by_side" ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Original Aligned Image */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-medium text-stone-600">
                  <span>Input Field of View (224×224)</span>
                  <span className="text-stone-400">Baseline</span>
                </div>
                <div className="aspect-square w-full rounded-xl overflow-hidden border border-stone-200 bg-stone-50 flex items-center justify-center">
                  {originalImagePreviewUrl ? (
                    <img
                      src={originalImagePreviewUrl}
                      alt="Original skin field"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-xs text-stone-400">Original not cached</div>
                  )}
                </div>
              </div>

              {/* Heatmap Overlay */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-medium text-stone-600">
                  <span>Grad-CAM Activation Blend</span>
                  <span className="text-sage-600 font-semibold">Trained CNN Output</span>
                </div>
                <div className="aspect-square w-full rounded-xl overflow-hidden border border-stone-200 bg-stone-50 flex items-center justify-center shadow-inner">
                  <img
                    src={heatmapDataUri}
                    alt="Grad-CAM activation overlay"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>
          ) : (
            /* Interactive Comparison Slider */
            <div className="space-y-2">
              <div className="relative aspect-square max-w-md mx-auto rounded-xl overflow-hidden border border-stone-200 select-none shadow-sm">
                {/* Heatmap Layer (Underneath or right) */}
                <img
                  src={heatmapDataUri}
                  alt="Heatmap"
                  className="absolute inset-0 w-full h-full object-cover"
                />

                {/* Original Image Layer (Clipped by slider position) */}
                {originalImagePreviewUrl && (
                  <div
                    className="absolute inset-0 overflow-hidden"
                    style={{ width: `${sliderPosition}%` }}
                  >
                    <img
                      src={originalImagePreviewUrl}
                      alt="Original"
                      className="absolute inset-0 w-full h-full object-cover max-w-none"
                      style={{ width: "100%", height: "100%" }}
                    />
                  </div>
                )}

                {/* Divider Line */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-white shadow-md cursor-ew-resize"
                  style={{ left: `${sliderPosition}%` }}
                >
                  <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 rounded-full bg-white text-stone-700 shadow-md flex items-center justify-center text-[10px] font-bold border border-stone-200">
                    ⇄
                  </div>
                </div>
              </div>

              {/* Slider Controller */}
              <div className="max-w-md mx-auto pt-2 flex items-center space-x-3 text-xs text-stone-500">
                <span>Original</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={sliderPosition}
                  onChange={(e) => setSliderPosition(Number(e.target.value))}
                  className="w-full h-1.5 bg-stone-200 rounded-lg appearance-none cursor-pointer accent-sage-600"
                />
                <span>Heatmap</span>
              </div>
            </div>
          )}

          {/* Colormap Legend */}
          <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 text-xs space-y-2">
            <div className="flex items-center justify-between text-stone-600 font-medium">
              <span>Attention Gradient Scale:</span>
              <div className="flex items-center space-x-2">
                <span>Minimal Influence</span>
                <div className="w-32 h-2.5 rounded bg-gradient-to-r from-blue-600 via-yellow-400 to-red-600 border border-stone-300" />
                <span>Peak Weight</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Explicit Unavailable / Demo State */
        <div className="p-6 rounded-xl bg-stone-50 border border-dashed border-stone-300 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center mx-auto">
            <Layers className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h4 className="text-sm font-semibold text-stone-800">
              Grad-CAM Visualization Disabled in Demo Mode
            </h4>
            <p className="text-xs text-stone-500 leading-relaxed">
              {explanation ||
                "Grad-CAM requires explicitly loaded, trained model weights. When running in simulated demo mode or with untrained weights, feature gradients are random and medically misleading."}
            </p>
          </div>
          <div className="text-[11px] text-stone-400 pt-2">
            To enable visual heatmaps, load a compatible checkpoint into <code>ml/weights/best_hybrid_skin_model.pt</code>.
          </div>
        </div>
      )}

      {/* Educational Notice on Grad-CAM */}
      <div className="flex items-start space-x-2 text-xs text-stone-500 bg-stone-50/80 p-3 rounded-lg border border-stone-200/60">
        <Info className="w-4 h-4 text-stone-400 shrink-0 mt-0.5" />
        <p>
          <strong>Scientific Interpretation:</strong> Grad-CAM highlights which spatial receptive fields in the image exerted the highest numerical influence on the model’s classification logits. It does <em>not</em> prove pathology or define anatomical boundaries of diseased tissue.
        </p>
      </div>
    </div>
  );
};
