"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { Badge } from "@/components/ui/Badge";
import {
  FileCode2, Copy, Download, Sparkles, CheckCircle2,
  FileText, Tag, ShieldCheck, ArrowRight, Zap, AlertCircle,
  Clock, AlertTriangle, User, Ban, Eye, BookOpen,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { BusinessRule } from "@/lib/types";
import { useDocumentContext } from "@/lib/DocumentContext";

// ─── Severity ────────────────────────────────────────────────────────────────

const HIGH_KW = [
  "prior authorization", "prior auth", "shall not", "must not", "prohibited",
  "denied", "not covered", "not allowed", "forbidden", "step therapy",
  "exclusion", "require authorization", "authorization required", "coverage denied",
];
const MED_KW = [
  "documentation required", "medical necessity", "approval required", "requires",
  "frequency", "limit", "maximum", "restriction", "supervision required",
  "must obtain", "authorization timing",
];

function classifySeverity(rule: BusinessRule): "High" | "Medium" | "Low" {
  const txt = [
    rule.procedure, rule.rule_type, rule.restriction, rule.raw_text,
    rule.requires_prior_authorization ? "prior authorization" : "",
  ].filter(Boolean).join(" ").toLowerCase();
  if (HIGH_KW.some((k) => txt.includes(k))) return "High";
  if (MED_KW.some((k) => txt.includes(k))) return "Medium";
  return "Low";
}

const SEV_STYLE = {
  High:   { color: "#f87171", bg: "rgba(248,113,113,0.07)", border: "rgba(248,113,113,0.22)" },
  Medium: { color: "#fbbf24", bg: "rgba(251,191,36,0.07)",  border: "rgba(251,191,36,0.22)"  },
  Low:    { color: "#34d399", bg: "rgba(52,211,153,0.07)",  border: "rgba(52,211,153,0.22)"  },
};

// ─── Rule type badge variants ─────────────────────────────────────────────────

const RULE_TYPE_VARIANT: Record<string, "danger" | "warning" | "info" | "success" | "default" | "muted"> = {
  "Prior Authorization": "danger",
  "Prohibitions":        "danger",
  "Provider Restriction":"warning",
  "Supervision":         "warning",
  "Billing":             "info",
  "Payment":             "info",
  "Coding":              "info",
  "Coverage":            "success",
  "Eligibility":         "success",
  "Documentation":       "default",
  "Frequency Limits":    "default",
  "Time Windows":        "default",
  "Exceptions":          "muted",
  "Policy":              "muted",
};

// ─── Confidence color ─────────────────────────────────────────────────────────

function confColor(c: number) {
  if (c >= 0.85) return "#34d399";
  if (c >= 0.70) return "#111827";
  if (c >= 0.55) return "#fbbf24";
  return "#94a3b8";
}

// ─── Deduplication ───────────────────────────────────────────────────────────

function deduplicateRules(rules: BusinessRule[]): BusinessRule[] {
  const seen = new Map<string, BusinessRule>();
  for (const rule of rules) {
    const cpt   = (rule.cpt_code  || "").trim().toLowerCase();
    const type  = (rule.rule_type || "").trim().toLowerCase();
    const actr  = (rule.actor     || "").trim().toLowerCase();
    const restr = (rule.restriction || "").slice(0, 50).trim().toLowerCase().replace(/\s+/g, " ");
    const rawNorm = rule.raw_text.slice(0, 80).toLowerCase().replace(/\s+/g, " ");

    const key = cpt
      ? `cpt:${cpt}|type:${type}`
      : actr && restr
        ? `actor:${actr}|restr:${restr}`
        : `raw:${rawNorm}`;

    if (!seen.has(key)) {
      seen.set(key, { ...rule });
    } else {
      const ex = seen.get(key)!;
      seen.set(key, {
        ...ex,
        confidence: Math.max(ex.confidence, rule.confidence),
        documentation_required: [
          ...new Set([...ex.documentation_required, ...rule.documentation_required]),
        ],
        restriction:           ex.restriction           ?? rule.restriction,
        allowed_action:        ex.allowed_action        ?? rule.allowed_action,
        condition:             ex.condition             ?? rule.condition,
        actor:                 ex.actor                 ?? rule.actor,
        rule_type:             ex.rule_type             ?? rule.rule_type,
        authorization_timing:  ex.authorization_timing  ?? rule.authorization_timing,
        emergency_exception:   ex.emergency_exception   ?? rule.emergency_exception,
        source_page:           ex.source_page           ?? rule.source_page,
      });
    }
  }
  return Array.from(seen.values());
}

// ─── IF → THEN logic ─────────────────────────────────────────────────────────

const ACTION_VERBS = /^(interpret|perform|bill|diagnose|administer|order|prescribe|render|provide|report|submit)\s+/i;

function ucFirst(s: string) { return s.charAt(0).toUpperCase() + s.slice(1); }

function generateIfThen(rule: BusinessRule): { ifs: string[]; thens: string[] } {
  const ifs: string[] = [];
  const thens: string[] = [];

  if (rule.actor)    ifs.push(`Provider = ${rule.actor}`);
  if (rule.cpt_code) ifs.push(`CPT Code = ${rule.cpt_code}`);
  if (rule.icd_code) ifs.push(`Diagnosis = ${rule.icd_code}`);
  if (rule.plan_type && rule.plan_type !== "All Plans")
    ifs.push(`Plan Type = ${rule.plan_type}`);
  if (rule.restriction) {
    const svc = rule.restriction.replace(ACTION_VERBS, "");
    if (svc !== rule.restriction) ifs.push(`Service = ${ucFirst(svc)}`);
  }

  if (rule.restriction)                  thens.push(`${ucFirst(rule.restriction)} → Not Allowed`);
  if (rule.allowed_action)               thens.push(`${ucFirst(rule.allowed_action)} → Allowed`);
  if (rule.condition)                    thens.push(`Requires ${ucFirst(rule.condition)} → Yes`);
  if (rule.requires_prior_authorization) thens.push("Prior Authorization → Required");
  if (rule.authorization_timing)         thens.push(`Authorization Timing → ${rule.authorization_timing}`);
  if (rule.documentation_required.length)thens.push("Documentation → Required");

  return { ifs, thens };
}

// ─── Summary stats ────────────────────────────────────────────────────────────

function computeSummary(rules: BusinessRule[]) {
  const categories = [...new Set(rules.map((r) => r.rule_type).filter(Boolean))] as string[];
  const highSev    = rules.filter((r) => classifySeverity(r) === "High").length;
  const avgConf    = rules.reduce((s, r) => s + r.confidence, 0) / (rules.length || 1);
  const readyCount = rules.filter((r) => r.cpt_code || (r.actor && r.restriction)).length;
  const cpts       = [...new Set(rules.flatMap((r) =>
    r.cpt_code ? r.cpt_code.split(/[,/\s]+/).filter(Boolean) : []))];
  const planTypes  = [...new Set(rules.map((r) => r.plan_type).filter(Boolean))] as string[];
  const providers  = [...new Set(rules.map((r) => r.actor).filter(Boolean))] as string[];
  return { categories, highSev, avgConf, readyCount, cpts, planTypes, providers };
}

// ─── JSON colouriser (no external deps, safe: we control the data) ────────────

function colorizeJson(json: string): string {
  return json
    .replace(/("(?:[^"\\]|\\.)*")(\s*:)/g,
      '<span style="color:#ffffff">$1</span>$2')
    .replace(/:\s*("(?:[^"\\]|\\.)*")/g,
      ': <span style="color:#a5f3fc">$1</span>')
    .replace(/:\s*(true|false|null)/g,
      ': <span style="color:#f87171">$1</span>')
    .replace(/:\s*(-?\d+\.?\d*)/g,
      ': <span style="color:#fbbf24">$1</span>');
}

// ─── Demo data ────────────────────────────────────────────────────────────────

const DEMO_TEXT = `MRI procedures (CPT codes 70553, 71552, 72148) require prior authorization for commercial plan members. Authorization must be obtained through the portal at least 72 hours prior to the scheduled service date. Emergency requests may be submitted within 24 hours post-service.

Specialty biologic medications require step therapy documentation showing failure of at least two preferred alternatives before approval. This applies to all commercial and Medicare Advantage plans effective January 1, 2026.

CPT code 99213 office visits require medical necessity documentation when billed more than 4 times in a rolling 90-day period for the same diagnosis code.`;

const DEMO_RULES: BusinessRule[] = [
  {
    procedure: "MRI — Prior Authorization",
    cpt_code: "70553, 71552, 72148",
    plan_type: "Commercial",
    requires_prior_authorization: true,
    documentation_required: ["Auth portal submission", "Physician order", "Clinical notes"],
    effective_date: "2026-01-01",
    authorization_timing: "72 hours before scheduled service",
    emergency_exception: "within 24 hours after service",
    source_page: 18,
    confidence: 0.94,
    raw_text: "MRI procedures (CPT codes 70553, 71552, 72148) require prior authorization for commercial plan members.",
    rule_type: "Prior Authorization",
  },
  {
    procedure: "Specialty Biologics — Prior Authorization",
    cpt_code: "J-codes",
    plan_type: "Commercial",
    requires_prior_authorization: true,
    documentation_required: ["Step therapy failure documentation", "2 preferred alternatives tried"],
    effective_date: "2026-01-01",
    source_page: 32,
    confidence: 0.89,
    raw_text: "Specialty biologic medications require step therapy documentation showing failure of at least two preferred alternatives.",
    rule_type: "Prior Authorization",
  },
  {
    procedure: "Office Visit — Billing Rule",
    cpt_code: "99213",
    plan_type: "All Plans",
    requires_prior_authorization: false,
    documentation_required: ["Medical necessity when > 4x per 90 days", "Same diagnosis code requirement"],
    effective_date: "2026-01-01",
    source_page: 41,
    confidence: 0.87,
    raw_text: "CPT code 99213 office visits require medical necessity documentation when billed more than 4 times in a rolling 90-day period.",
    rule_type: "Frequency Limits",
  },
];

// ─── IfThenBlock ──────────────────────────────────────────────────────────────

function IfThenBlock({ ifs, thens }: { ifs: string[]; thens: string[] }) {
  if (!ifs.length || !thens.length) return null;
  return (
    <div className="px-6 py-4 border-t border-black/5" style={{ background: "rgba(0,0,0,0.02)" }}>
      <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-3">Validation Logic</p>
      <div className="font-mono text-[12px] space-y-2.5">
        <div className="flex items-start gap-3">
          <span className="text-sky-400 font-bold w-8 shrink-0 pt-px">IF</span>
          <div className="space-y-1">
            {ifs.map((c, i) => (
              <div key={i} className="flex items-center gap-2">
                {i > 0 && <span className="text-slate-700 text-[10px] font-bold">AND</span>}
                <span className={`text-slate-600 ${i > 0 ? "ml-[29px]" : ""}`}>{c}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="flex items-start gap-3">
          <span className="text-emerald-400 font-bold w-8 shrink-0 pt-px">THEN</span>
          <div className="space-y-1">
            {thens.map((a, i) => (
              <p key={i} className="text-slate-600">{a}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── RuleCard ────────────────────────────────────────────────────────────────

function RuleCard({
  rule, index, sourceDocName,
}: {
  rule: BusinessRule;
  index: number;
  sourceDocName: string;
}) {
  const [jsonOpen,   setJsonOpen]   = useState(false);
  const [traceOpen,  setTraceOpen]  = useState(false);
  const [copied,     setCopied]     = useState(false);

  const severity  = classifySeverity(rule);
  const sev       = SEV_STYLE[severity];
  const { ifs, thens } = generateIfThen(rule);

  const hasAppliesTo  = !!(rule.actor || rule.cpt_code || rule.icd_code);
  const hasRHS        = !!(rule.restriction || rule.allowed_action);
  const hasConditions = !!(rule.condition || rule.authorization_timing || rule.emergency_exception);
  const hasDocs       = rule.documentation_required.length > 0;
  const hasIfThen     = ifs.length > 0 && thens.length > 0;

  const copy = () => {
    navigator.clipboard.writeText(JSON.stringify(rule, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.055 }}
      className="rounded-2xl overflow-hidden"
      style={{ border: `1px solid ${sev.border}`, background: "#ffffff" }}
    >
      {/* ── Card header ── */}
      <div className="px-6 pt-5 pb-4" style={{ background: sev.bg }}>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            {rule.rule_type && (
              <Badge variant={RULE_TYPE_VARIANT[rule.rule_type] ?? "muted"}>{rule.rule_type}</Badge>
            )}
            <span
              className="text-[10px] font-bold px-2 py-0.5 rounded-full border"
              style={{ color: sev.color, background: sev.bg, borderColor: sev.border }}
            >
              {severity} Risk
            </span>
          </div>
          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={() => setJsonOpen(!jsonOpen)}
              className="flex items-center gap-1 text-[11px] font-semibold px-2 py-1 rounded-lg border border-black/8 text-slate-500 hover:text-sky-400 hover:border-sky-500/30 transition-all"
            >
              <FileCode2 className="w-3 h-3" />
              JSON
            </button>
            <button onClick={copy} className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 hover:text-sky-400 transition-colors">
              {copied
                ? <><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Copied</>
                : <><Copy className="w-3.5 h-3.5" /> Copy</>}
            </button>
          </div>
        </div>

        <p className="text-[17px] font-bold text-gray-900 leading-snug mb-2">{rule.procedure}</p>

        <div className="flex items-center gap-3 flex-wrap" style={{ fontSize: 12, color: "rgba(100,116,139,0.8)" }}>
          <span className="font-mono">Rule {index + 1}</span>
          <span>·</span>
          <span style={{ color: confColor(rule.confidence) }} className="font-semibold">
            {Math.round(rule.confidence * 100)}% confidence
          </span>
          {rule.source_page != null && (
            <>
              <span>·</span>
              <span className="flex items-center gap-1">
                <BookOpen className="w-3 h-3" /> Page {rule.source_page}
              </span>
            </>
          )}
          {rule.cpt_code && (
            <>
              <span>·</span>
              <span className="font-mono" style={{ color: "#111827" }}>{rule.cpt_code}</span>
            </>
          )}
          {rule.effective_date && (
            <>
              <span>·</span>
              <span className="font-mono">{rule.effective_date}</span>
            </>
          )}
        </div>
      </div>

      {/* ── Validation logic ── */}
      {hasIfThen && <IfThenBlock ifs={ifs} thens={thens} />}

      {/* ── Applies To / Restrictions grid ── */}
      {(hasAppliesTo || hasRHS) && (
        <div
          className="grid border-t border-black/5"
          style={{ gridTemplateColumns: hasAppliesTo && hasRHS ? "1fr 1fr" : "1fr" }}
        >
          {hasAppliesTo && (
            <div className="px-5 py-4" style={{ borderRight: hasRHS ? "1px solid rgba(0,0,0,0.03)" : "none" }}>
              <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-3">Applies To</p>
              <div className="space-y-2">
                {rule.actor && (
                  <div className="flex items-center gap-2">
                    <User className="w-3 h-3 text-sky-400 shrink-0" />
                    <span className="text-[13px] text-slate-700">{rule.actor}</span>
                  </div>
                )}
                {rule.cpt_code && (
                  <div className="flex items-center gap-2">
                    <Tag className="w-3 h-3 text-indigo-400 shrink-0" />
                    <span className="text-[13px] text-slate-700 font-mono">{rule.cpt_code}</span>
                  </div>
                )}
                {rule.icd_code && (
                  <div className="flex items-center gap-2">
                    <Tag className="w-3 h-3 text-violet-400 shrink-0" />
                    <span className="text-[13px] text-slate-700 font-mono">ICD: {rule.icd_code}</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <FileText className="w-3 h-3 text-slate-600 shrink-0" />
                  <span className="text-[13px] text-slate-400">{rule.plan_type || "All Plans"}</span>
                </div>
              </div>
            </div>
          )}

          {hasRHS && (
            <div className="px-5 py-4 space-y-3">
              {rule.restriction && (
                <div>
                  <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Restriction</p>
                  <div className="flex items-start gap-2">
                    <Ban className="w-3 h-3 text-red-400 mt-0.5 shrink-0" />
                    <span className="text-[13px] text-red-300 leading-snug">{rule.restriction}</span>
                  </div>
                </div>
              )}
              {rule.allowed_action && (
                <div>
                  <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Allowed Action</p>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400 mt-0.5 shrink-0" />
                    <span className="text-[13px] text-emerald-300 leading-snug">{rule.allowed_action}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Conditions ── */}
      {hasConditions && (
        <div className="px-6 py-4 border-t border-black/5 space-y-2.5" style={{ background: "rgba(251,191,36,0.025)" }}>
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Conditions</p>
          {rule.condition && (
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
              <span className="text-[13px] text-amber-300 leading-snug">{rule.condition}</span>
            </div>
          )}
          {rule.authorization_timing && (
            <div className="flex items-start gap-2.5">
              <Clock className="w-3.5 h-3.5 text-sky-400 mt-0.5 shrink-0" />
              <span className="text-[13px] text-slate-600">Submit: {rule.authorization_timing}</span>
            </div>
          )}
          {rule.emergency_exception && (
            <div className="flex items-start gap-2.5">
              <AlertCircle className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
              <span className="text-[13px] text-slate-600">Emergency window: {rule.emergency_exception}</span>
            </div>
          )}
        </div>
      )}

      {/* ── Documentation ── */}
      {hasDocs && (
        <div className="px-6 py-4 border-t border-black/5">
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-3">
            Documentation Required
            <span className="ml-2 font-mono" style={{ color: confColor(rule.confidence) }}>
              {Math.round(rule.confidence * 100)}%
            </span>
          </p>
          <div className="flex flex-wrap gap-2">
            {rule.documentation_required.map((d, di) => (
              <span
                key={di}
                className="text-[12px] px-2.5 py-1 rounded-lg font-mono"
                style={{ background: "rgba(0,0,0,0.06)", border: "1px solid rgba(0,0,0,0.12)", color: "#a5b4fc" }}
              >
                {d}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Traceability ── */}
      <div className="px-6 py-3.5 border-t border-black/5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 text-[12px]" style={{ color: "rgba(100,116,139,0.7)" }}>
            <FileText className="w-3 h-3 shrink-0" />
            <span>{sourceDocName || "Manual Input"}</span>
            {rule.source_page != null && (
              <>
                <span>·</span>
                <span>Page {rule.source_page}</span>
              </>
            )}
            {!rule.source_page && <span>· No page reference</span>}
          </div>
          <button
            onClick={() => setTraceOpen(!traceOpen)}
            className="flex items-center gap-1.5 text-[11px] font-semibold transition-colors shrink-0"
            style={{ color: traceOpen ? "#111827" : "rgba(100,116,139,0.6)" }}
          >
            <Eye className="w-3 h-3" />
            {traceOpen ? "Hide Source" : "View Source"}
          </button>
        </div>
        <AnimatePresence>
          {traceOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-3 rounded-xl p-3.5" style={{ background: "rgba(0,0,0,0.01)", border: "1px solid rgba(0,0,0,0.04)" }}>
                <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Source Chunk</p>
                <p className="text-[12px] font-mono leading-relaxed break-words" style={{ color: "rgba(148,163,184,0.8)" }}>
                  {rule.raw_text}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── JSON preview ── */}
      <AnimatePresence>
        {jsonOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
            style={{ borderTop: "1px solid rgba(0,0,0,0.03)" }}
          >
            <div className="px-6 py-4" style={{ background: "rgba(0,0,0,0.35)" }}>
              <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">JSON Preview</p>
              <pre
                className="text-[11px] font-mono leading-relaxed overflow-auto max-h-52 pr-2"
                style={{ color: "rgba(148,163,184,0.7)" }}
                dangerouslySetInnerHTML={{ __html: colorizeJson(JSON.stringify(rule, null, 2)) }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Card footer ── */}
      <div className="px-6 py-3 flex items-center justify-between border-t border-black/5" style={{ background: "rgba(0,0,0,0.01)" }}>
        <div className="flex items-center gap-2.5">
          {rule.source_page != null
            ? <Badge variant="info">Page {rule.source_page}</Badge>
            : <Badge variant="muted">Manual Input</Badge>}
          {!hasDocs && !hasConditions && !hasAppliesTo && (
            <span className="text-[11px] text-slate-700 italic">Limited metadata</span>
          )}
        </div>
        <ConfidenceMeter score={rule.confidence} showBar={false} />
      </div>
    </motion.div>
  );
}

// ─── Summary Panel ───────────────────────────────────────────────────────────

function SummaryPanel({ rules }: { rules: BusinessRule[] }) {
  const s = computeSummary(rules);

  const statGrid = [
    { label: "Total Rules",      value: rules.length,                    color: "#111827" },
    { label: "High Risk",        value: s.highSev,                       color: "#f87171" },
    { label: "Avg Confidence",   value: `${Math.round(s.avgConf * 100)}%`, color: "#34d399" },
    { label: "Ready for Claims", value: s.readyCount,                    color: "#111827" },
  ];

  return (
    <div className="rounded-2xl border border-black/7 bg-white p-6 space-y-5">
      <h2 className="text-[16px] font-bold text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
        Extraction Summary
      </h2>

      {/* Main stats */}
      <div className="grid grid-cols-4 gap-3">
        {statGrid.map((s) => (
          <div key={s.label} className="text-center p-4 rounded-xl bg-black/4 border border-black/6">
            <p className="text-2xl font-black" style={{ color: s.color, fontFamily: "var(--font-heading, sans-serif)" }}>
              {s.value}
            </p>
            <p className="text-[11px] text-slate-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Rule categories */}
      {s.categories.length > 0 && (
        <div>
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">Rule Categories</p>
          <div className="flex flex-wrap gap-2">
            {s.categories.map((c) => (
              <Badge key={c} variant={RULE_TYPE_VARIANT[c] ?? "muted"}>{c}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* CPT codes, Plan types, Providers — chip rows */}
      {s.cpts.length > 0 && (
        <div>
          <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Extracted CPT Codes</p>
          <div className="flex flex-wrap gap-1.5">
            {s.cpts.map((c) => (
              <span key={c} className="text-[11px] px-2 py-0.5 rounded font-mono"
                style={{ background: "rgba(0,0,0,0.07)", border: "1px solid rgba(0,0,0,0.13)", color: "#a5b4fc" }}>
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {s.planTypes.length > 0 && (
          <div>
            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Plan Types</p>
            <div className="flex flex-wrap gap-1.5">
              {s.planTypes.map((p) => (
                <span key={p} className="text-[11px] px-2 py-0.5 rounded"
                  style={{ background: "rgba(0,0,0,0.05)", border: "1px solid rgba(0,0,0,0.11)", color: "#7dd3fc" }}>
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
        {s.providers.length > 0 && (
          <div>
            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2">Extracted Providers</p>
            <div className="flex flex-wrap gap-1.5">
              {s.providers.map((p) => (
                <span key={p} className="text-[11px] px-2 py-0.5 rounded"
                  style={{ background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.18)", color: "#6ee7b7" }}>
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Success banner ───────────────────────────────────────────────────────────

function SuccessBanner({ count, timeS, avgConf, ready }: {
  count: number; timeS: number; avgConf: number; ready: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl px-5 py-3.5 flex items-center justify-between gap-4 flex-wrap"
      style={{ background: "rgba(52,211,153,0.07)", border: "1px solid rgba(52,211,153,0.20)" }}
    >
      <div className="flex items-center gap-2.5">
        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
        <span className="text-[14px] font-bold text-emerald-400">Rules Extracted Successfully</span>
      </div>
      <div className="flex items-center gap-4 text-[12px] text-slate-400 flex-wrap">
        <span><span className="text-gray-900 font-semibold">{count}</span> rules found</span>
        <span><span className="text-gray-900 font-semibold">{timeS.toFixed(1)}s</span> processing</span>
        <span><span className="text-gray-900 font-semibold">{Math.round(avgConf * 100)}%</span> avg confidence</span>
        <span><span className="text-emerald-400 font-semibold">{ready}</span> ready for validation</span>
      </div>
    </motion.div>
  );
}

// ─── Empty state ──────────────────────────────────────────────────────────────

function EmptyState({ hasDocuments }: { hasDocuments: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-black/7 bg-white p-12 flex flex-col items-center text-center gap-5"
    >
      <div className="w-14 h-14 rounded-2xl border border-black/7 bg-black/4 flex items-center justify-center">
        <FileCode2 className="w-7 h-7 text-slate-600" />
      </div>
      <div>
        <p className="text-[17px] font-bold text-slate-600 mb-2">Structured rules will appear here</p>
        <p className="text-[13px] text-slate-600 max-w-xs leading-relaxed">
          {hasDocuments
            ? "Select an indexed document above, or paste policy text and click Extract."
            : "Paste policy text and click Extract, or upload a document first."}
        </p>
      </div>
      <div className="text-left w-full max-w-sm space-y-2 mt-1">
        <p className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Supported rule types</p>
        <div className="flex flex-wrap gap-1.5">
          {["Authorization","Billing","Coverage","Documentation","Provider","Frequency","Supervision","Eligibility"].map((t) => (
            <span key={t} className="text-[11px] px-2 py-0.5 rounded bg-black/4 border border-black/7 text-slate-500">{t}</span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function NoRulesFound() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-2xl border border-red-500/15 bg-red-500/5 p-10 text-center space-y-4"
    >
      <AlertCircle className="w-8 h-8 text-red-400 mx-auto" />
      <div>
        <p className="text-[16px] font-bold text-red-300 mb-2">No structured business rules were detected.</p>
        <p className="text-[13px] text-slate-500 leading-relaxed max-w-sm mx-auto">
          The text may not contain actionable policy statements.
        </p>
      </div>
      <div className="text-left inline-block">
        <p className="text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-2">Suggestions</p>
        <ul className="space-y-1.5 text-[13px] text-slate-500">
          <li>• Select a different indexed document</li>
          <li>• Paste text containing authorization, billing, coverage,</li>
          <li className="pl-3">provider, documentation, or frequency rules</li>
          <li>• Look for keywords: <span className="font-mono text-slate-400">must · shall · may · required · prohibited</span></li>
        </ul>
      </div>
    </motion.div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function RulesPage() {
  const [text, setText]                     = useState("");
  const [loading, setLoading]               = useState(false);
  const [rawRules, setRawRules]             = useState<BusinessRule[]>([]);
  const [error, setError]                   = useState("");
  const [isDemo, setIsDemo]                 = useState(false);
  const [selectedDocId, setSelectedDocId]   = useState<string>("");
  const [extractingFromDoc, setExtractingFromDoc] = useState(false);
  const [sourceDocName, setSourceDocName]   = useState("Manual Input");
  const [extractionTime, setExtractionTime] = useState(0);
  const [showSuccess, setShowSuccess]       = useState(false);
  const startRef = useRef<number>(0);

  const { documents, selectedDoc } = useDocumentContext();

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (selectedDoc && !selectedDocId) setSelectedDocId(selectedDoc.id);
  }, [selectedDoc, selectedDocId]);

  // Deduplicate and enrich
  const rules = deduplicateRules(rawRules);
  const summary = computeSummary(rules);

  // ── Extract from pasted text ──
  const handleExtract = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setIsDemo(false);
    setError("");
    setShowSuccess(false);
    setSourceDocName("Manual Input");
    startRef.current = Date.now();
    try {
      const res = await api.extractRules(text);
      const elapsed = (Date.now() - startRef.current) / 1000;
      setExtractionTime(elapsed);
      setRawRules(res.rules);
      if (res.rules.length > 0) setShowSuccess(true);
      else setError("no-rules");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed. Check backend connection.");
      setRawRules([]);
    } finally {
      setLoading(false);
    }
  };

  // ── Extract from indexed document ──
  const handleExtractFromDoc = async () => {
    if (!selectedDocId) return;
    setExtractingFromDoc(true);
    setIsDemo(false);
    setError("");
    setShowSuccess(false);
    startRef.current = Date.now();
    const doc = documents.find((d) => d.id === selectedDocId);
    setSourceDocName(doc?.filename ?? "Indexed Document");
    try {
      const res = await api.extractRulesFromDocument(selectedDocId);
      const elapsed = (Date.now() - startRef.current) / 1000;
      setExtractionTime(elapsed);
      setRawRules(res.rules);
      if (res.rules.length > 0) setShowSuccess(true);
      else setError("no-rules");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed. Check backend connection.");
      setRawRules([]);
    } finally {
      setExtractingFromDoc(false);
    }
  };

  const loadDemo = () => {
    setText(DEMO_TEXT);
    setRawRules(DEMO_RULES);
    setIsDemo(true);
    setError("");
    setShowSuccess(false);
    setSourceDocName("Demo Data");
  };

  const downloadAll = () => {
    const blob = new Blob([JSON.stringify(rules, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "extracted_rules.json"; a.click();
  };

  const busy = loading || extractingFromDoc;

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">

        <PageHero
          eyebrow="Rule Engine"
          title="Rule Extraction"
          subtitle="Convert raw policy language into structured, machine-readable business rules with validation logic, severity classification, and full source traceability."
          gradient="#94a3b8"
          action={
            rules.length > 0 && !isDemo ? (
              <Button variant="outline" size="sm" onClick={downloadAll} icon={<Download className="w-4 h-4" />}>
                Export JSON ({rules.length})
              </Button>
            ) : undefined
          }
        />

        <div className="grid gap-7" style={{ gridTemplateColumns: "minmax(0,55fr) minmax(0,45fr)" }}>

          {/* ── Left: Inputs ── */}
          <div className="space-y-5">

            {/* Extract from indexed document */}
            {documents.length > 0 && (
              <div className="rounded-2xl border border-black/7 bg-white p-6">
                <div className="flex items-center gap-2.5 mb-4">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <h2 className="text-[16px] font-bold text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                    Extract from Indexed Document
                  </h2>
                </div>
                <p className="text-[13px] text-slate-500 mb-4">
                  Select an uploaded document and extract rules directly from its indexed content.
                </p>
                <div className="flex gap-3">
                  <select
                    value={selectedDocId}
                    onChange={(e) => setSelectedDocId(e.target.value)}
                    className="flex-1 bg-black/4 border border-black/8 rounded-xl px-4 py-2.5 text-[14px] text-slate-700 focus:outline-none focus:border-black/20 transition-colors appearance-none"
                  >
                    <option value="" className="bg-white text-slate-500">Select a document…</option>
                    {documents.map((doc) => (
                      <option key={doc.id} value={doc.id} className="bg-white">
                        {doc.filename} ({doc.page_count}p · {doc.chunk_count ?? "?"} chunks)
                      </option>
                    ))}
                  </select>
                  <Button
                    onClick={handleExtractFromDoc}
                    loading={extractingFromDoc}
                    disabled={!selectedDocId || busy}
                    icon={<Sparkles className="w-4 h-4" />}
                  >
                    Extract
                  </Button>
                </div>
              </div>
            )}

            {/* Manual text input */}
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <div className="flex items-center justify-between mb-1.5">
                <h2 className="text-[20px] font-bold text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                  Policy Text Input
                </h2>
                <span className="text-[12px] text-slate-600 font-mono">{text.length} chars</span>
              </div>
              <p className="text-[15px] text-slate-400 mb-5">
                Paste raw policy text. The engine will detect and extract all actionable business rules.
              </p>
              <textarea
                value={text}
                onChange={(e) => { setText(e.target.value); setIsDemo(false); }}
                rows={12}
                placeholder="Paste policy text here…"
                className="w-full bg-black/4 border border-black/8 rounded-xl px-4 py-3.5 text-[15px] text-slate-700 placeholder:text-slate-600 focus:outline-none focus:border-black/20 transition-colors resize-none font-mono leading-relaxed"
              />
              {error && error !== "no-rules" && (
                <div className="mt-3 flex items-start gap-2.5 px-4 py-3 rounded-xl bg-red-500/8 border border-red-500/18">
                  <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <p className="text-[13px] text-red-400">{error}</p>
                </div>
              )}
              <div className="mt-5 flex gap-3">
                <Button
                  onClick={handleExtract}
                  loading={loading}
                  disabled={!text.trim() || busy}
                  icon={<Sparkles className="w-4 h-4" />}
                  className="flex-1"
                >
                  {loading ? "Extracting rules…" : "Extract Business Rules"}
                </Button>
                <Button variant="secondary" onClick={loadDemo} disabled={busy} size="md">
                  Load Demo
                </Button>
              </div>
            </div>
          </div>

          {/* ── Right: Output ── */}
          <div className="space-y-4">
            {busy ? (
              <div className="rounded-2xl border border-black/7 bg-white p-10 flex flex-col items-center gap-5">
                <div className="w-16 h-16 rounded-2xl bg-sky-500/10 border border-sky-500/18 flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-sky-400 animate-pulse" />
                </div>
                <div className="text-center">
                  <p className="text-[18px] font-bold text-gray-900 mb-1.5" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                    Extracting Rules…
                  </p>
                  <p className="text-[14px] text-slate-400">Parsing policy language into structured business rules</p>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="loading-dot" /><div className="loading-dot" /><div className="loading-dot" />
                </div>
              </div>
            ) : error === "no-rules" ? (
              <NoRulesFound />
            ) : rules.length === 0 ? (
              <EmptyState hasDocuments={documents.length > 0} />
            ) : (
              <>
                {isDemo && (
                  <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-amber-500/8 border border-amber-500/18">
                    <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <p className="text-[13px] text-amber-400 font-medium">
                      Demo Mode — paste your own policy text and click Extract for real results
                    </p>
                  </div>
                )}

                {showSuccess && !isDemo && (
                  <SuccessBanner
                    count={rules.length}
                    timeS={extractionTime}
                    avgConf={summary.avgConf}
                    ready={summary.readyCount}
                  />
                )}

                <AnimatePresence>
                  {rules.map((rule, i) => (
                    <RuleCard
                      key={`${rule.procedure}-${i}`}
                      rule={rule}
                      index={i}
                      sourceDocName={sourceDocName}
                    />
                  ))}
                </AnimatePresence>
              </>
            )}
          </div>
        </div>

        {/* ── Bottom: Summary + Actions ── */}
        {rules.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-7 space-y-5">
            <SummaryPanel rules={rules} />

            <div className="flex gap-4 items-center">
              <Link href="/claims" className="flex-1">
                <button
                  className="w-full flex items-center justify-center gap-3 py-3.5 px-6 rounded-xl text-gray-900 text-[15px] font-bold transition-all group"
                  style={{ background: "linear-gradient(135deg, #d1d5db, #6b7280)", boxShadow: "0 8px 32px rgba(0,0,0,0.12)" }}
                >
                  <ShieldCheck className="w-5 h-5" />
                  Send to Claims Validator
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </Link>
              {!isDemo && (
                <button
                  onClick={downloadAll}
                  className="flex items-center gap-2.5 py-3.5 px-5 rounded-xl border border-black/10 hover:border-black/18 hover:bg-black/4 text-slate-600 text-[15px] font-semibold transition-all"
                >
                  <Download className="w-4 h-4" />
                  Export JSON
                </button>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}
