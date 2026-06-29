"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  GitCompare, Upload, AlertTriangle, CheckCircle2, TrendingUp, FileText,
  ArrowRight, Download, ChevronDown, AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import { CompareResponse } from "@/lib/types";

const DEMO_COMPARE: CompareResponse = {
  summary:
    "The 2026 policy revision introduces significant changes to prior authorization requirements for imaging and mental health services. Commercial plan members will face stricter documentation requirements. Effective date moved from January 2025 to January 2026.",
  total_changes: 8,
  high_risk_count: 3,
  old_doc_name: "Policy_2025.pdf",
  new_doc_name: "Policy_2026.pdf",
  changes: [
    { area: "MRI Authorization",       old_value: "Not required for commercial plans",      new_value: "Required — 72 hours prior submission",         impact: "Higher review risk and workflow overhead",              risk_level: "high",   change_type: "Authorization" },
    { area: "Effective Date",           old_value: "January 1, 2025",                        new_value: "January 1, 2026",                              impact: "Policy update — all rules apply from new date",        risk_level: "low",    change_type: "Administrative" },
    { area: "CPT 99213 Documentation", old_value: "Standard office visit — allowed",        new_value: "Requires medical necessity documentation",      impact: "Documentation burden increases for providers",          risk_level: "medium", change_type: "Billing" },
    { area: "Telehealth Coverage",      old_value: "Commercial only",                        new_value: "Commercial + Medicare Advantage",               impact: "Coverage expansion — reduced denials",                  risk_level: "low",    change_type: "Coverage" },
    { area: "Mental Health Parity",     old_value: "12 sessions per year",                   new_value: "Unlimited sessions with ongoing authorization", impact: "Significant utilization management change",             risk_level: "high",   change_type: "Authorization" },
    { area: "Step Therapy Protocol",    old_value: "Not required",                            new_value: "Required for specialty biologics",              impact: "Claims denial risk for biologics without step therapy", risk_level: "high",   change_type: "Authorization" },
    { area: "Lab Panel Coverage",       old_value: "CPT 80053 fully covered",                new_value: "CPT 80053 requires medical necessity",          impact: "Increased documentation for routine labs",              risk_level: "medium", change_type: "Billing" },
    { area: "Emergency Authorization",  old_value: "48 hours post-service",                  new_value: "24 hours post-service",                         impact: "Tighter window increases administrative risk",           risk_level: "medium", change_type: "Authorization" },
  ],
};

const CHANGE_TYPE_COLORS: Record<string, string> = {
  Authorization:  "bg-red-500/10 text-red-400 border-red-500/18",
  Billing:        "bg-amber-500/10 text-amber-400 border-amber-500/18",
  Coverage:       "bg-emerald-500/10 text-emerald-400 border-emerald-500/18",
  Administrative: "bg-slate-500/10 text-slate-400 border-slate-500/18",
};

const RISK_CONFIG = {
  high:   { label: "High Impact",   color: "#f87171", bg: "rgba(248,113,113,0.06)",  border: "rgba(248,113,113,0.15)",  Icon: AlertTriangle  },
  medium: { label: "Medium Impact", color: "#fbbf24", bg: "rgba(251,191,36,0.06)",   border: "rgba(251,191,36,0.15)",   Icon: TrendingUp     },
  low:    { label: "Low Impact",    color: "#34d399", bg: "rgba(52,211,153,0.06)",   border: "rgba(52,211,153,0.15)",   Icon: CheckCircle2   },
};

const FILTER_OPTIONS = ["all", "high", "medium", "low", "Authorization", "Billing", "Coverage"];

type Change = (typeof DEMO_COMPARE.changes)[0];

function ChangeCard({ change, index }: { change: Change; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const tc = CHANGE_TYPE_COLORS[change.change_type] || "bg-slate-500/10 text-slate-400 border-slate-500/18";
  const rc = RISK_CONFIG[change.risk_level as keyof typeof RISK_CONFIG];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="rounded-2xl overflow-hidden"
      style={{ border: "1px solid rgba(0,0,0,0.04)", background: "#ffffff" }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left px-6 py-4 flex items-center justify-between hover:bg-black/2 transition-colors"
      >
        <div className="flex items-center gap-3 flex-wrap">
          <span className={`text-[11px] px-2.5 py-1 rounded-lg border font-semibold ${tc}`}>
            {change.change_type}
          </span>
          <p className="text-[15px] font-semibold text-slate-700">{change.area}</p>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-4">
          <div className="hidden sm:flex items-center gap-1.5">
            {rc && <rc.Icon className="w-3.5 h-3.5" style={{ color: rc.color }} />}
            <span className="text-[12px] font-semibold capitalize" style={{ color: rc?.color }}>{change.risk_level}</span>
          </div>
          <ChevronDown
            className="w-4 h-4 text-slate-500 transition-transform duration-200"
            style={{ transform: expanded ? "rotate(180deg)" : "rotate(0deg)" }}
          />
        </div>
      </button>

      <div className="grid grid-cols-2" style={{ borderTop: "1px solid rgba(0,0,0,0.03)" }}>
        <div className="px-6 py-4" style={{ borderRight: "1px solid rgba(0,0,0,0.03)" }}>
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">Before</p>
          <p className="text-[14px] text-slate-500 leading-relaxed">{change.old_value}</p>
        </div>
        <div className="px-6 py-4" style={{ background: "rgba(0,0,0,0.02)" }}>
          <p className="text-[10px] font-bold uppercase tracking-wider mb-2.5" style={{ color: "rgba(0,0,0,0.30)" }}>After</p>
          <p className="text-[14px] text-sky-600 leading-relaxed">{change.new_value}</p>
        </div>
      </div>

      <div style={{ borderTop: "1px solid rgba(0,0,0,0.03)" }}>
        {expanded ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="px-6 py-4"
            style={{ background: "rgba(0,0,0,0.01)" }}
          >
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Impact Assessment</p>
            <p className="text-[14px] text-slate-600 leading-relaxed">{change.impact}</p>
          </motion.div>
        ) : (
          <div className="px-6 py-3">
            <p className="text-[13px] text-slate-600 truncate">{change.impact}</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function FileDropZone({ label, file, onChange }: { label: string; file: File | null; onChange: (f: File) => void }) {
  return (
    <div
      className={`border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer ${
        file ? "border-sky-500/35 bg-sky-500/5" : "border-black/10 hover:border-black/18 hover:bg-black/2"
      }`}
      onClick={() => document.getElementById(label)?.click()}
    >
      <input id={label} type="file" accept=".pdf" className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onChange(f); }} />
      {file ? (
        <div className="flex flex-col items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-sky-500/15 flex items-center justify-center">
            <FileText className="w-5 h-5 text-sky-400" />
          </div>
          <p className="text-[14px] font-semibold text-gray-900 truncate max-w-full">{file.name}</p>
          <Badge variant="default">{(file.size / 1024 / 1024).toFixed(1)} MB</Badge>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-black/5 flex items-center justify-center">
            <Upload className="w-5 h-5 text-slate-600" />
          </div>
          <p className="text-[14px] font-semibold text-slate-600">{label === "old" ? "Old Policy" : "New Policy"}</p>
          <p className="text-[13px] text-slate-600">Click to upload PDF</p>
        </div>
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-black/7 bg-white p-14 flex flex-col items-center text-center gap-5"
    >
      <div className="w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
        <GitCompare className="w-8 h-8 text-violet-400" />
      </div>
      <div>
        <p className="text-[18px] font-bold text-slate-600 mb-2">No comparison yet</p>
        <p className="text-[14px] text-slate-600 max-w-sm leading-relaxed">
          Upload two policy PDFs above and click Compare, or load the demo to see how policy diffing works.
        </p>
      </div>
      <p className="text-[12px] text-slate-700 font-mono">
        Tip: The AI detects authorization, billing, and coverage changes between versions.
      </p>
    </motion.div>
  );
}

export default function ComparePage() {
  const [oldFile, setOldFile] = useState<File | null>(null);
  const [newFile, setNewFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState<CompareResponse | null>(null);
  const [error, setError]     = useState<string | null>(null);
  const [filter, setFilter]   = useState<string>("all");
  const [isDemo, setIsDemo]   = useState(false);

  const handleCompare = async () => {
    if (!oldFile || !newFile) {
      setError("Please upload both an old and new policy PDF before comparing.");
      return;
    }
    setLoading(true);
    setError(null);
    setIsDemo(false);
    try {
      const [oldDoc, newDoc] = await Promise.all([
        api.uploadDocument(oldFile),
        api.uploadDocument(newFile),
      ]);
      const res = await api.compareDocuments(oldDoc.id, newDoc.id);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    if (!result) return;
    const rows = [
      ["Area", "Old Policy", "New Policy", "Impact", "Risk", "Type"],
      ...result.changes.map((c) => [c.area, c.old_value, c.new_value, c.impact, c.risk_level, c.change_type]),
    ];
    const csv = rows.map((r) => r.map((v) => `"${v}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "policy_comparison.csv"; a.click();
  };

  const filteredChanges = result?.changes.filter(
    (c) => filter === "all" || c.risk_level === filter || c.change_type === filter
  ) || [];

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">

        <PageHero
          eyebrow="Policy Diff"
          title="Policy Comparison"
          subtitle="Detect authorization, coverage, and billing changes between policy versions. Every change is scored for risk and cited from the source document."
          gradient="#94a3b8"
          action={
            result ? (
              <div className="flex items-center gap-3">
                <Button variant="outline" size="sm" onClick={exportCSV} icon={<Download className="w-4 h-4" />}>
                  Export CSV
                </Button>
                <Button variant="ghost" size="sm" onClick={() => { setResult(null); setIsDemo(false); setError(null); }}>
                  New Comparison
                </Button>
              </div>
            ) : undefined
          }
        />

        {/* Upload zone */}
        <div className="rounded-2xl border border-black/7 bg-white p-6 mb-7">
          <h2 className="text-[18px] font-bold text-gray-900 mb-1.5" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
            Upload Two Policies to Compare
          </h2>
          <p className="text-[15px] text-slate-400 mb-5">
            Upload the old and new versions of any policy. AI will detect every material change.
          </p>
          <div className="grid grid-cols-[1fr_auto_1fr] gap-4 items-center">
            <FileDropZone label="old" file={oldFile} onChange={setOldFile} />
            <div className="flex flex-col items-center gap-1.5">
              <div className="w-10 h-10 rounded-full border border-black/10 bg-black/5 flex items-center justify-center">
                <ArrowRight className="w-4 h-4 text-slate-500" />
              </div>
              <p className="text-[11px] text-slate-700 font-mono">vs</p>
            </div>
            <FileDropZone label="new" file={newFile} onChange={setNewFile} />
          </div>

          {error && (
            <div className="mt-4 flex items-start gap-2.5 px-4 py-3 rounded-xl bg-red-500/8 border border-red-500/18">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <p className="text-[13px] text-red-500">{error}</p>
            </div>
          )}

          <div className="mt-5 flex items-center gap-3">
            <Button
              onClick={handleCompare}
              loading={loading}
              disabled={loading}
              icon={<GitCompare className="w-4 h-4" />}
              className="flex-1"
            >
              {loading ? "Comparing policies..." : "Compare Policies"}
            </Button>
            <Button
              variant="outline"
              onClick={() => { setResult(DEMO_COMPARE); setIsDemo(true); setError(null); }}
            >
              Load Demo
            </Button>
          </div>
        </div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {!result ? (
            <EmptyState key="empty" />
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-7"
            >
              {isDemo && (
                <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-amber-500/8 border border-amber-500/18">
                  <GitCompare className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <p className="text-[13px] text-amber-400 font-medium">Demo comparison — upload your own policies above to analyze real changes</p>
                </div>
              )}

              {/* Summary */}
              <div className="rounded-2xl border border-black/7 bg-white p-7">
                <div className="flex items-start justify-between gap-6 mb-5">
                  <div>
                    <h2 className="text-[20px] font-bold text-gray-900 mb-2" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      Comparison Summary
                    </h2>
                    <div className="flex items-center gap-2 text-[13px] text-slate-500">
                      <FileText className="w-3.5 h-3.5 shrink-0" />
                      <span>{result.old_doc_name}</span>
                      <ArrowRight className="w-3.5 h-3.5 shrink-0" />
                      <FileText className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                      <span className="text-sky-400">{result.new_doc_name}</span>
                    </div>
                  </div>
                </div>
                <p className="text-[15px] text-slate-600 leading-relaxed mb-6">{result.summary}</p>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-5 rounded-xl bg-black/4 border border-black/6">
                    <p className="text-4xl font-black text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      {result.total_changes}
                    </p>
                    <p className="text-[13px] text-slate-400 mt-1.5">Total Changes</p>
                  </div>
                  <div className="text-center p-5 rounded-xl" style={{ background: "rgba(248,113,113,0.06)", border: "1px solid rgba(248,113,113,0.15)" }}>
                    <p className="text-4xl font-black text-red-400" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      {result.high_risk_count}
                    </p>
                    <p className="text-[13px] text-slate-400 mt-1.5">High Risk</p>
                  </div>
                  <div className="text-center p-5 rounded-xl" style={{ background: "rgba(52,211,153,0.06)", border: "1px solid rgba(52,211,153,0.15)" }}>
                    <p className="text-4xl font-black text-emerald-400" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      {result.total_changes - result.high_risk_count}
                    </p>
                    <p className="text-[13px] text-slate-400 mt-1.5">Low / Medium</p>
                  </div>
                </div>
              </div>

              {/* Filters */}
              <div className="flex items-center gap-2 flex-wrap">
                {FILTER_OPTIONS.map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`text-[13px] px-3.5 py-1.5 rounded-lg border transition-all capitalize font-semibold ${
                      filter === f
                        ? "border-sky-500/40 bg-sky-500/14 text-sky-400"
                        : "border-black/8 bg-black/4 text-slate-400 hover:text-slate-700 hover:border-black/14"
                    }`}
                  >
                    {f}
                  </button>
                ))}
                <span className="ml-auto text-[13px] text-slate-500">
                  <span className="font-semibold text-gray-900 font-mono">{filteredChanges.length}</span> changes
                </span>
              </div>

              {/* Changes — grouped by risk level */}
              <div className="space-y-8">
                {(["high", "medium", "low"] as const).map((riskLevel) => {
                  const changes = filteredChanges.filter((c) => c.risk_level === riskLevel);
                  if (!changes.length) return null;
                  const rc = RISK_CONFIG[riskLevel];
                  return (
                    <div key={riskLevel} className="space-y-3">
                      <div
                        className="flex items-center gap-3 px-5 py-3 rounded-xl"
                        style={{ background: rc.bg, border: `1px solid ${rc.border}` }}
                      >
                        <rc.Icon className="w-4 h-4 shrink-0" style={{ color: rc.color }} />
                        <span className="text-[14px] font-bold" style={{ color: rc.color }}>{rc.label}</span>
                        <span className="text-[12px] font-semibold" style={{ color: `${rc.color}80` }}>
                          — {changes.length} change{changes.length !== 1 ? "s" : ""}
                        </span>
                      </div>
                      {changes.map((change, i) => (
                        <ChangeCard key={i} change={change} index={i} />
                      ))}
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardLayout>
  );
}
