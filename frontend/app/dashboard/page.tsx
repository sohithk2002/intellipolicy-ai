"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { GlassCard } from "@/components/ui/Card";
import {
  FileText, MessageSquare, GitCompare, FileCode2, TrendingUp,
  Clock, Activity, ArrowUpRight, CheckCircle2, AlertCircle,
  Zap, Brain, ArrowRight, ShieldCheck, ScrollText, BarChart2,
  AlertTriangle, Key, ChevronDown, Loader2, Download,
} from "lucide-react";
import Link from "next/link";
import { api, SampleDocument } from "@/lib/api";
import { AuditRecord, ClaimAuditRecord } from "@/lib/types";
import { useDocumentContext } from "@/lib/DocumentContext";

const STAT_META = [
  { label: "Documents Processed", key: "documents_uploaded",    icon: FileText,      from: "#0ea5e9", to: "#6366f1", glow: "rgba(14,165,233,0.10)"  },
  { label: "Questions Answered",  key: "questions_answered",     icon: MessageSquare, from: "#6366f1", to: "#8b5cf6", glow: "rgba(99,102,241,0.10)"  },
  { label: "Policy Comparisons",  key: "policy_changes_detected",icon: GitCompare,    from: "#8b5cf6", to: "#a855f7", glow: "rgba(139,92,246,0.10)"  },
  { label: "Rules Extracted",     key: "rules_extracted",        icon: FileCode2,     from: "#10b981", to: "#14b8a6", glow: "rgba(16,185,129,0.10)"  },
  { label: "Claims Validated",    key: "claims_validated",       icon: ShieldCheck,   from: "#f59e0b", to: "#f97316", glow: "rgba(245,158,11,0.10)"  },
  { label: "Audit Events",        key: "questions_answered",     icon: ScrollText,    from: "#ec4899", to: "#f43f5e", glow: "rgba(236,72,153,0.10)"  },
] as const;

const quickActions = [
  { href: "/upload",    label: "Upload Policy",    desc: "Add a new PDF document",    icon: FileText,      color: "#38bdf8" },
  { href: "/assistant", label: "Ask a Question",   desc: "Query your policy library",  icon: MessageSquare, color: "#818cf8" },
  { href: "/compare",   label: "Compare Policies", desc: "Detect version changes",     icon: GitCompare,    color: "#a78bfa" },
  { href: "/claims",    label: "Validate Claim",   desc: "Check CPT + diagnosis code", icon: Activity,      color: "#fbbf24" },
];

function computeAgents(stats: ApiStats | null) {
  const docs    = (stats?.documents_uploaded    ?? 0) > 0;
  const queries = (stats?.questions_answered    ?? 0) > 0;
  const compare = (stats?.policy_changes_detected ?? 0) > 0;
  const rules   = (stats?.rules_extracted       ?? 0) > 0;
  const claims  = (stats?.claims_validated      ?? 0) > 0;
  const active  = "#34d399";
  const standby = "#fbbf24";
  return [
    { name: "Intake Agent",     status: docs    ? "Active" : "Standby", accent: docs    ? active : standby },
    { name: "Retrieval Agent",  status: queries ? "Active" : "Standby", accent: queries ? active : standby },
    { name: "Policy QA Agent",  status: queries ? "Active" : "Standby", accent: queries ? active : standby },
    { name: "Comparison Agent", status: compare ? "Active" : "Standby", accent: compare ? active : standby },
    { name: "Rule Agent",       status: (rules || claims) ? "Active" : "Standby", accent: (rules || claims) ? active : standby },
  ];
}

const riskAccent: Record<string, { border: string; bg: string; icon: string }> = {
  high:   { border: "#f87171", bg: "rgba(248,113,113,0.05)", icon: "#f87171" },
  medium: { border: "#fbbf24", bg: "rgba(251,191,36,0.05)",  icon: "#fbbf24" },
  low:    { border: "#34d399", bg: "rgba(52,211,153,0.05)",  icon: "#34d399" },
};

type RiskLevel = "high" | "medium" | "low";
type RiskInsight = { label: string; risk: RiskLevel; doc: string; Icon: React.ElementType };

function computeRiskInsights(
  qaRecords: AuditRecord[],
  claimRecords: ClaimAuditRecord[],
  stats: ApiStats | null,
): RiskInsight[] {
  const insights: RiskInsight[] = [];

  // Low-confidence QA answers → risky
  for (const r of qaRecords.filter((r) => r.confidence > 0 && r.confidence < 0.6).slice(0, 2)) {
    const q = r.question.length > 55 ? r.question.slice(0, 55) + "…" : r.question;
    insights.push({
      label: `Low confidence answer: "${q}"`,
      risk: r.confidence < 0.3 ? "high" : "medium",
      doc: `Confidence: ${(r.confidence * 100).toFixed(0)}% · ${timeAgo(r.created_at)}`,
      Icon: AlertTriangle,
    });
  }

  // Claims with no rule matched → need attention
  for (const c of claimRecords.filter((r) => !r.rule_matched).slice(0, 2)) {
    const proc = c.procedure.length > 45 ? c.procedure.slice(0, 45) + "…" : c.procedure;
    insights.push({
      label: `Unmatched claim: CPT ${c.cpt_code} — ${proc}`,
      risk: "high",
      doc: `${c.plan_type} · ${c.decision} · ${timeAgo(c.created_at)}`,
      Icon: AlertTriangle,
    });
  }

  // Positive signals when things are working well
  if (insights.length < 2 && (stats?.documents_uploaded ?? 0) > 0) {
    insights.push({
      label: `${stats!.documents_uploaded} document${stats!.documents_uploaded > 1 ? "s" : ""} indexed and searchable`,
      risk: "low",
      doc: `${stats?.rules_extracted ?? 0} rules extracted`,
      Icon: CheckCircle2,
    });
  }
  if (insights.length < 3 && (stats?.claims_validated ?? 0) > 0) {
    const avgConf = ((stats?.avg_confidence ?? 0) * 100).toFixed(0);
    insights.push({
      label: `${stats!.claims_validated} claim${stats!.claims_validated > 1 ? "s" : ""} validated successfully`,
      risk: "low",
      doc: `Avg confidence: ${avgConf}%`,
      Icon: CheckCircle2,
    });
  }

  // Fallback: nothing has happened yet
  if (insights.length === 0) {
    insights.push({
      label: "No policy documents indexed yet",
      risk: "high",
      doc: "Upload a document to begin analysis",
      Icon: AlertTriangle,
    });
    insights.push({
      label: "No claims validated yet",
      risk: "medium",
      doc: "Run a claim validation to see risk signals",
      Icon: TrendingUp,
    });
  }

  return insights.slice(0, 4);
}

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function computeActivityData(
  qaRecords: AuditRecord[],
  claimRecords: ClaimAuditRecord[],
): { day: string; queries: number; claims: number }[] {
  const today = new Date();
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (6 - i));
    const prefix = d.toISOString().slice(0, 10); // "YYYY-MM-DD"
    return {
      day: DAY_NAMES[d.getDay()],
      queries: qaRecords.filter((r) => r.created_at.startsWith(prefix)).length,
      claims:  claimRecords.filter((r) => r.created_at.startsWith(prefix)).length,
    };
  });
}

const PROVIDERS = [
  { value: "anthropic", label: "Anthropic (Claude)", placeholder: "sk-ant-..." },
  { value: "openai",    label: "OpenAI (GPT-4o)",    placeholder: "sk-..."     },
  { value: "gemini",    label: "Google Gemini",       placeholder: "AIza..."    },
];

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1)  return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)  return `${hrs} hr ago`;
  return `${Math.floor(hrs / 24)} days ago`;
}

function ActivityChart({ data }: { data: { day: string; queries: number; claims: number }[] }) {
  const max = Math.max(...data.flatMap((d) => [d.queries, d.claims]), 1);
  const hasData = data.some((d) => d.queries > 0 || d.claims > 0);
  return (
    <div>
      {!hasData && (
        <p className="text-[13px] text-slate-600 text-center mb-4">
          No activity yet — ask questions or validate claims to see data here.
        </p>
      )}
      <div className="flex items-end gap-3" style={{ height: 144 }}>
        {data.map((d, i) => (
          <motion.div
            key={d.day}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 + i * 0.04 }}
            className="flex-1 flex flex-col gap-1 items-stretch"
            style={{ height: "100%" }}
          >
            <div className="flex-1 flex items-end gap-1">
              <motion.div
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: 0.45 + i * 0.06, duration: 0.5, ease: "easeOut" }}
                className="flex-1 rounded-t origin-bottom"
                style={{ height: `${(d.queries / max) * 100}%`, background: "rgba(56,189,248,0.6)", borderRadius: "4px 4px 0 0" }}
              />
              <motion.div
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: 0.5 + i * 0.06, duration: 0.5, ease: "easeOut" }}
                className="flex-1 rounded-t origin-bottom"
                style={{ height: `${(d.claims / max) * 100}%`, background: "rgba(129,140,248,0.55)", borderRadius: "4px 4px 0 0" }}
              />
            </div>
          </motion.div>
        ))}
      </div>
      <div className="flex gap-3 mt-3">
        {data.map((d) => (
          <div key={d.day} className="flex-1 text-center">
            <p className="text-[11px] text-slate-600 font-medium">{d.day}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function CardTitle({ icon: Icon, title, color = "text-sky-400", action }: {
  icon: React.ElementType;
  title: string;
  color?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between mb-7">
      <div className="flex items-center gap-3">
        <Icon className={`w-5 h-5 ${color}`} />
        <h2 className="text-[18px] font-bold text-white" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
          {title}
        </h2>
      </div>
      {action}
    </div>
  );
}

type ApiStats = {
  documents_uploaded: number;
  questions_answered: number;
  policy_changes_detected: number;
  rules_extracted: number;
  claims_validated: number;
  avg_confidence: number;
};

// ── API Key Config Panel ───────────────────────────────────────────────────────
function ApiKeyPanel() {
  const [provider, setProvider] = useState("anthropic");
  const [apiKey, setApiKey]     = useState("");
  const [saving, setSaving]     = useState(false);
  const [status, setStatus]     = useState<{ ok: boolean; msg: string } | null>(null);
  const [activeProvider, setActiveProvider] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    api.getActiveProvider().then((r) => {
      if (r.provider) setActiveProvider(r.provider);
    }).catch(() => {}).finally(() => setChecking(false));
  }, []);

  const handleSave = async () => {
    if (!apiKey.trim()) return;
    setSaving(true);
    setStatus(null);
    try {
      const res = await api.setApiKey(provider, apiKey);
      setStatus({ ok: true, msg: res.message });
      setActiveProvider(provider);
      setApiKey("");
    } catch (err) {
      setStatus({ ok: false, msg: err instanceof Error ? err.message : "Failed to save key" });
    } finally {
      setSaving(false);
    }
  };

  const selectedProvider = PROVIDERS.find((p) => p.value === provider)!;

  return (
    <GlassCard style={{ padding: "32px 32px" }}>
      <CardTitle
        icon={Key}
        title="LLM API Configuration"
        color="text-violet-400"
        action={
          checking ? (
            <div className="flex items-center gap-2 text-[12px] text-slate-500 bg-white/4 border border-white/8 px-3 py-1.5 rounded-lg font-semibold">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Checking…
            </div>
          ) : activeProvider ? (
            <div className="flex items-center gap-2 text-[12px] text-emerald-400 bg-emerald-500/8 border border-emerald-500/15 px-3 py-1.5 rounded-lg font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {PROVIDERS.find((p) => p.value === activeProvider)?.label || activeProvider} active
            </div>
          ) : (
            <div className="flex items-center gap-2 text-[12px] text-amber-400 bg-amber-500/8 border border-amber-500/15 px-3 py-1.5 rounded-lg font-semibold">
              <AlertCircle className="w-3.5 h-3.5" />
              No key configured
            </div>
          )
        }
      />

      <p className="text-[14px] text-slate-500 mb-5 leading-relaxed">
        Configure an LLM provider for AI-powered answers, rule extraction, and claim validation.
        Without a key, the system uses extractive fallback (regex-based) for all AI features.
      </p>

      <div className="space-y-4">
        {/* Provider dropdown */}
        <div>
          <label className="block text-[12px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Provider</label>
          <div className="relative">
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full appearance-none bg-white/4 border border-white/10 rounded-xl px-4 py-3 text-[14px] text-slate-200 focus:outline-none focus:border-violet-500/40 transition-colors cursor-pointer pr-10"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value} style={{ background: "#0d1224" }}>
                  {p.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
          </div>
        </div>

        {/* API Key input */}
        <div>
          <label className="block text-[12px] font-semibold text-slate-400 uppercase tracking-wider mb-2">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={selectedProvider.placeholder}
            onKeyDown={(e) => e.key === "Enter" && handleSave()}
            className="w-full bg-white/4 border border-white/10 rounded-xl px-4 py-3 text-[14px] text-slate-200 placeholder:text-slate-700 focus:outline-none focus:border-violet-500/40 transition-colors font-mono"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving || !apiKey.trim()}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-[14px] font-semibold transition-all disabled:opacity-40"
          style={{
            background: "linear-gradient(135deg, rgba(139,92,246,0.25), rgba(99,102,241,0.25))",
            border: "1px solid rgba(139,92,246,0.35)",
            color: "#c4b5fd",
          }}
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
          {saving ? "Saving…" : "Save API Key"}
        </button>

        <AnimatePresence>
          {status && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex items-center gap-2.5 px-4 py-3 rounded-xl text-[13px] font-medium ${
                status.ok
                  ? "bg-emerald-500/8 border border-emerald-500/20 text-emerald-400"
                  : "bg-red-500/8 border border-red-500/20 text-red-400"
              }`}
            >
              {status.ok ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
              {status.msg}
            </motion.div>
          )}
        </AnimatePresence>

        <p className="text-[11px] text-slate-700 leading-relaxed">
          API keys are encrypted and persisted on the backend — they survive server restarts.
        </p>
      </div>
    </GlassCard>
  );
}

// ── Sample Documents Panel ────────────────────────────────────────────────────
function SampleDocumentsPanel({ onLoaded }: { onLoaded: () => void }) {
  const [docs, setDocs]             = useState<SampleDocument[]>([]);
  const [loading, setLoading]       = useState(true);
  const [loadingDoc, setLoadingDoc] = useState<string | null>(null);
  const [loaded, setLoaded]         = useState<Set<string>>(new Set());
  const [error, setError]           = useState<string | null>(null);

  useEffect(() => {
    api.getSampleDocuments().then(setDocs).catch(() => setError("Backend not reachable")).finally(() => setLoading(false));
  }, []);

  const handleLoad = async (filename: string) => {
    setLoadingDoc(filename);
    setError(null);
    try {
      await api.loadSampleDocument(filename);
      setLoaded((prev) => new Set([...prev, filename]));
      onLoaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample document");
    } finally {
      setLoadingDoc(null);
    }
  };

  return (
    <GlassCard style={{ padding: "32px 32px" }}>
      <CardTitle
        icon={Download}
        title="Sample Policy Documents"
        color="text-sky-400"
        action={
          <span className="text-[11px] text-sky-400/70 bg-sky-500/8 border border-sky-500/15 px-2 py-1 rounded-md font-semibold">
            No API key needed
          </span>
        }
      />

      <p className="text-[14px] text-slate-500 mb-5 leading-relaxed">
        Load one of these bundled healthcare policy PDFs to explore the platform without uploading your own documents.
        Works with or without an API key — extractive AI runs offline.
      </p>

      {error && (
        <div className="flex items-center gap-2.5 px-4 py-3 rounded-xl bg-red-500/8 border border-red-500/18 mb-4">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <p className="text-[13px] text-red-300">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center gap-3 py-6 justify-center">
          <Loader2 className="w-5 h-5 text-slate-600 animate-spin" />
          <p className="text-[14px] text-slate-600">Loading sample documents…</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {docs.map((doc) => {
            const isLoaded   = loaded.has(doc.filename);
            const isLoading  = loadingDoc === doc.filename;
            return (
              <div
                key={doc.filename}
                className="flex items-center gap-4 rounded-xl transition-all"
                style={{
                  padding: "14px 18px",
                  background: isLoaded ? "rgba(52,211,153,0.05)" : "rgba(255,255,255,0.03)",
                  border: isLoaded ? "1px solid rgba(52,211,153,0.2)" : "1px solid rgba(255,255,255,0.07)",
                }}
              >
                <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                  style={{ background: "rgba(14,165,233,0.1)", border: "1px solid rgba(14,165,233,0.2)" }}>
                  <FileText className="w-4 h-4 text-sky-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[14px] font-semibold text-slate-200 leading-snug truncate">{doc.label}</p>
                  <p className="text-[11px] text-slate-600 mt-0.5 font-mono">{doc.size_kb} KB</p>
                </div>
                {isLoaded ? (
                  <div className="flex items-center gap-1.5 text-[12px] text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-4 h-4" />
                    Indexed
                  </div>
                ) : (
                  <button
                    onClick={() => handleLoad(doc.filename)}
                    disabled={isLoading}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-[13px] font-semibold transition-all disabled:opacity-50"
                    style={{
                      background: "rgba(14,165,233,0.12)",
                      border: "1px solid rgba(14,165,233,0.25)",
                      color: "#38bdf8",
                    }}
                  >
                    {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                    {isLoading ? "Loading…" : "Load"}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </GlassCard>
  );
}

// ── Document Library Panel ────────────────────────────────────────────────────
function DocumentLibraryPanel() {
  const { documents, selectedDoc, setSelectedDoc } = useDocumentContext();

  const DOC_TYPE_LABEL: Record<string, string> = {
    policy:            "Policy Manual",
    provider_contract: "Provider Contract",
    billing_guideline: "Billing Guideline",
    cms_rule:          "CMS Rule",
  };

  return (
    <GlassCard style={{ padding: "32px 32px" }}>
      <CardTitle
        icon={FileText}
        title="Uploaded Documents"
        color="text-sky-400"
        action={
          <div className="flex items-center gap-3">
            <span className="text-[12px] text-slate-500 font-medium">
              {documents.length} {documents.length === 1 ? "document" : "documents"}
            </span>
            <Link
              href="/upload"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all"
              style={{
                background: "rgba(14,165,233,0.1)",
                border: "1px solid rgba(14,165,233,0.22)",
                color: "#38bdf8",
              }}
            >
              <ArrowUpRight className="w-3 h-3" />
              Upload New
            </Link>
          </div>
        }
      />

      {documents.length === 0 ? (
        <div className="py-10 text-center">
          <FileText className="w-10 h-10 text-slate-700 mx-auto mb-4" />
          <p className="text-[15px] font-semibold text-slate-500 mb-1">No documents yet</p>
          <p className="text-[13px] text-slate-700 mb-5">
            Upload a policy PDF or load a sample document to get started.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-[13px] font-semibold"
            style={{
              background: "rgba(14,165,233,0.12)",
              border: "1px solid rgba(14,165,233,0.25)",
              color: "#38bdf8",
            }}
          >
            <ArrowRight className="w-4 h-4" />
            Go to Upload
          </Link>
        </div>
      ) : (
        <div className="space-y-2.5">
          {documents.map((doc, i) => {
            const isActive = selectedDoc?.id === doc.id;
            const isReady  = doc.status === "ready";
            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="flex items-center gap-4 rounded-xl transition-all"
                style={{
                  padding: "14px 18px",
                  background: isActive
                    ? "rgba(14,165,233,0.07)"
                    : "rgba(255,255,255,0.025)",
                  border: isActive
                    ? "1px solid rgba(14,165,233,0.25)"
                    : "1px solid rgba(255,255,255,0.06)",
                }}
              >
                {/* Icon */}
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  style={{
                    background: isActive ? "rgba(14,165,233,0.15)" : "rgba(255,255,255,0.05)",
                    border: isActive ? "1px solid rgba(14,165,233,0.25)" : "1px solid rgba(255,255,255,0.08)",
                  }}
                >
                  <FileText className="w-4 h-4" style={{ color: isActive ? "#38bdf8" : "#64748b" }} />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-[14px] font-semibold text-slate-200 truncate leading-snug">
                    {doc.filename}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-[11px] text-slate-500">
                      {DOC_TYPE_LABEL[doc.document_type] ?? doc.document_type}
                    </span>
                    {doc.page_count > 0 && (
                      <span className="text-[11px] text-slate-600">
                        {doc.page_count} pages
                      </span>
                    )}
                    {doc.chunk_count != null && doc.chunk_count > 0 && (
                      <span className="text-[11px] text-slate-600">
                        {doc.chunk_count} chunks
                      </span>
                    )}
                  </div>
                </div>

                {/* Status badge */}
                {isReady ? (
                  <span
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-md shrink-0"
                    style={{
                      background: "rgba(52,211,153,0.1)",
                      border: "1px solid rgba(52,211,153,0.2)",
                      color: "#34d399",
                    }}
                  >
                    Ready
                  </span>
                ) : (
                  <span
                    className="text-[11px] font-semibold px-2.5 py-1 rounded-md shrink-0"
                    style={{
                      background: "rgba(251,191,36,0.1)",
                      border: "1px solid rgba(251,191,36,0.2)",
                      color: "#fbbf24",
                    }}
                  >
                    {doc.status}
                  </span>
                )}

                {/* Active / Use button */}
                {isActive ? (
                  <div
                    className="flex items-center gap-1.5 text-[12px] font-semibold shrink-0"
                    style={{ color: "#38bdf8" }}
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Active
                  </div>
                ) : (
                  <button
                    onClick={() => setSelectedDoc(doc)}
                    disabled={!isReady}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all disabled:opacity-40 shrink-0"
                    style={{
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      color: "#94a3b8",
                    }}
                  >
                    Use
                  </button>
                )}
              </motion.div>
            );
          })}
        </div>
      )}
    </GlassCard>
  );
}

export default function DashboardPage() {
  const [apiStats, setApiStats]           = useState<ApiStats | null>(null);
  const [auditRecords, setAuditRecords]   = useState<AuditRecord[]>([]);
  const [claimRecords, setClaimRecords]   = useState<ClaimAuditRecord[]>([]);

  const refreshStats = () => {
    api.getDashboardStats().then(setApiStats).catch(() => {});
    api.getAuditRecords().then(setAuditRecords).catch(() => {});
    api.getClaimAuditRecords().then(setClaimRecords).catch(() => {});
  };

  useEffect(() => {
    refreshStats();
    const interval = setInterval(refreshStats, 30_000); // refresh every 30 s
    return () => clearInterval(interval);
  }, []);

  const stats = STAT_META.map((m) => ({
    ...m,
    value: apiStats !== null ? String(apiStats[m.key as keyof ApiStats] ?? 0) : "—",
    delta: apiStats !== null ? (Number(apiStats[m.key as keyof ApiStats]) === 0 ? "No data yet" : "From backend") : "Loading...",
  }));

  const activity = auditRecords.slice(0, 6).map((r) => ({
    msg: r.question.length > 72 ? r.question.slice(0, 72) + "…" : r.question,
    time: timeAgo(r.created_at),
    icon: MessageSquare,
    ok: r.confidence >= 0.7,
  }));

  const agents       = computeAgents(apiStats);
  const riskInsights = computeRiskInsights(auditRecords, claimRecords, apiStats);
  const chartData    = computeActivityData(auditRecords, claimRecords);

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-12 space-y-12">

        <PageHero
          eyebrow="Overview"
          title="Claims Intelligence Dashboard"
          subtitle="Monitor policy ingestion, AI decisions, rule extraction, and audit activity across your healthcare intelligence platform."
          gradient="#0ea5e9"
          action={
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[13px] font-semibold">
              <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-glow" />
              All systems operational
            </div>
          }
        />

        {/* ── Metric Cards ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
          {stats.map((s, i) => {
            const Icon = s.icon;
            return (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ y: -3, borderColor: "rgba(255,255,255,0.13)" }}
                className="relative rounded-[20px] overflow-hidden group cursor-pointer"
                style={{
                  padding: "28px 24px",
                  background: `radial-gradient(140% 100% at 50% 0%, ${s.from}14 0%, rgba(9,15,30,0.88) 65%)`,
                  border: "1px solid rgba(255,255,255,0.08)",
                  boxShadow: `0 1px 3px rgba(0,0,0,0.25), 0 0 32px ${s.glow}`,
                  transition: "border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease",
                }}
              >
                <div className="flex items-start justify-between mb-5">
                  <div
                    className="w-11 h-11 rounded-xl flex items-center justify-center"
                    style={{ background: `${s.from}18`, border: `1px solid ${s.from}28`, boxShadow: `0 0 16px ${s.from}15` }}
                  >
                    <Icon className="w-5 h-5" style={{ color: s.from }} />
                  </div>
                  <ArrowUpRight className="w-4 h-4 text-slate-700 group-hover:text-slate-400 transition-colors mt-0.5" />
                </div>
                <p
                  className="text-[32px] font-black text-white leading-none tracking-tight"
                  style={{ fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)" }}
                >
                  {s.value}
                </p>
                <p className="text-[12px] text-slate-400 mt-2.5 font-medium leading-snug">{s.label}</p>
                <p className="text-[11px] mt-2 font-semibold truncate" style={{ color: s.from }}>{s.delta}</p>
              </motion.div>
            );
          })}
        </div>

        {/* ── Uploaded Documents Library ────────────────────────────────────── */}
        <DocumentLibraryPanel />

        {/* ── API Key + Sample Documents ────────────────────────────────────── */}
        <div className="grid lg:grid-cols-2 gap-8">
          <ApiKeyPanel />
          <SampleDocumentsPanel onLoaded={refreshStats} />
        </div>

        {/* ── Middle Row: Quick Actions + Activity Feed ─────────────────────── */}
        <div className="grid lg:grid-cols-3 gap-8">

          {/* Quick Actions */}
          <GlassCard style={{ padding: "32px 32px" }}>
            <CardTitle icon={Zap} title="Quick Actions" />
            <div className="space-y-3">
              {quickActions.map((a) => {
                const Icon = a.icon;
                return (
                  <Link key={a.href} href={a.href}>
                    <motion.div
                      whileHover={{ x: 3 }}
                      transition={{ duration: 0.15 }}
                      className="flex items-center gap-4 rounded-xl cursor-pointer group"
                      style={{
                        padding: "16px 18px",
                        border: "1px solid rgba(255,255,255,0.05)",
                        transition: "background 0.15s ease, border-color 0.15s ease",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = `${a.color}06`;
                        e.currentTarget.style.borderColor = `${a.color}20`;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "transparent";
                        e.currentTarget.style.borderColor = "rgba(255,255,255,0.05)";
                      }}
                    >
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                        style={{ background: `${a.color}12`, border: `1px solid ${a.color}25` }}
                      >
                        <Icon className="w-4 h-4" style={{ color: a.color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[15px] font-semibold text-slate-200 group-hover:text-white transition-colors leading-tight">
                          {a.label}
                        </p>
                        <p className="text-[13px] text-slate-500 mt-1">{a.desc}</p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-700 group-hover:text-slate-400 transition-colors shrink-0" />
                    </motion.div>
                  </Link>
                );
              })}
            </div>
          </GlassCard>

          {/* Recent Activity */}
          <GlassCard style={{ padding: "32px 32px" }} className="lg:col-span-2">
            <CardTitle
              icon={Activity}
              title="Recent Activity"
              action={
                <div className="flex items-center gap-2 text-[12px] text-slate-500 bg-white/4 px-3 py-1.5 rounded-lg border border-white/6">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-glow" />
                  Live
                </div>
              }
            />
            {activity.length === 0 ? (
              <div className="py-10 text-center">
                <MessageSquare className="w-8 h-8 text-slate-700 mx-auto mb-3" />
                <p className="text-[14px] text-slate-600">No activity yet.</p>
                <p className="text-[13px] text-slate-700 mt-1">
                  Upload a document and ask questions to see activity here.
                </p>
              </div>
            ) : (
              <div className="divide-y" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
                {activity.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center gap-4"
                      style={{
                        padding: i === 0 ? "0 0 24px" : i === activity.length - 1 ? "24px 0 0" : "24px 0",
                      }}
                    >
                      <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                        style={{
                          background: item.ok ? "rgba(52,211,153,0.1)" : "rgba(251,191,36,0.1)",
                          border: item.ok ? "1px solid rgba(52,211,153,0.2)" : "1px solid rgba(251,191,36,0.2)",
                          color: item.ok ? "#34d399" : "#fbbf24",
                        }}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[14px] text-slate-300 leading-snug">{item.msg}</p>
                        <div className="flex items-center gap-1.5 mt-1.5">
                          <Clock className="w-3 h-3 text-slate-700" />
                          <span className="text-[12px] text-slate-600">{item.time}</span>
                        </div>
                      </div>
                      {item.ok
                        ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        : <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                      }
                    </motion.div>
                  );
                })}
              </div>
            )}
          </GlassCard>
        </div>

        {/* ── Activity Chart ────────────────────────────────────────────────── */}
        <GlassCard style={{ padding: "32px 32px" }}>
          <CardTitle
            icon={BarChart2}
            title="AI Activity This Week"
            action={
              <div className="flex items-center gap-5 text-[13px] text-slate-500">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded inline-block" style={{ background: "rgba(56,189,248,0.6)" }} />
                  Policy Queries
                </span>
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded inline-block" style={{ background: "rgba(129,140,248,0.55)" }} />
                  Claim Validations
                </span>
              </div>
            }
          />
          <ActivityChart data={chartData} />
        </GlassCard>

        {/* ── Bottom Row: AI Agent Status + Risk Insights ───────────────────── */}
        <div className="grid lg:grid-cols-5 gap-8">

          {/* AI Agent Status */}
          <GlassCard style={{ padding: "32px 32px" }} className="lg:col-span-3">
            <CardTitle
              icon={Brain}
              title="AI Agent Status"
              color="text-indigo-400"
              action={
                <span className="text-[11px] text-slate-500 bg-white/4 px-3 py-1.5 rounded-lg border border-white/6 font-mono">
                  LangGraph Orchestration
                </span>
              }
            />
            <div className="grid grid-cols-5 gap-5">
              {agents.map((agent, i) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35 + i * 0.07 }}
                  className="flex flex-col rounded-2xl"
                  style={{
                    padding: "22px 16px",
                    background: `${agent.accent}07`,
                    border: `1px solid ${agent.accent}20`,
                    boxShadow: `0 0 20px ${agent.accent}08`,
                    transition: "border-color 0.2s ease",
                  }}
                  whileHover={{ y: -2 }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <motion.div
                      animate={{ opacity: agent.status === "Active" ? [1, 0.4, 1] : 1 }}
                      transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                      className="w-2 h-2 rounded-full"
                      style={{ background: agent.accent }}
                    />
                    <span
                      className="text-[9px] font-bold px-2 py-0.5 rounded-md"
                      style={{ background: `${agent.accent}18`, color: agent.accent, letterSpacing: "0.06em" }}
                    >
                      {agent.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-[12px] font-semibold text-slate-300 leading-tight">{agent.name}</p>
                </motion.div>
              ))}
            </div>
          </GlassCard>

          {/* Risk Insights */}
          <GlassCard style={{ padding: "32px 32px" }} className="lg:col-span-2">
            <CardTitle
              icon={TrendingUp}
              title="Risk Insights"
              color="text-amber-400"
              action={
                <span className="text-[10px] text-amber-500/70 bg-amber-500/8 border border-amber-500/15 px-2 py-1 rounded-md font-semibold">
                  Demo
                </span>
              }
            />
            <div className="space-y-4">
              {riskInsights.map((r, i) => {
                const ra = riskAccent[r.risk];
                const Icon = r.Icon;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: 8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.07 }}
                    className="rounded-xl"
                    style={{
                      padding: "16px 18px",
                      background: ra.bg,
                      borderTop: "1px solid rgba(255,255,255,0.05)",
                      borderRight: "1px solid rgba(255,255,255,0.05)",
                      borderBottom: "1px solid rgba(255,255,255,0.05)",
                      borderLeft: `3px solid ${ra.border}`,
                      borderRadius: 14,
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="w-3.5 h-3.5 shrink-0 mt-0.5" style={{ color: ra.icon }} />
                      <div className="min-w-0 flex-1">
                        <p className="text-[13px] text-slate-200 font-medium leading-snug">{r.label}</p>
                        <p className="text-[11px] text-slate-600 mt-1.5 font-mono">{r.doc}</p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </GlassCard>

        </div>
      </div>
    </DashboardLayout>
  );
}
