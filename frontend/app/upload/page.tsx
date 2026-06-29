"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import {
  Upload,
  FileText,
  CheckCircle2,
  X,
  Database,
  Cpu,
  Layers,
  Scissors,
  Clock,
  File,
  MessageSquare,
  FileCode2,
  GitCompare,
  ArrowRight,
  BrainCircuit,
  SplitSquareHorizontal,
  Boxes,
  HardDrive,
  Timer,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Document } from "@/lib/types";
import { useDocumentContext } from "@/lib/DocumentContext";

const DOC_TYPES = [
  { value: "policy",            label: "Policy Manual"        },
  { value: "provider_contract", label: "Provider Contract"    },
  { value: "billing_guideline", label: "Billing Guideline"    },
  { value: "cms_rule",          label: "CMS Rule PDF"         },
];

const PIPELINE_STEPS = [
  { label: "PDF Parse",   icon: File,         desc: "Extract raw text from PDF",   color: "#111827" },
  { label: "Chunking",    icon: Scissors,     desc: "Split into semantic chunks",   color: "#94a3b8" },
  { label: "Embeddings",  icon: Cpu,          desc: "BAAI/bge-small-en-v1.5",      color: "#94a3b8" },
  { label: "Vector DB",   icon: Database,     desc: "Store in PGVector",            color: "#34d399" },
  { label: "Ready",       icon: CheckCircle2, desc: "Indexed and searchable",       color: "#10b981" },
];

function buildStats(result: Document | null, elapsed: number | null) {
  const chunksPerPage =
    result?.chunk_count && result.page_count
      ? (result.chunk_count / result.page_count).toFixed(1)
      : null;

  const speedValue = elapsed != null
    ? `${elapsed.toFixed(1)} s`
    : "—";

  return [
    {
      label: "Embedding Model",
      value: "BAAI/bge",
      sub: "bge-small-en-v1.5",
      icon: BrainCircuit,
      color: "#94a3b8",
      glow: "rgba(0,0,0,0.09)",
      live: false,
    },
    {
      label: "Chunk Size",
      value: "150 tok",
      sub: "25 token overlap",
      icon: SplitSquareHorizontal,
      color: "#111827",
      glow: "rgba(0,0,0,0.09)",
      live: false,
    },
    {
      label: result ? "Pages Indexed" : "Vector Dims",
      value: result ? String(result.page_count) : "384",
      sub: result ? `${result.document_type}` : "normalized embeddings",
      icon: result ? FileText : Boxes,
      color: "#94a3b8",
      glow: "rgba(167,139,250,0.15)",
      live: !!result,
    },
    {
      label: result ? "Chunks Created" : "Storage",
      value: result ? String(result.chunk_count ?? "—") : "In-Mem",
      sub: result
        ? chunksPerPage ? `${chunksPerPage} per page` : "indexed chunks"
        : "cosine similarity",
      icon: result ? Boxes : HardDrive,
      color: "#34d399",
      glow: "rgba(52,211,153,0.15)",
      live: !!result,
    },
    {
      label: "Processing",
      value: elapsed != null ? speedValue : "~8 s",
      sub: elapsed != null ? "actual upload time" : "per PDF estimate",
      icon: Timer,
      color: "#fb923c",
      glow: "rgba(251,146,60,0.15)",
      live: elapsed != null,
    },
    {
      label: "Re-ranking",
      value: "70/30",
      sub: "semantic + keyword",
      icon: Zap,
      color: "#f472b6",
      glow: "rgba(244,114,182,0.15)",
      live: false,
    },
  ];
}

function PipelineViz({ active, step }: { active: boolean; step: number }) {
  return (
    <div className="mt-6 space-y-2">
      {PIPELINE_STEPS.map((s, i) => {
        const Icon  = s.icon;
        const done    = i < step;
        const current = i === step && active;
        return (
          <motion.div
            key={s.label}
            animate={current ? { scale: [1, 1.015, 1] } : {}}
            transition={{ repeat: Infinity, duration: 1.3 }}
            className="relative flex items-center gap-3 rounded-xl px-3 py-2.5 border transition-all duration-300"
            style={{
              borderColor: done
                ? "rgba(52,211,153,0.3)"
                : current
                ? `${s.color}40`
                : "rgba(0,0,0,0.03)",
              background: done
                ? "rgba(52,211,153,0.06)"
                : current
                ? `${s.color}0d`
                : "rgba(0,0,0,0.01)",
            }}
          >
            {/* Step number badge */}
            <div
              className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 transition-all duration-300"
              style={{
                background: done
                  ? "rgba(52,211,153,0.2)"
                  : current
                  ? `${s.color}25`
                  : "rgba(0,0,0,0.03)",
                color: done ? "#34d399" : current ? s.color : "#475569",
              }}
            >
              {done ? "✓" : i + 1}
            </div>

            {/* Icon */}
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-all duration-300"
              style={{
                background: done
                  ? "rgba(52,211,153,0.12)"
                  : current
                  ? `${s.color}18`
                  : "rgba(0,0,0,0.02)",
              }}
            >
              <Icon
                className="w-3.5 h-3.5 transition-colors duration-300"
                style={{ color: done ? "#34d399" : current ? s.color : "#475569" }}
              />
            </div>

            <div className="flex-1 min-w-0">
              <p
                className="text-xs font-semibold transition-colors duration-300"
                style={{ color: done ? "#34d399" : current ? s.color : "#94a3b8" }}
              >
                {s.label}
              </p>
              <p className="text-[10px] text-slate-600 font-mono truncate">{s.desc}</p>
            </div>

            {/* Active pulse ring */}
            {current && (
              <motion.div
                className="absolute right-3 w-1.5 h-1.5 rounded-full"
                style={{ background: s.color }}
                animate={{ opacity: [1, 0.2, 1] }}
                transition={{ repeat: Infinity, duration: 0.9 }}
              />
            )}
          </motion.div>
        );
      })}
    </div>
  );
}

export default function UploadPage() {
  const [dragging, setDragging]       = useState(false);
  const [file, setFile]               = useState<File | null>(null);
  const [docType, setDocType]         = useState("policy");
  const [uploading, setUploading]     = useState(false);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [documents, setDocuments]     = useState<Document[]>([]);
  const [result, setResult]           = useState<Document | null>(null);
  const [error, setError]             = useState("");
  const [elapsedSec, setElapsedSec]   = useState<number | null>(null);
  const uploadStartRef                = useRef<number | null>(null);
  const timerRef                      = useRef<ReturnType<typeof setInterval> | null>(null);
  const { setSelectedDoc, refreshDocs } = useDocumentContext();

  // Live upload timer
  useEffect(() => {
    if (uploading) {
      uploadStartRef.current = Date.now();
      timerRef.current = setInterval(() => {
        setElapsedSec((Date.now() - (uploadStartRef.current ?? Date.now())) / 1000);
      }, 100);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [uploading]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f?.type === "application/pdf") setFile(f);
  }, []);

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f?.type === "application/pdf") setFile(f);
  };

  const simulatePipeline = async () => {
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      setPipelineStep(i);
      await new Promise((r) => setTimeout(r, 900));
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setElapsedSec(null);
    setPipelineStep(0);
    const t0 = Date.now();
    try {
      const [doc] = await Promise.all([
        api.uploadDocument(file, docType),
        simulatePipeline(),
      ]);
      setElapsedSec((Date.now() - t0) / 1000);
      setResult(doc);
      setDocuments((prev) => [doc, ...prev]);
      setSelectedDoc(doc);
      refreshDocs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Check that the backend is running on port 8000.");
      setPipelineStep(-1);
      setElapsedSec(null);
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResult(null);
    setPipelineStep(-1);
    setError("");
    setElapsedSec(null);
  };

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">
        <PageHero
          eyebrow="Ingestion Pipeline"
          title="Upload Documents"
          subtitle="Ingest healthcare policies, contracts, and billing guides into the vector store for AI-powered retrieval."
          gradient="#d1d5db"
        />

        <div className="grid lg:grid-cols-5 gap-7">

          {/* ── Upload Card ── */}
          <div className="lg:col-span-3 rounded-2xl border border-black/7 bg-white p-8">
            <h2 className="text-base font-bold text-gray-900 mb-1" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
              Upload Policy PDF
            </h2>
            <p className="text-sm text-slate-500 mb-5">Supports policy manuals, CMS guidelines, provider contracts, and billing guides</p>

            {/* Dropzone */}
            <AnimatePresence mode="wait">
              {!file ? (
                <motion.div
                  key="dropzone"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById("file-input")?.click()}
                  className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center gap-4 transition-all duration-200 cursor-pointer ${
                    dragging
                      ? "border-sky-500/60 bg-sky-500/6"
                      : "border-black/10 hover:border-black/20 hover:bg-black/2"
                  }`}
                >
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors ${
                    dragging ? "bg-sky-500/20 text-sky-400" : "bg-black/5 text-slate-600"
                  }`}>
                    <Upload className="w-7 h-7" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold text-slate-700">Drop your PDF here</p>
                    <p className="text-xs text-slate-500 mt-1">or click to browse — PDF files only, max 50 MB</p>
                  </div>
                  <input id="file-input" type="file" accept=".pdf" onChange={handleFile} className="hidden" />
                </motion.div>
              ) : (
                <motion.div
                  key="file-selected"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="border border-sky-500/30 bg-sky-500/6 rounded-xl p-4 flex items-center gap-3"
                >
                  <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center text-sky-400 shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">{file.name}</p>
                    <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB · PDF</p>
                  </div>
                  <button onClick={reset} className="text-slate-500 hover:text-slate-600 transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Doc type */}
            <div className="mt-5">
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Document Type</label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="input-field"
              >
                {DOC_TYPES.map((t) => (
                  <option key={t.value} value={t.value} className="bg-white">{t.label}</option>
                ))}
              </select>
            </div>

            {/* Pipeline */}
            {pipelineStep >= 0 && (
              <PipelineViz active={uploading} step={pipelineStep} />
            )}

            {/* Success */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-5 p-4 rounded-xl bg-emerald-500/8 border border-emerald-500/18"
              >
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <p className="text-sm font-bold text-emerald-400">Document Indexed Successfully</p>
                </div>
                <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
                  {[
                    ["Pages",    String(result.page_count)],
                    ["Chunks",   String(result.chunk_count)],
                    ["Type",     result.document_type],
                    ["Status",   "Ready"],
                  ].map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between">
                      <span className="text-slate-500">{k}</span>
                      <span className="text-slate-700 font-medium font-mono">{v}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Next actions after success */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-5"
              >
                <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-3">What would you like to do next?</p>
                <div className="space-y-2">
                  {[
                    { label: "Ask a Question",   desc: "Query this document with AI",   href: "/assistant", color: "#111827", icon: MessageSquare },
                    { label: "Extract Rules",     desc: "Convert policy to JSON rules",  href: "/rules",     color: "#94a3b8", icon: FileCode2     },
                    { label: "Compare Policies",  desc: "Detect changes vs another doc", href: "/compare",   color: "#94a3b8", icon: GitCompare    },
                  ].map((action) => {
                    const Icon = action.icon;
                    return (
                      <Link key={action.href} href={action.href}>
                        <div className="flex items-center gap-3 p-4 rounded-xl border border-black/6 hover:border-black/12 hover:bg-black/3 transition-all cursor-pointer group">
                          <div
                            className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                            style={{ background: `${action.color}12`, border: `1px solid ${action.color}22` }}
                          >
                            <Icon className="w-4 h-4" style={{ color: action.color }} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-slate-700 group-hover:text-gray-900 transition-colors">
                              {action.label}
                            </p>
                            <p className="text-[10px] text-slate-600">{action.desc}</p>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-700 group-hover:text-slate-400 shrink-0 transition-colors" />
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {error && <p className="text-xs text-red-400 mt-3">{error}</p>}

            <div className="mt-5 flex gap-3">
              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                loading={uploading}
                className="flex-1"
                icon={<Upload className="w-4 h-4" />}
              >
                {uploading ? "Processing..." : "Upload & Index"}
              </Button>
              {result && (
                <Button variant="outline" onClick={reset} size="md">Upload Another</Button>
              )}
            </div>
          </div>

          {/* ── Right Panel ── */}
          <div className="lg:col-span-2 space-y-5">

            {/* ── Ingestion Pipeline Card ── */}
            <div className="rounded-2xl border border-black/7 bg-white p-6">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                  style={{ background: "rgba(0,0,0,0.09)", border: "1px solid rgba(0,0,0,0.15)" }}>
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                </div>
                <div>
                  <h2 className="text-[13px] font-bold text-gray-900 leading-none" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                    Ingestion Pipeline
                  </h2>
                  <p className="text-[10px] text-slate-600 mt-0.5">5-step processing flow</p>
                </div>
              </div>
              <div className="space-y-2">
                {PIPELINE_STEPS.map((step, i) => {
                  const Icon = step.icon;
                  return (
                    <div key={step.label} className="flex items-center gap-3 rounded-xl p-2.5"
                      style={{ background: "rgba(0,0,0,0.01)", border: "1px solid rgba(0,0,0,0.02)" }}>
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0"
                        style={{ background: `${step.color}18`, color: step.color, border: `1px solid ${step.color}30` }}>
                        {i + 1}
                      </div>
                      <div className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                        style={{ background: `${step.color}12` }}>
                        <Icon className="w-3 h-3" style={{ color: step.color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-semibold text-slate-600 leading-none">{step.label}</p>
                        <p className="text-[9px] text-slate-600 font-mono mt-0.5 truncate">{step.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ── Processing Stats Flash Cards ── */}
            <div className="rounded-2xl border border-black/7 bg-white p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                    style={{ background: "rgba(0,0,0,0.09)", border: "1px solid rgba(0,0,0,0.15)" }}>
                    <Zap className="w-3.5 h-3.5 text-sky-400" />
                  </div>
                  <div>
                    <h2 className="text-[13px] font-bold text-gray-900 leading-none" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                      System Config
                    </h2>
                    <p className="text-[10px] text-slate-600 mt-0.5">
                      {result ? "Live document stats" : uploading ? "Processing…" : "Pipeline parameters"}
                    </p>
                  </div>
                </div>
                {/* Live indicator */}
                {(uploading || result) && (
                  <div className="flex items-center gap-1.5">
                    <motion.div
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ background: result ? "#34d399" : "#111827" }}
                      animate={{ opacity: uploading ? [1, 0.2, 1] : 1 }}
                      transition={{ repeat: uploading ? Infinity : 0, duration: 0.8 }}
                    />
                    <span className="text-[9px] font-semibold uppercase tracking-wider"
                      style={{ color: result ? "#34d399" : "#111827" }}>
                      {result ? "Live" : "Processing"}
                    </span>
                  </div>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2">
                {buildStats(result, elapsedSec).map((stat, idx) => {
                  const Icon = stat.icon;
                  return (
                    <motion.div
                      key={stat.label}
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05, duration: 0.3 }}
                      className="relative rounded-xl p-4 overflow-hidden group"
                      style={{
                        background: stat.glow,
                        border: `1px solid ${stat.color}${stat.live ? "40" : "22"}`,
                      }}
                    >
                      {/* Hover glow */}
                      <div
                        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                        style={{ background: `radial-gradient(circle at 50% 0%, ${stat.color}18 0%, transparent 70%)` }}
                      />
                      {/* Live shimmer on updated cards */}
                      {stat.live && (
                        <motion.div
                          className="absolute inset-0 pointer-events-none"
                          initial={{ opacity: 0.4 }}
                          animate={{ opacity: 0 }}
                          transition={{ duration: 1.2 }}
                          style={{ background: `${stat.color}15` }}
                        />
                      )}
                      <div className="flex items-center gap-1.5 mb-2">
                        <div className="w-5 h-5 rounded-md flex items-center justify-center shrink-0"
                          style={{ background: `${stat.color}20` }}>
                          <Icon className="w-2.5 h-2.5" style={{ color: stat.color }} />
                        </div>
                        <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-500 leading-none">
                          {stat.label}
                        </p>
                        {stat.live && (
                          <div className="w-1 h-1 rounded-full ml-auto shrink-0" style={{ background: stat.color }} />
                        )}
                      </div>
                      <motion.p
                        key={stat.value}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.25 }}
                        className="text-[15px] font-bold leading-none font-mono"
                        style={{ color: stat.color }}
                      >
                        {/* Show live ticking during upload for Processing card */}
                        {stat.label === "Processing" && uploading && elapsedSec != null
                          ? `${elapsedSec.toFixed(1)} s`
                          : stat.value}
                      </motion.p>
                      <p className="text-[9px] text-slate-600 mt-1 truncate font-mono">{stat.sub}</p>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Recent uploads */}
            {documents.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl border border-black/7 bg-white p-5"
              >
                <h2 className="text-sm font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                  Just Indexed
                </h2>
                <div className="space-y-2.5">
                  {documents.slice(0, 3).map((doc) => (
                    <div key={doc.id} className="flex items-center gap-2.5">
                      <FileText className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <p className="text-xs text-slate-600 flex-1 truncate">{doc.filename}</p>
                      <div className="flex items-center gap-1 text-[10px] text-slate-600 shrink-0">
                        <Clock className="w-2.5 h-2.5" />
                        just now
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
