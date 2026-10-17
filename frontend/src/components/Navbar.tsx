"use client";

import React from "react";
import { Sparkles, Database, Cpu, AlertCircle } from "lucide-react";
import { HealthResponse } from "@/lib/types";

interface NavbarProps {
  health: HealthResponse | null;
  activeTab: "analyze" | "ingredients" | "reports";
  onTabChange: (tab: "analyze" | "ingredients" | "reports") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, activeTab, onTabChange }) => {
  const isDemo = health?.inference_mode === "demo_simulated" || health?.demo_mode;
  const isDbConnected = health?.database_connected;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-stone-200/80 bg-white/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onTabChange("analyze")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sage-600 to-sage-400 flex items-center justify-center text-white shadow-sm shadow-sage-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-semibold tracking-tight text-stone-900 font-sans">
                Dermastack
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-sage-100 text-sage-800 border border-sage-200">
                AI Skin Lab
              </span>
            </div>
            <p className="text-xs text-stone-500 hidden sm:block">
              Hybrid Vision &amp; Ingredient Intelligence
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2 bg-stone-100/80 p-1 rounded-xl border border-stone-200/60">
          <button
            onClick={() => onTabChange("analyze")}
            className={`px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "analyze"
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-600 hover:text-stone-900 hover:bg-stone-200/50"
            }`}
          >
            Skin Analysis
          </button>
          <button
            onClick={() => onTabChange("ingredients")}
            className={`px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "ingredients"
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-600 hover:text-stone-900 hover:bg-stone-200/50"
            }`}
          >
            Ingredient Checker
          </button>
          <button
            onClick={() => onTabChange("reports")}
            className={`px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
              activeTab === "reports"
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-600 hover:text-stone-900 hover:bg-stone-200/50"
            }`}
          >
            Reports &amp; History
          </button>
        </nav>

        {/* System Status Indicators */}
        <div className="hidden lg:flex items-center space-x-3 text-xs">
          {/* Inference Mode Pill */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border font-medium ${
              isDemo
                ? "bg-amber-50 text-amber-800 border-amber-200"
                : "bg-emerald-50 text-emerald-800 border-emerald-200"
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>{isDemo ? "Simulated Demo Mode" : "Trained Model Active"}</span>
          </div>

          {/* Database Status Pill */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border font-medium ${
              isDbConnected
                ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                : "bg-stone-100 text-stone-700 border-stone-200"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>{isDbConnected ? "MongoDB Connected" : "Local Demo Persistence"}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
