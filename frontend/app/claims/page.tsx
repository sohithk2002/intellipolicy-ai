"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { Badge } from "@/components/ui/Badge";
import { getDecisionColor } from "@/lib/utils";
import {
  ShieldCheck, CheckCircle2, XCircle, AlertTriangle,
  FileText, ArrowRight, RefreshCw, Clock, Zap, ScrollText, AlertCircle,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ClaimValidationResponse } from "@/lib/types";
import { useDocumentContext } from "@/lib/DocumentContext";

const PLAN_TYPES = ["Commercial", "Medicare Advantage", "Medicaid", "Self-Insured"];

const DEMO_CASES = [
  {
    cpt_code: "70553",
    diagnosis_code: "M54.5",
    plan_type: "Commercial",
    procedure: "MRI Brain with Contrast",
    service_date: "2026-02-15",
    tag: "Demo",
  },
  {
    cpt_code: "99213",
    diagnosis_code: "J06.9",
    plan_type: "Medicare Advantage",
    procedure: "Office Visit Level 3",
    service_date: "2026-02-10",
    tag: "Demo",
  },
];

const TIMELINE_STEPS = [
  "Input received",
  "Structured rule search",
  "Document fallback search",
  "Relevant evidence found",
  "Decision generated",
];

export default function ClaimsPage() {
  const { selectedDoc } = useDocumentContext();
  const [form, setForm] = useState({
    cpt_code: "",
    diagnosis_code: "",
    plan_type: "Commercial",
    procedure: "",
    service_date: new Date().toISOString().split("T")[0],
  });
  const [loading, setLoading]       = useState(false);
  const [result, setResult]         = useState<ClaimValidationResponse | null>(null);
  const [timelineStep, setTimelineStep] = useState(-1);
  const [error, setError]           = useState("");

  const update = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const simulateTimeline = async () => {
    for (let i = 0; i < TIMELINE_STEPS.length; i++) {
      setTimelineStep(i);
      await new Promise((r) => setTimeout(r, 300));
    }
  };

  const handleValidate = async () => {
    if (!form.cpt_code || !form.diagnosis_code) return;
    setLoading(true);
    setResult(null);
    setError("");
    setTimelineStep(-1);
    simulateTimeline();
    try {
      const res = await api.validateClaim({ ...form, document_id: selectedDoc?.id });
      setResult(res);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Validation failed. Make sure the backend is running and policy rules have been extracted."
      );
    } finally {
      setLoading(false);
    }
  };

  const loadDemoCase = (demo: typeof DEMO_CASES[0]) => {
    setForm({
      cpt_code: demo.cpt_code,
      diagnosis_code: demo.diagnosis_code,
      plan_type: demo.plan_type,
      procedure: demo.procedure,
      service_date: demo.service_date,
    });
    setResult(null);
    setError("");
    setTimelineStep(-1);
  };

  const clearAll = () => {
    setResult(null);
    setError("");
    setTimelineStep(-1);
    setForm({
      cpt_code: "",
      diagnosis_code: "",
      plan_type: "Commercial",
      procedure: "",
      service_date: new Date().toISOString().split("T")[0],
    });
  };

  const DecisionIcon =
    result?.decision === "Approved" ? CheckCircle2 : result?.decision === "Denied" ? XCircle : AlertTriangle;
  const decisionIconColor =
    result?.decision === "Approved" ? "text-emerald-400" : result?.decision === "Denied" ? "text-red-400" : "text-amber-400";

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">

        <PageHero
          eyebrow="Claims Validation"
          title="Claims Validator"
          subtitle="Check CPT codes, diagnosis codes, and plan types against extracted policy rules to produce traceable, audit-ready coverage decisions."
          gradient="#fbbf24"
          action={
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-sky-500/10 border border-sky-500/18 text-sky-400 text-sm font-semibold">
              <ShieldCheck className="w-4 h-4" />
              AI-Powered Decision Engine
            </div>
          }
        />

        <div className="grid gap-7" style={{ gridTemplateColumns: "minmax(0,55fr) minmax(0,45fr)" }}>

          {/* ── Claim Input Form ── */}
          <div className="space-y-5">
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <h2 className="text-[20px] font-bold text-gray-900 mb-1.5" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                Claim Information
              </h2>
              <p className="text-[15px] text-slate-400 mb-6">Enter claim details to validate against extracted policy rules</p>

              <div className="space-y-5">
                {[
                  { label: "CPT Code",                key: "cpt_code",       placeholder: "e.g. 70553, 99213"            },
                  { label: "Diagnosis Code (ICD-10)", key: "diagnosis_code", placeholder: "e.g. M54.5, J06.9"            },
                  { label: "Procedure Description",   key: "procedure",      placeholder: "e.g. MRI Brain with Contrast" },
                  { label: "Service Date",             key: "service_date",   type: "date"                                },
                ].map((field) => (
                  <div key={field.key}>
                    <label className="text-[13px] font-semibold text-slate-400 mb-1.5 block">{field.label}</label>
                    <input
                      type={field.type || "text"}
                      value={form[field.key as keyof typeof form]}
                      onChange={(e) => update(field.key, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full bg-black/4 border border-black/8 rounded-xl px-4 py-3 text-[15px] text-slate-700 placeholder:text-slate-600 focus:outline-none focus:border-black/20 transition-colors"
                    />
                  </div>
                ))}
                <div>
                  <label className="text-[13px] font-semibold text-slate-400 mb-1.5 block">Plan Type</label>
                  <select
                    value={form.plan_type}
                    onChange={(e) => update("plan_type", e.target.value)}
                    className="w-full bg-black/4 border border-black/8 rounded-xl px-4 py-3 text-[15px] text-slate-700 focus:outline-none focus:border-black/20 transition-colors appearance-none"
                  >
                    {PLAN_TYPES.map((t) => (
                      <option key={t} value={t} className="bg-white">{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              {error && (
                <div className="mt-4 flex items-start gap-2.5 px-4 py-3 rounded-xl bg-red-500/8 border border-red-500/18">
                  <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <p className="text-[13px] text-red-400">{error}</p>
                </div>
              )}

              <div className="mt-6 flex gap-3">
                <Button
                  onClick={handleValidate}
                  loading={loading}
                  disabled={!form.cpt_code || !form.diagnosis_code || loading}
                  icon={<ShieldCheck className="w-4 h-4" />}
                  className="flex-1"
                >
                  {loading ? "Validating..." : "Validate Claim"}
                </Button>
                <Button variant="ghost" size="md" onClick={clearAll} icon={<RefreshCw className="w-4 h-4" />}>
                  Clear
                </Button>
              </div>
            </div>

            {/* Demo Cases */}
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <div className="flex items-center gap-2.5 mb-1.5">
                <Zap className="w-4 h-4 text-amber-400" />
                <p className="text-[16px] font-bold text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                  Load Demo Claim
                </p>
              </div>
              <p className="text-[13px] text-slate-600 mb-4">Pre-fills the form. Results depend on what rules are extracted from your uploaded document.</p>
              <div className="space-y-2.5">
                {DEMO_CASES.map((demo, i) => (
                  <button
                    key={i}
                    onClick={() => loadDemoCase(demo)}
                    className="w-full flex items-center gap-4 p-5 rounded-xl border border-black/6 bg-black/2 hover:bg-black/5 hover:border-black/12 transition-all text-left"
                  >
                    <div className="w-9 h-9 rounded-lg bg-black/5 border border-black/7 flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4 text-sky-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[14px] font-semibold text-slate-700">{demo.procedure}</p>
                      <p className="text-[12px] text-slate-500 font-mono mt-0.5">CPT {demo.cpt_code} · {demo.plan_type}</p>
                    </div>
                    <Badge variant="warning" className="shrink-0">Demo</Badge>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ── Decision Panel ── */}
          <div className="space-y-5">
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="rounded-2xl border border-black/7 bg-white p-8 flex flex-col items-center gap-5"
                >
                  <div className="w-16 h-16 rounded-2xl bg-sky-500/10 border border-sky-500/18 flex items-center justify-center">
                    <ShieldCheck className="w-8 h-8 text-sky-400 animate-pulse" />
                  </div>
                  <div className="text-center">
                    <p className="text-[18px] font-bold text-gray-900 mb-1" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      Validating Claim...
                    </p>
                    <p className="text-[14px] text-slate-400">Checking against extracted policy rules</p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="loading-dot" /><div className="loading-dot" /><div className="loading-dot" />
                  </div>
                  <div className="w-full space-y-2.5">
                    {TIMELINE_STEPS.map((step, i) => (
                      <div key={step} className={`flex items-center gap-3 text-[14px] transition-all ${i <= timelineStep ? "text-slate-600" : "text-slate-700"}`}>
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-all ${
                          i < timelineStep ? "bg-emerald-500/20 text-emerald-400" : i === timelineStep ? "bg-sky-500/20 text-sky-400 pulse-glow" : "bg-black/5"
                        }`}>
                          {i < timelineStep ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                        </div>
                        {step}
                      </div>
                    ))}
                  </div>
                </motion.div>
              ) : result ? (
                <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">

                  {/* Decision banner */}
                  <div className={`rounded-2xl border p-9 text-center ${getDecisionColor(result.decision)}`}>
                    <DecisionIcon className={`w-12 h-12 mx-auto mb-4 ${decisionIconColor}`} />
                    <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-2">Validation Decision</p>
                    <p className={`text-[52px] font-black leading-none mb-5 ${decisionIconColor}`} style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      {result.decision}
                    </p>
                    <div className="flex justify-center mb-5">
                      <ConfidenceMeter score={result.confidence} showBar={false} />
                    </div>
                    <div className="border-t border-black/8 pt-5">
                      <p className="text-[15px] text-slate-600 leading-relaxed">{result.reason}</p>
                    </div>
                  </div>

                  {/* Validation pipeline */}
                  <div className="rounded-2xl border border-black/7 bg-white p-6">
                    <p className="text-[12px] font-bold text-slate-500 uppercase tracking-wider mb-4">Validation Pipeline</p>
                    <div className="space-y-3.5">
                      {TIMELINE_STEPS.map((step) => {
                        // Steps skipped when rule was matched directly
                        const isSkipped =
                          result.rule_matched &&
                          (step === "Document fallback search" || step === "Relevant evidence found");

                        if (isSkipped) {
                          return (
                            <div key={step} className="flex items-center gap-3 text-[14px] text-slate-700">
                              <div className="w-4 h-4 rounded-full border border-black/10 shrink-0" />
                              {step}
                              <span className="ml-1 text-[11px] text-slate-700 font-medium">(skipped — rule matched)</span>
                            </div>
                          );
                        }

                        let active = true;
                        let tag: React.ReactNode = null;

                        if (step === "Structured rule search") {
                          active = result.rule_matched;
                          tag = result.rule_matched
                            ? <span className="ml-1 text-[11px] text-emerald-500 font-medium">(rule matched)</span>
                            : <span className="ml-1 text-[11px] text-amber-600 font-medium">(no rule matched)</span>;
                        } else if (step === "Document fallback search") {
                          active = !!result.document_fallback_performed;
                        } else if (step === "Relevant evidence found") {
                          const hasEvidence =
                            !!result.document_fallback_performed &&
                            !result.policy_source.startsWith("No matching") &&
                            result.confidence > 0.1;
                          active = hasEvidence;
                          tag = hasEvidence
                            ? <span className="ml-1 text-[11px] text-emerald-500 font-medium">(found)</span>
                            : <span className="ml-1 text-[11px] text-amber-600 font-medium">(none found)</span>;
                        }

                        return (
                          <div key={step} className={`flex items-center gap-3 text-[14px] ${active ? "text-slate-600" : "text-slate-600"}`}>
                            {active
                              ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                              : <AlertTriangle className="w-4 h-4 text-amber-500/60 shrink-0" />
                            }
                            {step}{tag}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Policy source */}
                  <div className="rounded-2xl border border-black/7 bg-white p-6">
                    <div className="flex items-center gap-2.5 mb-3">
                      <FileText className="w-4 h-4 text-sky-400" />
                      <p className="text-[15px] font-bold text-gray-900">Policy Source</p>
                    </div>
                    <p className="text-[15px] text-slate-600">{result.policy_source}</p>
                    {result.source_page && (
                      <Badge variant="info" className="mt-3">Page {result.source_page}</Badge>
                    )}
                  </div>

                  {/* Missing info */}
                  {result.missing_info.length > 0 && (
                    <div className="rounded-xl border border-amber-500/18 bg-amber-500/5 p-6">
                      <p className="text-[13px] font-bold text-amber-400 mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" /> Missing Information
                      </p>
                      <ul className="space-y-3">
                        {result.missing_info.map((item, i) => (
                          <li key={i} className="text-[14px] text-slate-600 flex items-center gap-2.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />{item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Next steps */}
                  {result.next_steps.length > 0 && (
                    <div className="rounded-2xl border border-black/7 bg-white p-6">
                      <p className="text-[16px] font-bold text-gray-900 mb-5">Recommended Next Steps</p>
                      <div className="space-y-4">
                        {result.next_steps.map((step, i) => (
                          <div key={i} className="flex items-start gap-3">
                            <span className="w-6 h-6 rounded-full bg-sky-500/14 text-sky-400 text-[12px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                              {i + 1}
                            </span>
                            <p className="text-[14px] text-slate-600 leading-relaxed">{step}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Flow actions */}
                  <div className="flex gap-3">
                    <Link href="/audit" className="flex-1">
                      <Button variant="outline" className="w-full" icon={<ScrollText className="w-4 h-4" />}>
                        View Audit Trail
                      </Button>
                    </Link>
                    <Button variant="ghost" size="md" onClick={clearAll} icon={<RefreshCw className="w-4 h-4" />}>
                      New Claim
                    </Button>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="rounded-2xl border border-black/7 bg-white p-12 flex flex-col items-center gap-5 text-center"
                >
                  <div className="w-16 h-16 rounded-2xl bg-black/4 border border-black/7 flex items-center justify-center">
                    <ShieldCheck className="w-8 h-8 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-[18px] font-bold text-slate-400 mb-2" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      Decision will appear here
                    </p>
                    <p className="text-[14px] text-slate-600 max-w-xs leading-relaxed">
                      Enter claim details and click Validate Claim to check against extracted policy rules.
                    </p>
                    <p className="text-[13px] text-slate-700 mt-2 max-w-xs leading-relaxed">
                      Tip: extract rules from an uploaded document first for accurate results.
                    </p>
                  </div>
                  <div className="flex flex-col items-center gap-2 mt-2">
                    {TIMELINE_STEPS.map((step) => (
                      <div key={step} className="flex items-center gap-2 text-[13px] text-slate-700">
                        <div className="w-3.5 h-3.5 rounded-full border border-black/10" />
                        {step}
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
