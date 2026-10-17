"use client";

import React, { useState } from "react";
import {
  FlaskConical,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Loader2,
  ShieldAlert,
  BookOpen,
  Sparkles,
  Tag
} from "lucide-react";
import { api } from "@/lib/api";
import { IngredientCheckResponse } from "@/lib/types";

const SAMPLE_FORMULAS = [
  {
    name: "Barrier Repair Cream",
    concerns: ["dryness", "barrier_damage"],
    sensitivities: [],
    text: "Water (Aqua), Glycerin, Ceramides (NP, AP, EOP), Squalane, Hyaluronic Acid, Centella Asiatica Extract, Allantoin, Phenoxyethanol, Ethylhexylglycerin"
  },
  {
    name: "Active Exfoliating Toner",
    concerns: ["acne"],
    sensitivities: ["fragrance"],
    text: "Water, Salicylic Acid (BHA), Glycolic Acid (AHA), Niacinamide 5%, Alcohol Denat, Fragrance / Parfum, Linalool, Polysorbate 20"
  },
  {
    name: "Soothing Mineral Sunscreen",
    concerns: ["sensitive", "rosacea"],
    sensitivities: [],
    text: "Zinc Oxide 15%, Titanium Dioxide 5%, Water, Jojoba Oil, Colloidal Oatmeal, Panthenol, Tocopherol, UnknownBotanicalExtract"
  }
];

export const IngredientChecker: React.FC = () => {
  const [ingredientText, setIngredientText] = useState<string>("");
  const [concernsText, setConcernsText] = useState<string>("");
  const [sensitivitiesText, setSensitivitiesText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<IngredientCheckResponse | null>(null);

  const handleSampleClick = (sample: typeof SAMPLE_FORMULAS[0]) => {
    setIngredientText(sample.text);
    setConcernsText(sample.concerns.join(", "));
    setSensitivitiesText(sample.sensitivities.join(", "));
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingredientText.trim()) {
      setErrorMsg("Please paste or type an ingredient list first.");
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);

    const skinConcerns = concernsText
      .split(/[,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);

    const knownSensitivities = sensitivitiesText
      .split(/[,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      const response = await api.checkIngredients(ingredientText, skinConcerns, knownSensitivities);
      setResult(response);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to analyze ingredient deck.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Form Card */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-6">
        <div>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-lavender-100 text-lavender-700 flex items-center justify-center">
              <FlaskConical className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-semibold text-stone-900 tracking-tight">
              Cosmetic Ingredient Formulation Checker
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-stone-500 mt-1">
            Parse INCI ingredient lists, evaluate documented scientific functions, comedogenic/irritancy profiles, and flag potential allergens.
          </p>
        </div>

        {/* Quick Sample Presets */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs font-medium text-stone-400">Try quick sample:</span>
          {SAMPLE_FORMULAS.map((sample) => (
            <button
              key={sample.name}
              type="button"
              onClick={() => handleSampleClick(sample)}
              className="px-2.5 py-1 text-xs font-medium rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 transition"
            >
              {sample.name}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-stone-700 mb-1">
              Ingredient List (INCI text from packaging)
            </label>
            <textarea
              rows={5}
              value={ingredientText}
              onChange={(e) => setIngredientText(e.target.value)}
              placeholder="e.g. Water, Glycerin, Niacinamide, Salicylic Acid, Ceramides NP, Fragrance, Phenoxyethanol..."
              className="w-full p-3 border border-stone-300 rounded-xl text-xs sm:text-sm bg-white text-stone-800 placeholder-stone-400 focus:ring-2 focus:ring-lavender-400 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-stone-700 mb-1">
                Your Skin Concerns (comma-separated, optional)
              </label>
              <input
                type="text"
                value={concernsText}
                onChange={(e) => setConcernsText(e.target.value)}
                placeholder="e.g. acne, rosacea, sensitive, dryness"
                className="w-full px-3 py-2 border border-stone-300 rounded-lg text-xs bg-white text-stone-800 placeholder-stone-400 focus:ring-2 focus:ring-lavender-400 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-stone-700 mb-1">
                Known Sensitivities or Allergies (optional)
              </label>
              <input
                type="text"
                value={sensitivitiesText}
                onChange={(e) => setSensitivitiesText(e.target.value)}
                placeholder="e.g. fragrance, linalool, sulfates, aspirin"
                className="w-full px-3 py-2 border border-stone-300 rounded-lg text-xs bg-white text-stone-800 placeholder-stone-400 focus:ring-2 focus:ring-lavender-400 focus:outline-none"
              />
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
              <span>{errorMsg}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !ingredientText.trim()}
            className={`w-full py-3 px-4 rounded-xl text-sm font-semibold transition-all shadow-sm flex items-center justify-center space-x-2 ${
              isLoading || !ingredientText.trim()
                ? "bg-stone-200 text-stone-400 cursor-not-allowed"
                : "bg-lavender-600 hover:bg-lavender-700 text-white shadow-lavender-600/20 active:scale-[0.99]"
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Cross-Referencing Scientific Literature...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Evaluate Formulation</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Analysis Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Summary Overview Card */}
          <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-stone-100 gap-4">
              <div>
                <h3 className="text-base font-semibold text-stone-900 tracking-tight">
                  Formulation Breakdown
                </h3>
                <p className="text-xs text-stone-500 mt-0.5">
                  Parsed {result.total_parsed} tokens • {result.total_identified} cataloged • {result.total_unknown} unindexed
                </p>
              </div>

              {/* Status Metric Pills */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium">
                  {result.total_identified} Identified
                </span>
                {result.total_unknown > 0 && (
                  <span className="px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-medium">
                    {result.total_unknown} Unknown
                  </span>
                )}
              </div>
            </div>

            {/* Overview Explanation */}
            <p className="text-xs sm:text-sm text-stone-600 leading-relaxed bg-stone-50 p-4 rounded-xl border border-stone-200/60">
              {result.educational_overview}
            </p>

            {/* Potential Alerts/Flags */}
            {result.potential_flags.length > 0 && (
              <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 space-y-2">
                <div className="flex items-center space-x-2 text-amber-900 font-semibold text-xs sm:text-sm">
                  <ShieldAlert className="w-4 h-4 text-amber-700" />
                  <span>Personalized Formulation Alerts</span>
                </div>
                <ul className="space-y-1 text-xs text-amber-800 list-disc list-inside">
                  {result.potential_flags.map((flag, idx) => (
                    <li key={idx} className="leading-relaxed">
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Detailed Ingredients Table / Cards */}
          <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-4">
            <h3 className="text-base font-semibold text-stone-900 tracking-tight">
              Ingredient Profiles &amp; Evidence
            </h3>

            <div className="space-y-3 pt-1">
              {result.ingredients.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all ${
                    item.is_known
                      ? "border-stone-200 bg-white hover:border-stone-300"
                      : "border-dashed border-stone-300 bg-stone-50/50"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs sm:text-sm font-bold text-stone-900">
                        {item.matched_name}
                      </span>
                      {item.matched_name.toLowerCase() !== item.query_name.toLowerCase() && (
                        <span className="text-[11px] text-stone-400 italic">
                          (as "{item.query_name}")
                        </span>
                      )}
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          item.evidence_level === "High"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : item.evidence_level === "Moderate"
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "bg-stone-100 text-stone-600 border border-stone-200"
                        }`}
                      >
                        Evidence: {item.evidence_level}
                      </span>
                    </div>

                    {/* Ratings */}
                    {item.is_known && (
                      <div className="flex items-center space-x-3 text-xs text-stone-500 font-mono">
                        {item.comedogenic_rating !== null && (
                          <span
                            className={`px-2 py-0.5 rounded ${
                              item.comedogenic_rating >= 3
                                ? "bg-amber-100 text-amber-800 font-bold"
                                : "bg-stone-100 text-stone-700"
                            }`}
                          >
                            Comedogenicity: {item.comedogenic_rating}/5
                          </span>
                        )}
                        {item.irritancy_rating !== null && (
                          <span
                            className={`px-2 py-0.5 rounded ${
                              item.irritancy_rating >= 3
                                ? "bg-rose-100 text-rose-800 font-bold"
                                : "bg-stone-100 text-stone-700"
                            }`}
                          >
                            Irritancy: {item.irritancy_rating}/5
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Functions Tags */}
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {item.functions.map((func, fIdx) => (
                      <span
                        key={fIdx}
                        className="px-2 py-0.5 text-[10px] font-medium rounded-md bg-stone-100 text-stone-700 border border-stone-200"
                      >
                        {func}
                      </span>
                    ))}
                  </div>

                  {/* Safety Profile */}
                  <p className="text-xs text-stone-600 leading-relaxed mb-2">
                    {item.safety_profile}
                  </p>

                  {/* Cautions */}
                  {item.cautions && (
                    <div className="p-2.5 rounded-lg bg-amber-50/60 border border-amber-200/60 text-[11px] text-amber-800 leading-relaxed mb-2">
                      <strong>Caution:</strong> {item.cautions}
                    </div>
                  )}

                  {/* Sources */}
                  {item.sources && item.sources.length > 0 && (
                    <div className="flex items-center space-x-1 text-[10px] text-stone-400">
                      <BookOpen className="w-3 h-3 text-stone-400 shrink-0" />
                      <span>Sources: {item.sources.join(" • ")}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Medical Disclaimer */}
          <div className="p-4 rounded-xl bg-stone-100 border border-stone-200 text-xs text-stone-600 flex items-start space-x-3">
            <BookOpen className="w-4 h-4 text-stone-400 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              {result.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
