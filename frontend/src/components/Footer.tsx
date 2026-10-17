"use client";

import React from "react";
import { ShieldAlert, BookOpen, Lock } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-stone-200 bg-stone-50/80 py-8 px-4 sm:px-6 lg:px-8 text-stone-600">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Medical Safety & Privacy Notice */}
        <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200/80 flex items-start space-x-3 text-xs sm:text-sm text-amber-900 leading-relaxed">
          <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-amber-900">
              Important Medical &amp; Clinical Disclaimers
            </p>
            <p>
              Dermastack is strictly an educational research platform and experimental software demonstration. It does <strong>not</strong> provide medical diagnoses, treatment prescriptions, or definitive clinical assessments. Skin lesions, persistent rashes, bleeding nodules, or changing pigmented marks must always be evaluated in person by a qualified board-certified dermatologist.
            </p>
          </div>
        </div>

        {/* Footer Links & Info */}
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-stone-500 gap-4 pt-2">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <Lock className="w-3.5 h-3.5 text-stone-400" />
              <span>Privacy First: Images are processed in-memory and not stored by default</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <BookOpen className="w-3.5 h-3.5 text-stone-400" />
              <span>Literature-Backed Dermatological Reference</span>
            </span>
          </div>

          <div className="text-right">
            Dermastack v1.0.0 • Local Developer Environment
          </div>
        </div>
      </div>
    </footer>
  );
};
