"use client";

import React, { useState, useRef, useEffect } from "react";
import { UploadCloud, Image as ImageIcon, X, AlertCircle, Loader2, CheckCircle2, Sliders } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { AnalysisResponse } from "@/lib/types";

interface ImageUploadProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onError: (errorMsg: string) => void;
}

const MAX_FILE_SIZE_MB = 15;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export const ImageUpload: React.FC<ImageUploadProps> = ({ onAnalysisComplete, onError }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Optional contextual parameters
  const [ageRange, setAgeRange] = useState<string>("");
  const [skinType, setSkinType] = useState<string>("");
  const [concerns, setConcerns] = useState<string>("");
  const [consentToSave, setConsentToSave] = useState<boolean>(true);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Clean up preview object URL on unmount or file replacement
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const validateFile = (file: File): boolean => {
    setValidationError(null);

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setValidationError("Please select a valid image file (JPEG, PNG, or WEBP).");
      return false;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setValidationError(`File size (${(file.size / 1024 / 1024).toFixed(1)} MB) exceeds maximum allowed ${MAX_FILE_SIZE_MB} MB.`);
      return false;
    }

    return true;
  };

  const handleFileChange = (file: File) => {
    if (validateFile(file)) {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setValidationError(null);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleRemove = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setValidationError("Please select or drop an image first.");
      return;
    }

    setIsLoading(true);
    setValidationError(null);

    const formData = new FormData();
    formData.append("image", selectedFile);
    if (ageRange) formData.append("age_range", ageRange);
    if (skinType) formData.append("skin_type", skinType);
    if (concerns) formData.append("concerns", concerns);
    formData.append("consent_to_save", consentToSave ? "true" : "false");

    try {
      const result = await api.analyzeImage(formData);
      onAnalysisComplete(result);
    } catch (err: any) {
      const msg = err.message || "Failed to process skin image.";
      setValidationError(msg);
      onError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-stone-900 tracking-tight">
          Upload Skin Image
        </h2>
        <p className="text-xs sm:text-sm text-stone-500 mt-1">
          Provide a well-lit, macro photograph of the skin region or lesion for hybrid feature analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Upload Drop Zone / Preview */}
        {!previewUrl ? (
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? "border-sage-500 bg-sage-50/50"
                : "border-stone-300 hover:border-sage-400 bg-stone-50/50 hover:bg-stone-50"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
            />
            <div className="w-14 h-14 rounded-full bg-sage-100 text-sage-700 flex items-center justify-center mx-auto mb-3 shadow-sm">
              <UploadCloud className="w-7 h-7" />
            </div>
            <p className="text-sm font-medium text-stone-800">
              Drag &amp; drop your skin image here, or{" "}
              <span className="text-sage-600 hover:text-sage-700 underline font-semibold">browse files</span>
            </p>
            <p className="text-xs text-stone-500 mt-2">
              Supports JPEG, PNG, WEBP (Max {MAX_FILE_SIZE_MB}MB)
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 text-[11px] text-stone-500">
              <span className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200">
                Good natural lighting
              </span>
              <span className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200">
                Sharp focal focus
              </span>
              <span className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200">
                No filters or heavy makeup
              </span>
            </div>
          </div>
        ) : (
          <div className="relative rounded-xl border border-stone-200 overflow-hidden bg-stone-900/5 p-4 flex flex-col sm:flex-row items-center gap-6">
            <div className="relative w-48 h-48 rounded-lg overflow-hidden border border-stone-300 shadow-inner bg-white shrink-0">
              {/* Image Preview */}
              <img
                src={previewUrl}
                alt="Uploaded skin region preview"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1 space-y-2 text-left w-full">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-sage-700 bg-sage-100 px-2 py-0.5 rounded">
                  Image Ready
                </span>
                <button
                  type="button"
                  onClick={handleRemove}
                  className="p-1 rounded-lg hover:bg-stone-200 text-stone-500 hover:text-stone-800 transition"
                  title="Remove image"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm font-medium text-stone-800 truncate">
                {selectedFile?.name}
              </p>
              <p className="text-xs text-stone-500">
                Size: {((selectedFile?.size || 0) / 1024 / 1024).toFixed(2)} MB • {selectedFile?.type}
              </p>
              <div className="pt-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg border border-stone-300 bg-white hover:bg-stone-50 text-stone-700 transition"
                >
                  Replace File
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                />
              </div>
            </div>
          </div>
        )}

        {/* Validation Error Message */}
        {validationError && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{validationError}</span>
          </div>
        )}

        {/* Advanced / Optional Context Accordion */}
        <div className="border border-stone-200 rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-4 py-2.5 bg-stone-50/70 hover:bg-stone-100/70 flex items-center justify-between text-xs font-medium text-stone-700 transition"
          >
            <span className="flex items-center space-x-2">
              <Sliders className="w-3.5 h-3.5 text-stone-500" />
              <span>Optional Skin Context &amp; Patient Preferences</span>
            </span>
            <span className="text-stone-400 font-semibold">{showAdvanced ? "− Collapse" : "+ Expand"}</span>
          </button>

          {showAdvanced && (
            <div className="p-4 bg-white space-y-4 text-xs sm:text-sm border-t border-stone-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-stone-700 mb-1">
                    Age Bracket (Optional)
                  </label>
                  <select
                    value={ageRange}
                    onChange={(e) => setAgeRange(e.target.value)}
                    className="w-full px-3 py-2 border border-stone-300 rounded-lg text-xs bg-white text-stone-800 focus:ring-2 focus:ring-sage-400 focus:outline-none"
                  >
                    <option value="">Prefer not to say</option>
                    <option value="18-29">18 - 29 years</option>
                    <option value="30-45">30 - 45 years</option>
                    <option value="46-60">46 - 60 years</option>
                    <option value="60+">60+ years</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-stone-700 mb-1">
                    Skin Type (Optional)
                  </label>
                  <select
                    value={skinType}
                    onChange={(e) => setSkinType(e.target.value)}
                    className="w-full px-3 py-2 border border-stone-300 rounded-lg text-xs bg-white text-stone-800 focus:ring-2 focus:ring-sage-400 focus:outline-none"
                  >
                    <option value="">Unspecified</option>
                    <option value="Fitzpatrick I">Type I (Pale white skin, burns easily, rarely tans)</option>
                    <option value="Fitzpatrick II">Type II (Fair skin, burns easily, tans minimally)</option>
                    <option value="Fitzpatrick III">Type III (Medium white skin, gradual tan)</option>
                    <option value="Fitzpatrick IV">Type IV (Olive skin, rarely burns, tans easily)</option>
                    <option value="Fitzpatrick V">Type V (Brown skin, very rarely burns)</option>
                    <option value="Fitzpatrick VI">Type VI (Deeply pigmented dark brown/black skin)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-stone-700 mb-1">
                  Reported Symptoms or Concerns (Optional)
                </label>
                <input
                  type="text"
                  value={concerns}
                  onChange={(e) => setConcerns(e.target.value)}
                  placeholder="e.g. Itchiness, mild redness, dry borders, visible for 2 months"
                  className="w-full px-3 py-2 border border-stone-300 rounded-lg text-xs bg-white text-stone-800 placeholder-stone-400 focus:ring-2 focus:ring-sage-400 focus:outline-none"
                />
              </div>

              {/* Consent Toggle */}
              <div className="pt-2 flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="consent_save"
                  checked={consentToSave}
                  onChange={(e) => setConsentToSave(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-stone-300 text-sage-600 focus:ring-sage-400 cursor-pointer"
                />
                <label htmlFor="consent_save" className="text-xs text-stone-600 cursor-pointer select-none">
                  Consent to save anonymized report metadata in local persistence history. (Images themselves are processed in-memory and not stored to disk).
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <button
          type="submit"
          disabled={!selectedFile || isLoading}
          className={`w-full py-3 px-4 rounded-xl text-sm font-semibold transition-all shadow-sm flex items-center justify-center space-x-2 ${
            !selectedFile || isLoading
              ? "bg-stone-200 text-stone-400 cursor-not-allowed"
              : "bg-sage-600 hover:bg-sage-700 text-white shadow-sage-600/20 active:scale-[0.99]"
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Running Hybrid Feature Analysis...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4" />
              <span>Analyze Skin Features</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
