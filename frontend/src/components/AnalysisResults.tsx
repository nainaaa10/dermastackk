"use client";

import React from "react";
import {
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  ShieldCheck,
  Sparkles,
  Info,
  Calendar,
  Layers,
  Database
} from "lucide-react";
import { AnalysisResponse } from "@/lib/types";

interface AnalysisResultsProps {
  result: AnalysisResponse;
  onNewAnalysis: () => void;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result, onNewAnalysis }) => {
  const isDemo = result.inference_mode === "demo_simulated";
  const confidencePercent = (result.confidence_score * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Top Banner: Mode & Uncertainty Alert */}
      {isDemo && (
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs sm:text-sm flex items-start space-x-3 shadow-xs">
          <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-amber-900">
              Simulated Demo Mode Notice
            </p>
            <p className="text-amber-800 leading-relaxed">
              These results are synthetic illustrative outputs generated for interface testing without requiring deep learning weights. They do <strong>not</strong> represent a real diagnostic assessment of the uploaded skin.
            </p>
          </div>
        </div>
      )}

      {result.is_uncertain && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs sm:text-sm flex items-start space-x-3 shadow-xs">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-900">
              Inconclusive / High-Uncertainty Assessment
            </p>
            <p className="text-rose-800 leading-relaxed">
              {result.uncertainty_reason ||
                "The model’s confidence did not meet the documented threshold (50.0%) for reliable separation. In clinical dermatology, visual ambiguity warrants professional dermoscopy."}
            </p>
          </div>
        </div>
      )}

      {/* Primary Result Summary Card */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-stone-100 gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs text-stone-500 mb-1">
              <span className="font-mono text-stone-400">ID: {result.report_id}</span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{new Date(result.created_at).toLocaleString()}</span>
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">
              {result.predicted_name}
            </h2>
            <p className="text-xs sm:text-sm text-stone-500 mt-1">
              Model Version: {result.model_version} • Mode: {result.inference_mode}
            </p>
          </div>

          {/* Confidence Score Pill */}
          <div className="flex flex-col items-end">
            <span className="text-xs text-stone-500 mb-1 font-medium">Confidence Score</span>
            <div className="flex items-baseline space-x-1">
              <span className="text-3xl font-extrabold text-stone-900 font-mono tracking-tight">
                {confidencePercent}
              </span>
              <span className="text-sm font-semibold text-stone-500">%</span>
            </div>
            <div className="w-36 h-2 rounded-full bg-stone-100 mt-2 overflow-hidden border border-stone-200">
              <div
                className={`h-full transition-all duration-500 ${
                  result.confidence_score > 0.65
                    ? "bg-sage-600"
                    : result.confidence_score > 0.40
                    ? "bg-amber-500"
                    : "bg-rose-500"
                }`}
                style={{ width: `${Math.min(result.confidence_score * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Educational Summary Block */}
        <div className="p-4 rounded-xl bg-stone-50 border border-stone-200/80 space-y-2 text-xs sm:text-sm">
          <div className="flex items-center space-x-2 text-stone-700 font-semibold">
            <Sparkles className="w-4 h-4 text-sage-600" />
            <span>Educational Guidance</span>
          </div>
          <p className="text-stone-600 leading-relaxed">
            {result.educational_summary}
          </p>
        </div>

        {/* Persistence Status */}
        <div className="flex items-center justify-between text-xs text-stone-500 pt-2 border-t border-stone-100">
          <div className="flex items-center space-x-2">
            <Database className="w-3.5 h-3.5 text-stone-400" />
            <span>
              {result.is_persisted
                ? `Saved to ${result.persistence_storage === "mongodb" ? "MongoDB Atlas/Local" : "Local Demo Session"}`
                : "Not persisted (consent omitted)"}
            </span>
          </div>
          <button
            onClick={onNewAnalysis}
            className="text-xs font-semibold text-sage-600 hover:text-sage-700 underline"
          >
            Upload Another Image
          </button>
        </div>
      </div>

      {/* Candidate Score Distribution Table */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-semibold text-stone-900 tracking-tight">
          Candidate Class Probabilities
        </h3>
        <p className="text-xs text-stone-500">
          Relative probability distribution across all 7 indexed dermatological feature classes.
        </p>

        <div className="space-y-3 pt-2">
          {result.predictions.map((pred, idx) => {
            const pct = (pred.score * 100).toFixed(1);
            const isTop = idx === 0;

            return (
              <div
                key={pred.class_id}
                className={`p-3 rounded-xl border transition-all ${
                  isTop
                    ? "border-sage-300 bg-sage-50/40"
                    : "border-stone-200 hover:border-stone-300 bg-stone-50/20"
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        isTop ? "bg-sage-600 text-white" : "bg-stone-200 text-stone-700"
                      }`}
                    >
                      {idx + 1}
                    </span>
                    <span className="text-xs sm:text-sm font-semibold text-stone-800">
                      {pred.name}
                    </span>
                    <span className="text-[10px] text-stone-400 font-mono px-1.5 py-0.5 rounded bg-stone-100">
                      {pred.category}
                    </span>
                  </div>
                  <div className="font-mono text-xs font-bold text-stone-800">
                    {pct}%
                  </div>
                </div>

                <div className="w-full h-1.5 rounded-full bg-stone-200/80 overflow-hidden mb-2">
                  <div
                    className={`h-full ${isTop ? "bg-sage-600" : "bg-stone-400"}`}
                    style={{ width: `${pred.score * 100}%` }}
                  />
                </div>

                <p className="text-[11px] text-stone-500 leading-tight">
                  {pred.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Medical Safety Disclaimer */}
      <div className="p-4 rounded-xl bg-stone-100 border border-stone-200 text-xs text-stone-600 flex items-start space-x-3">
        <ShieldCheck className="w-4 h-4 text-stone-500 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          {result.disclaimer}
        </p>
      </div>
    </div>
  );
};
