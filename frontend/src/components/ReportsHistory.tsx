"use client";

import React, { useState, useEffect } from "react";
import {
  History,
  RefreshCw,
  Eye,
  Calendar,
  AlertTriangle,
  Database,
  Loader2,
  FileText,
  X
} from "lucide-react";
import { api } from "@/lib/api";
import { ReportSummary, AnalysisResponse } from "@/lib/types";
import { AnalysisResults } from "./AnalysisResults";

interface ReportsHistoryProps {
  onSelectReport?: (report: AnalysisResponse) => void;
}

export const ReportsHistory: React.FC<ReportsHistoryProps> = ({ onSelectReport }) => {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<AnalysisResponse | null>(null);
  const [isFetchingDetail, setIsFetchingDetail] = useState<boolean>(false);

  const fetchReports = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await api.getReports(50);
      setReports(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to retrieve reports from server.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleViewDetail = async (reportId: string) => {
    setIsFetchingDetail(true);
    try {
      const detail = await api.getReportById(reportId);
      setSelectedReport(detail);
      if (onSelectReport) {
        onSelectReport(detail);
      }
    } catch (err: any) {
      alert(`Error loading report ${reportId}: ${err.message}`);
    } finally {
      setIsFetchingDetail(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Detail Modal View if opened */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 bg-stone-900/40 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-4 border border-stone-200">
            <div className="flex items-center justify-between pb-3 border-b border-stone-100">
              <h3 className="text-lg font-bold text-stone-900">
                Report Details ({selectedReport.report_id})
              </h3>
              <button
                onClick={() => setSelectedReport(null)}
                className="p-1 rounded-lg hover:bg-stone-100 text-stone-500 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <AnalysisResults result={selectedReport} onNewAnalysis={() => setSelectedReport(null)} />
          </div>
        </div>
      )}

      {/* Main Table Card */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-100">
          <div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-sage-100 text-sage-700 flex items-center justify-center">
                <History className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-semibold text-stone-900 tracking-tight">
                Analysis History &amp; Reports
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-stone-500 mt-1">
              Locally persisted skin assessments and educational records.
            </p>
          </div>

          <button
            onClick={fetchReports}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-stone-200 bg-stone-50 hover:bg-stone-100 text-stone-700 transition self-start"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{errorMsg}</span>
          </div>
        )}

        {isLoading ? (
          <div className="py-12 text-center text-stone-400 space-y-2">
            <Loader2 className="w-6 h-6 animate-spin mx-auto text-sage-600" />
            <p className="text-xs">Loading persisted reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="py-12 text-center text-stone-400 space-y-3 bg-stone-50/50 rounded-xl border border-dashed border-stone-200">
            <FileText className="w-8 h-8 mx-auto text-stone-300" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-stone-600">No reports found</p>
              <p className="text-xs text-stone-400 max-w-sm mx-auto">
                No skin analyses have been saved yet in this session or database. Run an analysis from the Skin Analysis tab to generate a record.
              </p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-600">
              <thead className="bg-stone-50/80 text-stone-500 uppercase tracking-wider font-semibold border-y border-stone-200/80">
                <tr>
                  <th className="py-3 px-4">Report ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Primary Category</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Mode</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {reports.map((r) => (
                  <tr key={r.report_id} className="hover:bg-stone-50/60 transition">
                    <td className="py-3 px-4 font-mono font-medium text-stone-800">
                      {r.report_id}
                    </td>
                    <td className="py-3 px-4 text-stone-500 whitespace-nowrap">
                      {new Date(r.created_at).toLocaleDateString()}{" "}
                      <span className="text-[10px] text-stone-400">
                        {new Date(r.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-stone-900">
                      <div className="flex items-center space-x-1.5">
                        <span>{r.predicted_name}</span>
                        {r.is_uncertain && (
                          <span className="text-[10px] text-amber-700 bg-amber-100 px-1.5 py-0.2 rounded font-semibold">
                            Uncertain
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-stone-700">
                      {(r.confidence_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                          r.inference_mode === "trained_inference"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {r.inference_mode}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleViewDetail(r.report_id)}
                        disabled={isFetchingDetail}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-sage-50 hover:bg-sage-100 text-sage-700 border border-sage-200 transition"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
