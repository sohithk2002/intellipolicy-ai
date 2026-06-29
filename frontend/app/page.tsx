"use client";

import { motion, AnimatePresence, useMotionValueEvent, useScroll } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import {
  Upload, MessageSquare, GitCompare, FileCode2, ShieldCheck, Activity,
  Brain, Zap, Clock, AlertTriangle, FileText, ArrowRight, ChevronRight,
  CheckCircle2, Lock, BookOpen, Database,
} from "lucide-react";

/* ─── Data ─────────────────────────────────────────────────────────── */

const capabilities = [
  { icon: Upload,       title: "Smart PDF Ingestion",        desc: "Upload healthcare policies, CMS rules, and provider contracts. AI extracts, chunks, and semantically indexes every page.",                    accent: "#0ea5e9" },
  { icon: MessageSquare,title: "Policy Q&A with Citations",   desc: "Ask questions in plain English. Get precise answers with page-level citations, confidence scores, and evidence snippets.",                    accent: "#818cf8" },
  { icon: GitCompare,   title: "Policy Comparison Engine",    desc: "Upload old and new policies. Instantly detect authorization changes, coverage updates, and billing risk across versions.",                     accent: "#a78bfa" },
  { icon: FileCode2,    title: "Structured Rule Extraction",  desc: "Convert natural language policy text into machine-readable JSON business rules for downstream claims processing.",                            accent: "#34d399" },
  { icon: ShieldCheck,  title: "Claims Validation AI",        desc: "Enter CPT code, diagnosis, and plan type. Get Approved / Denied / Needs Review with policy source and next steps.",                         accent: "#fbbf24" },
  { icon: Activity,     title: "Full Audit Trail",            desc: "Every AI decision is fully traceable. Retrieved pages, reasoning steps, source citations — all in one exportable view.",                      accent: "#f87171" },
];

const painPoints = [
  { icon: Clock,         title: "Policy search takes too long",    desc: "Manual policy review consumes 4–8 hours per document cycle. Prior authorization questions require multiple policy lookups to resolve."           },
  { icon: AlertTriangle, title: "Version changes are easy to miss", desc: "Policy updates ship quarterly. Without automated comparison, critical authorization and billing changes go undetected until claims are denied." },
  { icon: FileText,      title: "Decisions need audit evidence",    desc: "AI systems that cannot explain their reasoning create compliance risk. Every decision needs a cited policy source and a traceable reasoning chain." },
];

const workflowSteps = [
  { label: "Upload Policy",  icon: Upload,        color: "#38bdf8", step: "01", desc: "Drag and drop policy PDFs. The AI parses, chunks, and embeds every page into a searchable vector store." },
  { label: "Ask Question",   icon: MessageSquare, color: "#818cf8", step: "02", desc: "Ask anything in plain English. The AI retrieves the most relevant sections and generates a cited answer." },
  { label: "Extract Rules",  icon: FileCode2,     color: "#a78bfa", step: "03", desc: "Convert policy text into structured JSON business rules for downstream claims processing systems." },
  { label: "Validate Claim", icon: ShieldCheck,   color: "#34d399", step: "04", desc: "Enter CPT code, diagnosis, plan type. Get Approved / Denied / Needs Review with policy citation." },
  { label: "View Audit",     icon: BookOpen,      color: "#fbbf24", step: "05", desc: "Every AI decision is logged with reasoning steps, citations, and confidence scores — exportable for compliance." },
];

const agents = [
  { name: "Intake Agent",     icon: Upload,        color: "#38bdf8", role: "PDF parse · text extraction · metadata storage"          },
  { name: "Retrieval Agent",  icon: Brain,         color: "#818cf8", role: "Vector search · BAAI/bge-small · cosine similarity"       },
  { name: "Policy QA Agent",  icon: MessageSquare, color: "#a78bfa", role: "Context assembly · LLM inference · citation mapping"      },
  { name: "Comparison Agent", icon: GitCompare,    color: "#34d399", role: "Section diff · risk scoring · change classification"      },
  { name: "Rule Agent",       icon: FileCode2,     color: "#fbbf24", role: "JSON extraction · claims validation · structured output"  },
];

/* ─── Hero Visual ───────────────────────────────────────────────────── */

function HeroVisual() {
  return (
    <div className="relative w-full select-none" style={{ height: 560 }} aria-hidden>
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-8 left-1/2 -translate-x-1/2 w-[420px] h-[280px] rounded-full"
          style={{ background: "radial-gradient(ellipse,rgba(14,165,233,0.1) 0%,transparent 70%)" }} />
        <div className="absolute bottom-16 right-8 w-[280px] h-[200px] rounded-full"
          style={{ background: "radial-gradient(ellipse,rgba(99,102,241,0.08) 0%,transparent 70%)" }} />
      </div>

      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
        <defs>
          <linearGradient id="cg1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0" /><stop offset="50%" stopColor="#0ea5e9" stopOpacity="0.5" /><stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="cg2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#34d399" stopOpacity="0" /><stop offset="50%" stopColor="#34d399" stopOpacity="0.5" /><stop offset="100%" stopColor="#34d399" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="cg3" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#818cf8" stopOpacity="0" /><stop offset="50%" stopColor="#818cf8" stopOpacity="0.5" /><stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="cg4" x1="100%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#fbbf24" stopOpacity="0" /><stop offset="50%" stopColor="#fbbf24" stopOpacity="0.5" /><stop offset="100%" stopColor="#fbbf24" stopOpacity="0" />
          </linearGradient>
        </defs>
        <motion.path d="M 112 92 Q 160 160 200 220"  fill="none" stroke="url(#cg1)" strokeWidth="1.5" animate={{ opacity: [0.15, 0.7, 0.15] }} transition={{ duration: 2.8, repeat: Infinity }} />
        <motion.path d="M 390 100 Q 350 170 310 220" fill="none" stroke="url(#cg2)" strokeWidth="1.5" animate={{ opacity: [0.15, 0.7, 0.15] }} transition={{ duration: 2.8, delay: 0.7, repeat: Infinity }} />
        <motion.path d="M 100 450 Q 160 400 200 360" fill="none" stroke="url(#cg3)" strokeWidth="1.5" animate={{ opacity: [0.15, 0.7, 0.15] }} transition={{ duration: 2.8, delay: 1.4, repeat: Infinity }} />
        <motion.path d="M 400 460 Q 345 400 310 360" fill="none" stroke="url(#cg4)" strokeWidth="1.5" animate={{ opacity: [0.15, 0.7, 0.15] }} transition={{ duration: 2.8, delay: 2.1, repeat: Infinity }} />
      </svg>

      {/* Central card */}
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)",
          width: 320, zIndex: 10,
          background: "linear-gradient(155deg,rgba(10,18,42,0.97) 0%,rgba(14,22,52,0.97) 100%)",
          border: "1px solid rgba(56,189,248,0.22)", borderRadius: 20, padding: "20px 22px",
          boxShadow: "0 0 80px rgba(14,165,233,0.12), 0 40px 100px rgba(0,0,0,0.7)",
          backdropFilter: "blur(28px)",
        }}
      >
        <div className="flex items-center gap-2 mb-4 pb-3" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 0 16px rgba(14,165,233,0.4)" }}>
            <Brain style={{ width: 13, height: 13, color: "white" }} />
          </div>
          <span className="text-[12px] font-bold text-white">Policy Q&A</span>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-glow" />
            <span className="text-[9px] font-bold text-emerald-400 tracking-widest">LIVE</span>
          </div>
        </div>
        <div className="rounded-xl px-3.5 py-2.5 mb-3" style={{ background: "rgba(56,189,248,0.06)", border: "1px solid rgba(56,189,248,0.12)" }}>
          <div className="text-[10px] text-slate-500 mb-1 font-semibold uppercase tracking-wider">Question</div>
          <p className="text-[12px] text-slate-200 leading-relaxed">Is CPT 99213 covered under Plan A for outpatient consults?</p>
        </div>
        <div className="rounded-xl px-3.5 py-2.5 mb-3" style={{ background: "rgba(52,211,153,0.05)", border: "1px solid rgba(52,211,153,0.15)" }}>
          <div className="text-[10px] text-emerald-400 mb-1.5 font-semibold uppercase tracking-wider">AI Answer</div>
          <p className="text-[12px] text-slate-200 leading-relaxed">Yes — covered with prior authorization. Requires ICD-10 code and ordering provider NPI per §3.2.1.</p>
        </div>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-[10px] text-slate-500 shrink-0">Confidence</span>
          <div className="flex-1 h-1.5 rounded-full" style={{ background: "rgba(255,255,255,0.06)" }}>
            <motion.div className="h-full rounded-full" style={{ background: "linear-gradient(90deg,#0ea5e9,#34d399)" }} initial={{ width: 0 }} animate={{ width: "94%" }} transition={{ delay: 0.8, duration: 1.2, ease: "easeOut" }} />
          </div>
          <span className="text-[11px] font-bold text-emerald-400 shrink-0">94%</span>
        </div>
        <div className="flex items-start gap-2 mb-4 rounded-lg px-3 py-2" style={{ background: "rgba(129,140,248,0.06)", border: "1px solid rgba(129,140,248,0.14)" }}>
          <BookOpen style={{ width: 11, height: 11, color: "#818cf8", marginTop: 2, flexShrink: 0 }} />
          <div>
            <div className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold mb-0.5">Source Citation</div>
            <div className="text-[11px] text-slate-300">CMS Policy 2024-Q4 · §3.2.1 · Page 14</div>
          </div>
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: 12 }}>
          <div className="text-[9px] text-slate-600 uppercase tracking-wider font-semibold mb-2.5">Audit Timeline</div>
          {[
            { step: "PDF Ingested",     color: "#38bdf8", delay: 0   },
            { step: "Chunks Retrieved", color: "#818cf8", delay: 0.4 },
            { step: "LLM Inference",    color: "#a78bfa", delay: 0.8 },
            { step: "Citation Mapped",  color: "#34d399", delay: 1.2 },
          ].map(({ step, color, delay }) => (
            <motion.div key={step} className="flex items-center gap-2 mb-1.5" initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1 + delay, duration: 0.4 }}>
              <div className="w-1 h-1 rounded-full shrink-0" style={{ background: color }} />
              <div className="text-[10px]" style={{ color: `${color}bb` }}>{step}</div>
              <div className="flex-1 h-px" style={{ background: `${color}15` }} />
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 + delay }} className="text-[9px] text-slate-600">✓</motion.div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Floating chips */}
      {[
        { pos: { top: 56, left: 20 }, border: "rgba(52,211,153,0.25)", shadow: "rgba(52,211,153,0.12)", delay: 0.5, dx: -16, dy: -8,
          content: <><div className="flex items-center gap-1.5 mb-1.5"><ShieldCheck style={{ width: 10, height: 10, color: "#34d399" }} /><div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Claim Decision</div></div><div className="text-[13px] font-bold" style={{ color: "#34d399" }}>Approved</div><div className="text-[9px] text-slate-500 mt-0.5">CPT 99213 · Plan A</div></> },
        { pos: { top: 68, right: 8 }, border: "rgba(56,189,248,0.22)", shadow: "rgba(56,189,248,0.1)", delay: 0.7, dx: 16, dy: -8,
          content: <><div className="flex items-center gap-1.5 mb-1.5"><Database style={{ width: 10, height: 10, color: "#38bdf8" }} /><div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Retrieved Evidence</div></div><div className="text-[11px] font-semibold text-slate-200">3 policy sections</div><div className="text-[9px] text-slate-500 mt-0.5">Pages 12, 14, 31</div></> },
        { pos: { bottom: 68, left: 12 }, border: "rgba(129,140,248,0.22)", shadow: "rgba(129,140,248,0.1)", delay: 0.9, dx: -16, dy: 8,
          content: <><div className="flex items-center gap-1.5 mb-1.5"><FileCode2 style={{ width: 10, height: 10, color: "#818cf8" }} /><div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Rule Extracted</div></div><div className="text-[10px] font-mono" style={{ color: "#818cf8cc" }}>{`{ "prior_auth": true,`}<br />{`  "cpt": "99213" }`}</div></> },
        { pos: { bottom: 60, right: 4 }, border: "rgba(251,191,36,0.2)", shadow: "rgba(251,191,36,0.08)", delay: 1.1, dx: 16, dy: 8,
          content: <><div className="flex items-center gap-1.5 mb-1.5"><Activity style={{ width: 10, height: 10, color: "#fbbf24" }} /><div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Audit Logged</div></div><div className="text-[11px] font-semibold text-slate-200">Full trace saved</div><div className="flex items-center gap-1 mt-0.5"><div className="w-1 h-1 rounded-full bg-emerald-400 pulse-glow" /><span className="text-[9px] text-emerald-500">Exportable</span></div></> },
      ].map(({ pos, border, shadow, delay, dx, dy, content }, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: dx, y: dy }}
          animate={{ opacity: 1, x: 0, y: 0 }}
          transition={{ delay, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          style={{
            position: "absolute", ...pos, width: i === 2 ? 176 : i === 3 ? 164 : i === 1 ? 172 : 168, zIndex: 20,
            background: "rgba(8,14,32,0.93)", border: `1px solid ${border}`, borderRadius: 14,
            padding: "12px 14px", backdropFilter: "blur(20px)",
            boxShadow: `0 0 28px ${shadow}, 0 16px 40px rgba(0,0,0,0.55)`,
          }}
        >
          {content}
        </motion.div>
      ))}
    </div>
  );
}

/* ─── Section transition variants ───────────────────────────────────── */

const SV = {
  hidden:  { opacity: 0, y: 24, scale: 0.985 },
  visible: { opacity: 1, y: 0,  scale: 1,    transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] as const } },
  exit:    { opacity: 0, y: -12, scale: 0.985, transition: { duration: 0.18, ease: "easeIn" as const } },
};

const CONTAINER = { maxWidth: 1280, margin: "0 auto", padding: "0 32px" };
const VIEWPORT_SECTION: React.CSSProperties = {
  minHeight: "calc(100vh - 84px)",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  padding: "80px 0",
};

type Section = "home" | "problem" | "capabilities" | "workflow" | "architecture";

const NAV_TABS: { id: Section; label: string }[] = [
  { id: "problem",      label: "Problem"      },
  { id: "capabilities", label: "Capabilities" },
  { id: "workflow",     label: "Workflow"      },
  { id: "architecture", label: "Architecture" },
];

/* ─── Page ─────────────────────────────────────────────────────────── */

export default function LandingPage() {
  const [active, setActive] = useState<Section>("home");
  const { scrollYProgress } = useScroll();
  const [scrolled, setScrolled] = useState(false);
  useMotionValueEvent(scrollYProgress, "change", (v) => setScrolled(v > 0.005));

  return (
    <div className="min-h-screen bg-[#04070f] overflow-x-hidden">

      {/* ──────── NAV ──────── */}
      <nav
        className="fixed top-0 left-0 right-0 z-50"
        style={{
          height: 84,
          background: "rgba(4,7,15,0.82)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          boxShadow: scrolled ? "0 4px 32px rgba(0,0,0,0.45)" : "none",
          transition: "box-shadow 0.3s ease",
        }}
      >
        <div className="h-full flex items-center justify-between" style={{ maxWidth: 1400, margin: "0 auto", paddingLeft: 40, paddingRight: 40 }}>

          {/* Logo → home */}
          <button onClick={() => setActive("home")} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 14 }}>
            <div className="relative">
              <motion.div
                animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.15, 1] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                style={{ position: "absolute", inset: -4, borderRadius: 16, background: "radial-gradient(ellipse,rgba(14,165,233,0.35) 0%,transparent 70%)", pointerEvents: "none" }}
              />
              <div style={{ width: 38, height: 38, borderRadius: 12, background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 0 24px rgba(14,165,233,0.45)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
                <Zap style={{ width: 18, height: 18, color: "white" }} />
              </div>
            </div>
            <span style={{ fontSize: 20, fontWeight: 700, color: "white", letterSpacing: "-0.03em", fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)" }}>
              IntelliPolicy AI
            </span>
          </button>

          {/* Center nav tabs */}
          <div className="hidden md:flex items-center" style={{ gap: 40 }}>
            {NAV_TABS.map(({ id, label }) => {
              const isActive = active === id;
              return (
                <button
                  key={id}
                  onClick={() => setActive(id)}
                  style={{
                    position: "relative",
                    fontSize: 16,
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? "white" : "rgba(148,163,184,0.85)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    paddingTop: 12,
                    paddingBottom: 12,
                    paddingLeft: 2,
                    paddingRight: 2,
                    letterSpacing: "-0.01em",
                    transition: "color 0.15s ease",
                    textShadow: isActive ? "0 0 24px rgba(14,165,233,0.55)" : "none",
                  }}
                  onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.color = "white"; }}
                  onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.color = "rgba(148,163,184,0.85)"; }}
                >
                  {label}
                  {isActive && (
                    <motion.span
                      layoutId="nav-active-line"
                      style={{
                        position: "absolute",
                        bottom: 8,
                        left: 0,
                        right: 0,
                        height: 1.5,
                        background: "linear-gradient(90deg,#0ea5e9,#6366f1)",
                        borderRadius: 1,
                      }}
                      transition={{ type: "spring", stiffness: 400, damping: 35 }}
                    />
                  )}
                </button>
              );
            })}
          </div>

          {/* Right buttons */}
          <div className="flex items-center" style={{ gap: 12 }}>
            <Link href="/assistant" className="hidden md:block">
              <motion.button
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.97 }}
                transition={{ duration: 0.18 }}
                style={{ display: "inline-flex", alignItems: "center", gap: 7, height: 42, paddingLeft: 20, paddingRight: 20, borderRadius: 11, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)", color: "rgba(203,213,225,0.9)", fontSize: 15, fontWeight: 500, letterSpacing: "-0.01em", cursor: "pointer", whiteSpace: "nowrap" }}
              >
                View Demo
              </motion.button>
            </Link>
            <Link href="/dashboard">
              <motion.button
                whileHover={{ y: -2, boxShadow: "0 8px 28px rgba(14,165,233,0.38)" }}
                whileTap={{ scale: 0.97 }}
                transition={{ duration: 0.18 }}
                style={{ display: "inline-flex", alignItems: "center", gap: 7, height: 44, paddingLeft: 22, paddingRight: 22, borderRadius: 11, background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 2px 16px rgba(14,165,233,0.28)", color: "white", fontSize: 15, fontWeight: 600, letterSpacing: "-0.01em", border: "none", cursor: "pointer", whiteSpace: "nowrap" }}
              >
                Launch App <ArrowRight style={{ width: 15, height: 15 }} />
              </motion.button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ──────── SECTIONS ──────── */}
      <div style={{ paddingTop: 84 }}>
        <AnimatePresence mode="wait">

          {/* ── HOME ── */}
          {active === "home" && (
            <motion.div key="home" variants={SV} initial="hidden" animate="visible" exit="exit">
              {/* Hero */}
              <section
                className="relative overflow-hidden"
                style={{
                  minHeight: "calc(100vh - 84px)",
                  display: "flex",
                  alignItems: "center",
                  backgroundImage: "linear-gradient(rgba(56,189,248,0.028) 1px,transparent 1px),linear-gradient(90deg,rgba(56,189,248,0.028) 1px,transparent 1px)",
                  backgroundSize: "64px 64px",
                }}
              >
                {/* Blobs */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                  <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[900px] h-[600px] rounded-full opacity-50" style={{ background: "radial-gradient(ellipse,rgba(14,165,233,0.07) 0%,transparent 70%)" }} />
                  <div className="absolute top-1/3 left-[10%] w-[500px] h-[400px] rounded-full opacity-40" style={{ background: "radial-gradient(ellipse,rgba(99,102,241,0.07) 0%,transparent 70%)" }} />
                  <div className="absolute top-1/4 right-[8%] w-[400px] h-[400px] rounded-full opacity-30" style={{ background: "radial-gradient(ellipse,rgba(139,92,246,0.06) 0%,transparent 70%)" }} />
                </div>

                <div className="relative z-10 w-full" style={{ ...CONTAINER, padding: "80px 32px" }}>
                  <div className="grid items-center" style={{ gridTemplateColumns: "48% 52%", gap: "3rem" }}>
                    {/* Left */}
                    <div className="space-y-8">
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
                        className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full"
                        style={{ border: "1px solid rgba(14,165,233,0.25)", background: "rgba(14,165,233,0.06)" }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-sky-400 pulse-glow" />
                        <span className="text-sky-400 text-xs font-bold tracking-wide uppercase">Healthcare Policy Intelligence Platform</span>
                      </motion.div>

                      <motion.h1 initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                        style={{ fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)", fontSize: "clamp(2.5rem, 5vw, 4.5rem)", fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.05 }}>
                        <span className="text-white">Traceable Agentic AI</span><br />
                        <span className="gradient-text">for Healthcare Policy</span><br />
                        <span style={{ color: "rgba(148,163,184,0.55)" }}>Intelligence</span>
                      </motion.h1>

                      <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.18 }}
                        style={{ fontSize: 17, color: "rgba(148,163,184,0.85)", lineHeight: 1.8, maxWidth: 500 }}>
                        Reduce manual policy review with AI-powered document understanding, policy comparison, claims validation, and audit-ready citations.
                      </motion.p>

                      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.26 }}
                        style={{ marginTop: 32, display: "flex", alignItems: "center", gap: 16 }}>
                        <Link href="/upload">
                          <motion.button whileHover={{ y: -2, boxShadow: "0 6px 24px rgba(14,165,233,0.32)" }} whileTap={{ scale: 0.97 }} transition={{ duration: 0.2 }}
                            style={{ display: "inline-flex", alignItems: "center", gap: 7, height: 40, paddingLeft: 20, paddingRight: 20, borderRadius: 12, background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 2px 12px rgba(14,165,233,0.22)", color: "white", fontSize: 15, fontWeight: 600, letterSpacing: "-0.02em", border: "none", cursor: "pointer", whiteSpace: "nowrap" }}>
                            <Upload style={{ width: 16, height: 16, flexShrink: 0 }} /> Upload Policy
                          </motion.button>
                        </Link>
                        <Link href="/dashboard">
                          <motion.button whileHover={{ y: -2, background: "rgba(255,255,255,0.08)" }} whileTap={{ scale: 0.97 }} transition={{ duration: 0.2 }}
                            style={{ display: "inline-flex", alignItems: "center", gap: 7, height: 40, paddingLeft: 20, paddingRight: 20, borderRadius: 12, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)", color: "white", fontSize: 15, fontWeight: 600, letterSpacing: "-0.02em", cursor: "pointer", whiteSpace: "nowrap" }}>
                            View Dashboard <ChevronRight style={{ width: 16, height: 16, flexShrink: 0 }} />
                          </motion.button>
                        </Link>
                      </motion.div>

                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
                        style={{ marginTop: 20, display: "flex", flexWrap: "wrap", gap: 24 }}>
                        {["Citation-grounded", "Audit-ready", "Human-in-the-loop", "Enterprise POC"].map((b) => (
                          <div key={b} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            <CheckCircle2 style={{ width: 13, height: 13, color: "#10b981", flexShrink: 0 }} />
                            <span style={{ fontSize: 12, color: "#64748b" }}>{b}</span>
                          </div>
                        ))}
                      </motion.div>
                    </div>

                    {/* Right */}
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                      className="hidden lg:flex items-center justify-center">
                      <HeroVisual />
                    </motion.div>
                  </div>
                </div>
              </section>

              {/* CTA */}
              <section style={{ padding: "0 32px 0" }}>
                <div style={CONTAINER}>
                  <motion.div
                    initial={{ opacity: 0, y: 36 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="relative overflow-hidden text-center"
                    style={{
                      borderRadius: 28,
                      padding: "80px 48px",
                      background: "radial-gradient(120% 90% at 50% 0%, rgba(14,165,233,0.12) 0%, rgba(99,102,241,0.08) 40%, rgba(10,14,28,0.96) 80%)",
                      border: "1px solid rgba(56,189,248,0.12)",
                      boxShadow: "0 0 80px rgba(14,165,233,0.06), 0 40px 100px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)",
                    }}
                  >
                    {/* Subtle grid */}
                    <div className="absolute inset-0 pointer-events-none"
                      style={{ backgroundImage: "linear-gradient(rgba(56,189,248,0.022) 1px,transparent 1px),linear-gradient(90deg,rgba(56,189,248,0.022) 1px,transparent 1px)", backgroundSize: "52px 52px" }} />
                    {/* Top glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 pointer-events-none"
                      style={{ width: 640, height: 280, background: "radial-gradient(ellipse,rgba(14,165,233,0.14) 0%,transparent 70%)" }} />
                    {/* Bottom fade into footer */}
                    <div className="absolute bottom-0 left-0 right-0 h-32 pointer-events-none"
                      style={{ background: "linear-gradient(to bottom,transparent,rgba(4,7,15,0.6))" }} />

                    <div className="relative z-10">
                      <div className="w-14 h-14 rounded-2xl mx-auto mb-8 flex items-center justify-center"
                        style={{ background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 0 48px rgba(14,165,233,0.4), 0 8px 24px rgba(0,0,0,0.4)" }}>
                        <Zap style={{ width: 24, height: 24, color: "white" }} />
                      </div>
                      <h2 className="headline-text text-white mb-5">Ready to modernize<br /><span className="gradient-text">healthcare policy review?</span></h2>
                      <p className="text-[17px] text-slate-400 mb-10 max-w-lg mx-auto leading-relaxed">
                        Scalable architecture. Citation-grounded answers. Audit-ready workflow.
                      </p>
                      <div className="flex flex-wrap gap-4 justify-center">
                        <Link href="/dashboard">
                          <motion.button
                            whileHover={{ y: -2, boxShadow: "0 0 56px rgba(14,165,233,0.45), 0 8px 24px rgba(0,0,0,0.4)" }}
                            whileTap={{ scale: 0.97 }}
                            transition={{ duration: 0.2, ease: "easeOut" }}
                            style={{ display: "inline-flex", alignItems: "center", gap: 8, height: 48, paddingLeft: 28, paddingRight: 28, borderRadius: 14, background: "linear-gradient(135deg,#0ea5e9,#6366f1)", boxShadow: "0 0 32px rgba(14,165,233,0.32), 0 4px 16px rgba(0,0,0,0.4)", color: "white", fontSize: 15, fontWeight: 600, letterSpacing: "-0.01em", border: "none", cursor: "pointer" }}>
                            Launch App <ArrowRight style={{ width: 16, height: 16 }} />
                          </motion.button>
                        </Link>
                        <Link href="/assistant">
                          <motion.button
                            whileHover={{ y: -2, borderColor: "rgba(255,255,255,0.18)" }}
                            whileTap={{ scale: 0.97 }}
                            transition={{ duration: 0.2, ease: "easeOut" }}
                            style={{ display: "inline-flex", alignItems: "center", gap: 8, height: 48, paddingLeft: 28, paddingRight: 28, borderRadius: 14, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.09)", backdropFilter: "blur(12px)", color: "rgba(203,213,225,0.9)", fontSize: 15, fontWeight: 600, letterSpacing: "-0.01em", cursor: "pointer" }}>
                            Try Demo <ChevronRight style={{ width: 16, height: 16 }} />
                          </motion.button>
                        </Link>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </section>

              {/* Footer — blends naturally into page */}
              <footer style={{ padding: "80px 32px 64px" }}>
                <div style={{ ...CONTAINER, textAlign: "center" }}>
                  {/* Hairline separator */}
                  <div style={{ height: 1, background: "linear-gradient(90deg,transparent,rgba(255,255,255,0.05),transparent)", marginBottom: 48 }} />
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, marginBottom: 16 }}>
                    <div style={{ width: 24, height: 24, borderRadius: 8, background: "linear-gradient(135deg,#0ea5e9,#6366f1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Zap style={{ width: 11, height: 11, color: "white" }} />
                    </div>
                    <span style={{ fontSize: 14, fontWeight: 600, color: "rgba(148,163,184,0.7)", letterSpacing: "-0.01em", fontFamily: "var(--font-heading, sans-serif)" }}>
                      IntelliPolicy AI
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: "rgba(100,116,139,0.7)", letterSpacing: "0.01em", marginBottom: 8 }}>
                    Enterprise Proof of Concept · Built for healthcare policy intelligence
                  </p>
                  <p style={{ fontSize: 11, color: "rgba(71,85,105,0.6)", maxWidth: 420, margin: "0 auto", lineHeight: 1.7 }}>
                    AI outputs require human review before operational use.
                  </p>
                </div>
              </footer>
            </motion.div>
          )}

          {/* ── PROBLEM ── */}
          {active === "problem" && (
            <motion.div key="problem" variants={SV} initial="hidden" animate="visible" exit="exit">
              <div style={VIEWPORT_SECTION}>
                <div style={CONTAINER}>
                  {/* Heading */}
                  <div className="text-center" style={{ marginBottom: 48 }}>
                    <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
                      className="section-label"
                      style={{ background: "linear-gradient(135deg,#f87171,#fb923c)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginBottom: 24 }}>
                      The Problem
                    </motion.p>
                    <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                      className="headline-text text-white" style={{ marginBottom: 24 }}>
                      Manual policy review{" "}
                      <span style={{ background: "linear-gradient(135deg,#f87171,#fb923c)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>does not scale</span>
                    </motion.h2>
                    <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }}
                      style={{ fontSize: 18, color: "rgba(148,163,184,0.85)", maxWidth: 680, margin: "0 auto", lineHeight: 1.75 }}>
                      Healthcare teams spend hundreds of hours every quarter manually reviewing policy documents, comparing versions, validating claims, and maintaining audit compliance.
                    </motion.p>
                  </div>

                  {/* Cards */}
                  <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto items-stretch">
                    {painPoints.map((p, i) => {
                      const Icon = p.icon;
                      return (
                        <motion.div
                          key={p.title}
                          initial={{ opacity: 0, y: 30 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                          whileHover={{ y: -6 }}
                          className="rounded-2xl cursor-default relative overflow-hidden flex flex-col"
                          style={{
                            padding: "32px 28px 28px",
                            background: "radial-gradient(120% 80% at 50% 0%, rgba(248,113,113,0.07) 0%, rgba(10,14,28,0.9) 65%)",
                            border: "1px solid rgba(248,113,113,0.1)",
                            backdropFilter: "blur(16px)",
                            boxShadow: "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)",
                            transition: "border-color 0.22s ease, box-shadow 0.22s ease",
                          }}
                          onMouseEnter={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = "rgba(248,113,113,0.3)"; d.style.boxShadow = "0 24px 72px rgba(0,0,0,0.5), 0 0 60px rgba(248,113,113,0.09), inset 0 1px 0 rgba(255,255,255,0.06)"; }}
                          onMouseLeave={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = "rgba(248,113,113,0.1)"; d.style.boxShadow = "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)"; }}
                        >
                          <div style={{ width: 48, height: 48, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 24, background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.2)", boxShadow: "0 0 20px rgba(248,113,113,0.15)", flexShrink: 0 }}>
                            <Icon style={{ width: 22, height: 22, color: "#f87171" }} />
                          </div>
                          <h3 style={{ fontSize: 15, fontWeight: 700, color: "white", marginBottom: 12, lineHeight: 1.35 }}>{p.title}</h3>
                          <p style={{ fontSize: 14, color: "rgba(148,163,184,0.7)", lineHeight: 1.75, flex: 1 }}>{p.desc}</p>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── CAPABILITIES ── */}
          {active === "capabilities" && (
            <motion.div key="capabilities" variants={SV} initial="hidden" animate="visible" exit="exit">
              <div
                style={{
                  ...VIEWPORT_SECTION,
                  backgroundImage: "radial-gradient(circle,rgba(56,189,248,0.045) 1px,transparent 1px)",
                  backgroundSize: "28px 28px",
                }}
              >
                <div style={CONTAINER}>
                  {/* Heading */}
                  <div className="text-center" style={{ marginBottom: 48 }}>
                    <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
                      className="section-label"
                      style={{ background: "linear-gradient(135deg,#818cf8,#a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginBottom: 24 }}>
                      Platform Capabilities
                    </motion.p>
                    <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                      className="headline-text text-white" style={{ marginBottom: 24 }}>
                      Everything your claims team needs —{" "}<span className="gradient-text-blue">in one platform</span>
                    </motion.h2>
                    <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }}
                      style={{ fontSize: 18, color: "rgba(148,163,184,0.85)", maxWidth: 680, margin: "0 auto", lineHeight: 1.75 }}>
                      A unified AI platform that replaces hours of manual policy review with seconds of intelligent, cited, auditable analysis.
                    </motion.p>
                  </div>

                  {/* 3×2 grid */}
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 items-stretch">
                    {capabilities.map((c, i) => {
                      const Icon = c.icon;
                      return (
                        <motion.div
                          key={c.title}
                          initial={{ opacity: 0, y: 28 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.18 + i * 0.07, ease: [0.16, 1, 0.3, 1] }}
                          whileHover={{ y: -6 }}
                          className="group rounded-2xl cursor-default relative overflow-hidden flex flex-col"
                          style={{
                            padding: "32px 28px 28px",
                            background: `radial-gradient(120% 70% at 50% 0%, ${c.accent}09 0%, rgba(10,14,28,0.92) 70%)`,
                            border: `1px solid ${c.accent}18`,
                            backdropFilter: "blur(16px)",
                            boxShadow: "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)",
                            transition: "border-color 0.22s ease, box-shadow 0.22s ease",
                          }}
                          onMouseEnter={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = `${c.accent}40`; d.style.boxShadow = `0 24px 72px rgba(0,0,0,0.5), 0 0 60px ${c.accent}14, inset 0 1px 0 rgba(255,255,255,0.07)`; }}
                          onMouseLeave={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = `${c.accent}18`; d.style.boxShadow = "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)"; }}
                        >
                          <div className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                            style={{ background: `linear-gradient(90deg,transparent,${c.accent}55,transparent)` }} />
                          <div style={{ width: 48, height: 48, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 24, background: `${c.accent}12`, border: `1px solid ${c.accent}25`, boxShadow: `0 0 20px ${c.accent}18`, flexShrink: 0 }}>
                            <Icon style={{ width: 20, height: 20, color: c.accent }} />
                          </div>
                          <h3 style={{ fontSize: 15, fontWeight: 700, color: "white", marginBottom: 12, lineHeight: 1.35 }}>{c.title}</h3>
                          <p style={{ fontSize: 14, color: "rgba(148,163,184,0.7)", lineHeight: 1.75, flex: 1 }}>{c.desc}</p>
                          <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                            style={{ marginTop: 20, fontSize: 13, fontWeight: 600, color: c.accent }}>
                            Explore <ArrowRight style={{ width: 13, height: 13 }} />
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── WORKFLOW ── */}
          {active === "workflow" && (
            <motion.div key="workflow" variants={SV} initial="hidden" animate="visible" exit="exit">
              <div style={VIEWPORT_SECTION}>
                <div style={CONTAINER}>
                  {/* Heading */}
                  <div className="text-center" style={{ marginBottom: 64 }}>
                    <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
                      className="section-label"
                      style={{ background: "linear-gradient(135deg,#34d399,#10b981)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginBottom: 24 }}>
                      How It Works
                    </motion.p>
                    <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                      className="headline-text text-white" style={{ marginBottom: 24 }}>
                      From policy PDF to{" "}<span className="gradient-text-green">decision in seconds</span>
                    </motion.h2>
                    <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }}
                      style={{ fontSize: 18, color: "rgba(148,163,184,0.85)", maxWidth: 580, margin: "0 auto", lineHeight: 1.75 }}>
                      Five intelligent steps that turn unstructured policy documents into cited, traceable AI decisions.
                    </motion.p>
                  </div>

                  {/* Steps */}
                  <div className="relative max-w-5xl mx-auto">
                    {/* Track line */}
                    <div className="hidden lg:block absolute top-[44px] left-[8%] right-[8%] h-0.5"
                      style={{ background: "rgba(255,255,255,0.04)", borderRadius: 1 }} />
                    {/* Animated fill */}
                    <motion.div
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.35, duration: 1.2, ease: "easeInOut" }}
                      className="hidden lg:block absolute top-[44px] left-[8%] right-[8%] h-0.5 origin-left"
                      style={{ background: "linear-gradient(90deg,#38bdf8,#818cf8,#a78bfa,#34d399,#fbbf24)", borderRadius: 1, boxShadow: "0 0 12px rgba(56,189,248,0.25)" }}
                    />

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                      {workflowSteps.map((s, i) => {
                        const Icon = s.icon;
                        return (
                          <motion.div
                            key={s.label}
                            initial={{ opacity: 0, y: 32 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                            className="flex flex-col items-center text-center"
                          >
                            <motion.div
                              whileHover={{ scale: 1.07, boxShadow: `0 0 48px ${s.color}50, 0 16px 40px rgba(0,0,0,0.55)` }}
                              transition={{ duration: 0.22, ease: "easeOut" }}
                              className="relative z-10 flex items-center justify-center"
                              style={{
                                width: 88, height: 88, borderRadius: 24,
                                background: `radial-gradient(120% 120% at 50% 0%, ${s.color}14 0%, rgba(10,14,28,0.95) 70%)`,
                                border: `1px solid ${s.color}38`,
                                boxShadow: `0 0 32px ${s.color}20, 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 ${s.color}15`,
                                marginBottom: 28,
                              }}
                            >
                              <Icon style={{ color: s.color, width: 32, height: 32 }} />
                            </motion.div>
                            <div style={{ paddingLeft: 4, paddingRight: 4 }}>
                              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.18em", marginBottom: 10, background: `linear-gradient(135deg,${s.color},${s.color}80)`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
                                {s.step}
                              </div>
                              <div style={{ fontSize: 15, fontWeight: 700, color: "white", marginBottom: 10, lineHeight: 1.3 }}>{s.label}</div>
                              <p style={{ fontSize: 13, color: "rgba(100,116,139,0.85)", lineHeight: 1.7 }}>{s.desc}</p>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── ARCHITECTURE ── */}
          {active === "architecture" && (
            <motion.div key="architecture" variants={SV} initial="hidden" animate="visible" exit="exit">
              <div
                style={{
                  ...VIEWPORT_SECTION,
                  backgroundImage: "radial-gradient(circle,rgba(56,189,248,0.04) 1px,transparent 1px)",
                  backgroundSize: "28px 28px",
                }}
              >
                <div style={CONTAINER}>
                  {/* Heading */}
                  <div className="text-center" style={{ marginBottom: 48 }}>
                    <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
                      className="section-label"
                      style={{ background: "linear-gradient(135deg,#a78bfa,#818cf8)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginBottom: 24 }}>
                      Agent Architecture
                    </motion.p>
                    <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                      className="headline-text text-white" style={{ marginBottom: 24 }}>
                      5 specialized AI agents,{" "}<span className="gradient-text-blue">orchestrated for precision</span>
                    </motion.h2>
                    <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }}
                      style={{ fontSize: 18, color: "rgba(148,163,184,0.85)", maxWidth: 680, margin: "0 auto", lineHeight: 1.75 }}>
                      LangGraph agents work in sequence — each with a defined role, shared context, and audit-logged outputs that support full traceability.
                    </motion.p>
                  </div>

                  {/* Agent cards */}
                  <div className="relative max-w-5xl mx-auto">
                    {/* Track */}
                    <div className="hidden lg:block absolute top-13.5 left-[5%] right-[5%] h-0.5"
                      style={{ background: "rgba(255,255,255,0.04)", borderRadius: 1 }} />
                    <motion.div
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: 0.35, duration: 1, ease: "easeInOut" }}
                      className="hidden lg:block absolute top-13.5 left-[5%] right-[5%] h-0.5 origin-left"
                      style={{ background: "linear-gradient(90deg,#38bdf8,#818cf8,#a78bfa,#34d399,#fbbf24)", borderRadius: 1, boxShadow: "0 0 10px rgba(129,140,248,0.25)" }}
                    />

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 items-stretch" style={{ marginBottom: 56 }}>
                      {agents.map((ag, i) => {
                        const Icon = ag.icon;
                        return (
                          <motion.div
                            key={ag.name}
                            initial={{ opacity: 0, y: 28 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                            whileHover={{ y: -6 }}
                            className="rounded-2xl text-center relative overflow-hidden flex flex-col"
                            style={{
                              padding: "28px 16px 24px",
                              background: `radial-gradient(120% 70% at 50% 0%, ${ag.color}09 0%, rgba(10,14,28,0.92) 70%)`,
                              border: `1px solid ${ag.color}15`,
                              backdropFilter: "blur(16px)",
                              boxShadow: "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)",
                              transition: "border-color 0.22s ease, box-shadow 0.22s ease",
                            }}
                            onMouseEnter={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = `${ag.color}40`; d.style.boxShadow = `0 24px 64px rgba(0,0,0,0.5), 0 0 48px ${ag.color}14, inset 0 1px 0 rgba(255,255,255,0.07)`; }}
                            onMouseLeave={e => { const d = e.currentTarget as HTMLDivElement; d.style.borderColor = `${ag.color}15`; d.style.boxShadow = "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)"; }}
                          >
                            <div style={{ width: 52, height: 52, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 18px", background: `${ag.color}12`, border: `1px solid ${ag.color}28`, boxShadow: `0 0 24px ${ag.color}20, inset 0 1px 0 ${ag.color}15` }}>
                              <Icon style={{ color: ag.color, width: 22, height: 22 }} />
                            </div>
                            <div style={{ fontSize: 13, fontWeight: 700, color: "white", marginBottom: 8, lineHeight: 1.3 }}>{ag.name}</div>
                            <div style={{ fontSize: 11, color: "rgba(100,116,139,0.8)", lineHeight: 1.6, fontFamily: "var(--font-code, monospace)" }}>{ag.role.split(" · ")[0]}</div>
                          </motion.div>
                        );
                      })}
                    </div>

                    {/* Audit callout */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.55 }}
                      style={{
                        borderRadius: 20,
                        padding: "20px 28px",
                        minHeight: 76,
                        background: "radial-gradient(120% 80% at 50% 0%, rgba(52,211,153,0.07) 0%, rgba(10,14,28,0.85) 70%)",
                        border: "1px solid rgba(52,211,153,0.18)",
                        boxShadow: "0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(52,211,153,0.08)",
                        display: "flex",
                        alignItems: "center",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 20, width: "100%" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 14, flexShrink: 0 }}>
                          <div style={{ width: 38, height: 38, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.22)", boxShadow: "0 0 16px rgba(52,211,153,0.15)" }}>
                            <Lock style={{ width: 15, height: 15, color: "#34d399" }} />
                          </div>
                          <span style={{ fontSize: 14, fontWeight: 700, color: "#34d399", whiteSpace: "nowrap" }}>Audit-Ready by Design</span>
                        </div>
                        <div style={{ width: 1, height: 32, background: "rgba(52,211,153,0.15)", flexShrink: 0 }} />
                        <p style={{ fontSize: 14, color: "rgba(148,163,184,0.7)", lineHeight: 1.65, flex: 1 }}>
                          Every AI inference is logged with retrieved pages, reasoning steps, confidence scores, and source citations — exportable for compliance review at any time.
                        </p>
                      </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
