"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
import { ImageUpload } from "./ImageUpload";
import { AnalysisResults } from "./AnalysisResults";
import { HeatmapViewer } from "./HeatmapViewer";
import { IngredientChecker } from "./IngredientChecker";
import { ReportsHistory } from "./ReportsHistory";
import { api } from "@/lib/api";
import { HealthResponse, AnalysisResponse } from "@/lib/types";
import { Sparkles, Shield, Cpu, RefreshCw, AlertCircle } from "lucide-react";

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"analyze" | "ingredients" | "reports">("analyze");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [currentPreviewUrl, setCurrentPreviewUrl] = useState<string | null>(null);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setHealthLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
      setGlobalError(null);
    } catch (err: any) {
      setGlobalError(err.message);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleAnalysisComplete = (result: AnalysisResponse) => {
    setCurrentAnalysis(result);
  };

  const handleNewAnalysis = () => {
    setCurrentAnalysis(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-stone-50 font-sans text-stone-900 antialiased selection:bg-sage-200 selection:text-sage-900">
      {/* Sticky Header */}
      <Navbar health={health} activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Global Connection Warning if Backend is Offline */}
      {globalError && (
        <div className="bg-rose-500 text-white px-4 py-2.5 text-xs sm:text-sm font-medium flex items-center justify-between shadow-sm">
          <div className="max-w-7xl mx-auto flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{globalError}</span>
          </div>
          <button
            onClick={fetchHealth}
            className="px-2 py-0.5 rounded bg-white/20 hover:bg-white/30 text-white text-xs font-semibold"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <section className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sage-100 text-sage-800 text-xs font-semibold border border-sage-200">
            <Sparkles className="w-3.5 h-3.5 text-sage-600" />
            <span>AI Skincare &amp; Dermatological Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-stone-900 font-sans">
            Evidence-Based Skin Feature Analysis &amp; Formulation Science
          </h1>
          <p className="text-stone-600 text-sm sm:text-base max-w-3xl leading-relaxed">
            Dermastack pairs experimental Hybrid CNN + Vision Transformer image representations with cosmetic science literature to demystify skin patterns and ingredient formulations.
          </p>
        </section>

        {/* Tab 1: Skin Analysis */}
        {activeTab === "analyze" && (
          <div className="space-y-8">
            {!currentAnalysis ? (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <div className="lg:col-span-7">
                  <ImageUpload
                    onAnalysisComplete={handleAnalysisComplete}
                    onError={(err) => setGlobalError(err)}
                  />
                </div>

                {/* Educational & Architectural Sidebar */}
                <div className="lg:col-span-5 space-y-6">
                  <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-4">
                    <h3 className="text-sm font-bold text-stone-900 uppercase tracking-wider text-sage-700">
                      Hybrid Architecture Highlights
                    </h3>
                    <div className="space-y-3 text-xs text-stone-600 leading-relaxed">
                      <div className="flex items-start space-x-2.5">
                        <div className="w-5 h-5 rounded-full bg-sage-100 text-sage-700 flex items-center justify-center shrink-0 mt-0.5 font-bold text-[10px]">
                          1
                        </div>
                        <p>
                          <strong>Multi-Stage CNN:</strong> Captures high-frequency micro-textures, pigment borders, and localized lesion contours.
                        </p>
                      </div>
                      <div className="flex items-start space-x-2.5">
                        <div className="w-5 h-5 rounded-full bg-sage-100 text-sage-700 flex items-center justify-center shrink-0 mt-0.5 font-bold text-[10px]">
                          2
                        </div>
                        <p>
                          <strong>Vision Transformer (ViT):</strong> Multi-head self-attention projects spatial patches to capture global contextual patterns.
                        </p>
                      </div>
                      <div className="flex items-start space-x-2.5">
                        <div className="w-5 h-5 rounded-full bg-sage-100 text-sage-700 flex items-center justify-center shrink-0 mt-0.5 font-bold text-[10px]">
                          3
                        </div>
                        <p>
                          <strong>Rejection Thresholds:</strong> Low-confidence scores (&lt;50%) or high-entropy distributions are automatically flagged as uncertain.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-sage-50/60 rounded-2xl border border-sage-200/70 p-5 text-xs text-sage-900 space-y-2">
                    <p className="font-semibold flex items-center space-x-1.5">
                      <Shield className="w-4 h-4 text-sage-700" />
                      <span>Privacy &amp; Local Execution Guarantee</span>
                    </p>
                    <p className="text-sage-800 leading-relaxed">
                      Images submitted to Dermastack are processed strictly in RAM and are not committed to disk or cloud servers without your explicit consent.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              /* Analysis Results View */
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <div className="lg:col-span-7">
                  <AnalysisResults
                    result={currentAnalysis}
                    onNewAnalysis={handleNewAnalysis}
                  />
                </div>
                <div className="lg:col-span-5">
                  <HeatmapViewer
                    originalImagePreviewUrl={currentPreviewUrl}
                    heatmapDataUri={currentAnalysis.gradcam_heatmap}
                    status={currentAnalysis.gradcam_status}
                    explanation={currentAnalysis.gradcam_explanation}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Ingredient Formulation Checker */}
        {activeTab === "ingredients" && (
          <div>
            <IngredientChecker />
          </div>
        )}

        {/* Tab 3: Reports & Analysis History */}
        {activeTab === "reports" && (
          <div>
            <ReportsHistory
              onSelectReport={(report) => {
                setCurrentAnalysis(report);
                setActiveTab("analyze");
              }}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};
