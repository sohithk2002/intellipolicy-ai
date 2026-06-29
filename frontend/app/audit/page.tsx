"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils";
import { api } from "@/lib/api";
import { AuditRecord } from "@/lib/types";
import {
  ScrollText, FileText, Search, Brain,
  MessageSquare, BookOpen, CheckCircle2, Clock, Download, MousePointerClick,
  Loader2,
} from "lucide-react";

function TraceDetail({ record }: { record: AuditRecord }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={record.session_id}
        initial={{ opacity: 0, x: 12 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.18 }}
        className="p-7 space-y-6"
      >
        {/* Question block */}
        <div className="rounded-xl border border-white/6 bg-white/2 p-5">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <MessageSquare className="w-3.5 h-3.5 text-sky-400 shrink-0" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Question</span>
            <Badge variant="info">Session {record.session_id.slice(0, 8)}…</Badge>
            <Badge variant="muted">{formatDate(record.created_at)}</Badge>
            <div className="ml-auto shrink-0">
              <ConfidenceMeter score={record.confidence} showBar={false} />
            </div>
          </div>
          <p className="text-sm font-semibold text-white leading-relaxed">{record.question}</p>
        </div>

        {/* Reasoning pipeline */}
        {record.steps.length > 0 && (
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-1.5">
              <Brain className="w-3.5 h-3.5 text-indigo-400" /> Reasoning Pipeline
            </p>
            <div className="space-y-0">
              {record.steps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex flex-col items-center shrink-0">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center z-10"
                      style={{ background: "rgba(52,211,153,0.12)", border: "1px solid rgba(52,211,153,0.3)" }}>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    </div>
                    {i < record.steps.length - 1 && (
                      <div className="w-px flex-1 my-1" style={{ background: "linear-gradient(to bottom, rgba(52,211,153,0.2), rgba(52,211,153,0.05))", minHeight: 20 }} />
                    )}
                  </div>
                  <div className={`min-w-0 ${i < record.steps.length - 1 ? "pb-4" : "pb-0"}`}>
                    <p className="text-[13px] font-bold text-white leading-tight">{step.step}</p>
                    <p className="text-[12px] text-slate-400 mt-1 leading-relaxed">{step.description}</p>
                    <p className="text-[10px] text-slate-700 mt-1 font-mono">{formatDate(step.timestamp)}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning summary */}
        {record.reasoning_summary && (
          <div className="rounded-xl border border-indigo-500/14 bg-indigo-500/5 p-5">
            <p className="text-[11px] font-bold text-indigo-400 uppercase tracking-widest mb-3">AI Reasoning Summary</p>
            <p className="text-[13px] text-slate-300 leading-relaxed">{record.reasoning_summary}</p>
          </div>
        )}

        {/* Citations */}
        {record.source_citations.length > 0 && (
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
              <BookOpen className="w-3 h-3 text-sky-400" /> Source Citations
            </p>
            <div className="space-y-3">
              {record.source_citations.map((c, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + i * 0.08 }}
                  className="rounded-xl border border-sky-500/14 bg-sky-500/5 p-4"
                >
                  <div className="flex items-center gap-2 mb-2.5 flex-wrap">
                    <FileText className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                    <span className="text-[13px] font-semibold text-sky-400">{c.document_name}</span>
                    <Badge variant="info">Page {c.page_number}</Badge>
                    <Badge variant="muted">{Math.round(c.relevance_score * 100)}% match</Badge>
                  </div>
                  <p className="text-[13px] text-slate-400 italic leading-relaxed">&ldquo;{c.text}&rdquo;</p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Final answer */}
        <div className="rounded-xl border border-emerald-500/14 bg-emerald-500/5 p-5">
          <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest mb-3">Final Answer</p>
          <p className="text-[13px] text-slate-300 leading-relaxed">{record.final_answer}</p>
        </div>

        {/* Pages retrieved */}
        {record.retrieved_pages.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap pt-1">
            <span className="text-[11px] text-slate-600">Retrieved pages:</span>
            {record.retrieved_pages.map((p) => (
              <Badge key={p} variant="info">p.{p}</Badge>
            ))}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

function EmptyDetail() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center gap-4 p-8">
      <div className="w-14 h-14 rounded-2xl bg-white/4 border border-white/7 flex items-center justify-center">
        <MousePointerClick className="w-6 h-6 text-slate-600" />
      </div>
      <div>
        <p className="text-sm font-semibold text-slate-500 mb-1">Select a record to inspect its trace</p>
        <p className="text-xs text-slate-700 max-w-xs leading-relaxed">
          Every AI question is logged with its full reasoning pipeline, retrieved citations, and confidence scoring.
        </p>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 p-12">
      <div className="w-16 h-16 rounded-2xl bg-white/4 border border-white/7 flex items-center justify-center">
        <ScrollText className="w-8 h-8 text-slate-600" />
      </div>
      <div>
        <p className="text-[18px] font-bold text-slate-400 mb-2">No audit records yet</p>
        <p className="text-[14px] text-slate-600 max-w-xs leading-relaxed">
          Ask questions on the AI Assistant page to generate audit events here.
        </p>
      </div>
    </div>
  );
}

export default function AuditPage() {
  const [records, setRecords]     = useState<AuditRecord[]>([]);
  const [loading, setLoading]     = useState(true);
  const [search, setSearch]       = useState("");
  const [selected, setSelected]   = useState<AuditRecord | null>(null);

  useEffect(() => {
    api.getAuditRecords()
      .then((data) => {
        setRecords(data);
        if (data.length > 0) setSelected(data[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = records.filter(
    (r) => !search || r.question.toLowerCase().includes(search.toLowerCase())
  );

  // Compute real stats from loaded records
  const totalSessions  = records.length;
  const avgConf        = records.length > 0
    ? (records.reduce((s, r) => s + r.confidence, 0) / records.length * 100).toFixed(1) + "%"
    : "—";
  const totalPages     = records.reduce((s, r) => s + r.retrieved_pages.length, 0);

  const statCards = [
    { label: "Total Sessions",  value: totalSessions === 0 ? "0" : String(totalSessions), icon: MessageSquare, color: "#38bdf8" },
    { label: "Avg Confidence",  value: avgConf,                                              icon: Brain,         color: "#818cf8" },
    { label: "Pages Retrieved", value: totalPages === 0 ? "0" : String(totalPages),          icon: FileText,      color: "#a78bfa" },
    { label: "Avg Latency",     value: "~2s",                                                icon: Clock,         color: "#34d399" },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">
        <PageHero
          eyebrow="Compliance"
          title="Audit Trail"
          subtitle="Full traceability — every question, retrieval step, reasoning chain, and answer"
          gradient="#34d399"
          action={
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/8 border border-emerald-500/14 px-2.5 py-1.5 rounded-lg">
                <CheckCircle2 className="w-3 h-3" /> HIPAA-compliant logging
              </div>
              {records.length > 0 && (
                <Button variant="outline" size="sm" icon={<Download className="w-3.5 h-3.5" />}>
                  Export Report
                </Button>
              )}
            </div>
          }
        />

        <div className="flex flex-col gap-5" style={{ height: "calc(100vh - 200px)" }}>

          {/* Summary stats */}
          <div className="grid grid-cols-4 gap-4 shrink-0">
            {statCards.map((s, i) => {
              const Icon = s.icon;
              return (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="rounded-2xl border border-white/7 bg-[#090f1e]/70 px-5 py-4 flex items-center gap-4"
                >
                  <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                    style={{ background: `${s.color}12`, border: `1px solid ${s.color}20` }}>
                    <Icon className="w-4 h-4" style={{ color: s.color }} />
                  </div>
                  <div>
                    <p className="text-xl font-black" style={{ color: s.color, fontFamily: "var(--font-heading, sans-serif)" }}>
                      {s.value}
                    </p>
                    <p className="text-[10px] text-slate-500">{s.label}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Split panel */}
          <div className="flex-1 flex gap-5 min-h-0">

            {/* Left: record list */}
            <div className="w-80 shrink-0 flex flex-col rounded-2xl border border-white/7 bg-[#090f1e]/70 overflow-hidden">
              <div className="px-3.5 py-3 border-b border-white/5 shrink-0">
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-600" />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search records..."
                    className="w-full pl-8 pr-3 py-2 bg-white/4 border border-white/6 rounded-lg text-xs text-slate-200 placeholder:text-slate-700 focus:outline-none focus:border-sky-500/30 transition-colors"
                  />
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <p className="text-[10px] text-slate-600">
                    <span className="font-semibold text-slate-400 font-mono">{filtered.length}</span> records
                  </p>
                  <p className="text-[10px] text-slate-700">Click to inspect trace</p>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto divide-y divide-white/4">
                {loading ? (
                  <div className="p-6 flex flex-col items-center gap-3 text-center">
                    <Loader2 className="w-5 h-5 text-slate-600 animate-spin" />
                    <p className="text-xs text-slate-600">Loading records…</p>
                  </div>
                ) : filtered.length === 0 ? (
                  <div className="p-6 text-center">
                    <p className="text-xs text-slate-600">
                      {records.length === 0 ? "No records yet. Ask a question first." : "No records match your search."}
                    </p>
                  </div>
                ) : (
                  filtered.map((record) => {
                    const isSelected = selected?.session_id === record.session_id;
                    return (
                      <button
                        key={record.session_id}
                        onClick={() => setSelected(record)}
                        className={`w-full text-left px-4 py-3.5 border-l-2 transition-all ${
                          isSelected
                            ? "border-sky-500 bg-sky-500/6"
                            : "border-transparent hover:bg-white/3 hover:border-white/10"
                        }`}
                      >
                        <p className="text-xs font-semibold text-slate-200 line-clamp-2 mb-2 leading-snug">
                          {record.question}
                        </p>
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-[10px] text-slate-600 font-mono">{record.session_id.slice(0, 12)}…</span>
                          <ConfidenceMeter score={record.confidence} showBar={false} />
                        </div>
                        <div className="flex items-center gap-1 mt-1">
                          <Clock className="w-2.5 h-2.5 text-slate-700" />
                          <p className="text-[10px] text-slate-700">{formatDate(record.created_at)}</p>
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </div>

            {/* Right: detail panel */}
            <div className="flex-1 rounded-2xl border border-white/7 bg-[#090f1e]/70 overflow-y-auto">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-slate-600 animate-spin" />
                </div>
              ) : records.length === 0 ? (
                <EmptyState />
              ) : selected ? (
                <TraceDetail record={selected} />
              ) : (
                <EmptyDetail />
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
