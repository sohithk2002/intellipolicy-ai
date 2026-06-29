"use client";

import { useState, useRef, useEffect, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { PageHero } from "@/components/ui/PageHero";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { Badge } from "@/components/ui/Badge";
import {
  Send, FileText, BookOpen,
  Lightbulb, ArrowRight, User, Bot, Sparkles, ScrollText, FileCode2,
  Brain, ChevronDown, AlertCircle,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { AskResponse } from "@/lib/types";
import { useDocumentContext } from "@/lib/DocumentContext";

function renderInlineBold(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={i} className="text-gray-900 font-semibold">{part.slice(2, -2)}</strong>
      : <span key={i}>{part}</span>
  );
}

function renderAnswerText(text: string) {
  const lines = text.split("\n");
  const nodes: ReactNode[] = [];
  let paraGroup: string[] = [];

  const flushPara = () => {
    if (!paraGroup.length) return;
    const combined = paraGroup.join(" ").trim();
    if (combined) nodes.push(
      <p key={`p-${nodes.length}`} className="text-[15px] text-slate-700 leading-relaxed">
        {renderInlineBold(combined)}
      </p>
    );
    paraGroup = [];
  };

  for (const line of lines) {
    const t = line.trim();
    if (!t) { flushPara(); continue; }
    const bullet = t.match(/^[-•*]\s+(.+)/);
    if (bullet) {
      flushPara();
      nodes.push(
        <div key={`b-${nodes.length}`} className="flex items-start gap-2.5">
          <div className="w-1.5 h-1.5 rounded-full bg-sky-400/70 mt-2.25 shrink-0" />
          <p className="text-[15px] text-slate-700 leading-relaxed">{renderInlineBold(bullet[1])}</p>
        </div>
      );
      continue;
    }
    const num = t.match(/^(\d+)[.)]\s+(.+)/);
    if (num) {
      flushPara();
      nodes.push(
        <div key={`n-${nodes.length}`} className="flex items-start gap-2.5">
          <span className="text-[11px] font-bold text-sky-400/80 mt-0.5 shrink-0 w-4 font-mono">{num[1]}.</span>
          <p className="text-[15px] text-slate-700 leading-relaxed">{renderInlineBold(num[2])}</p>
        </div>
      );
      continue;
    }
    paraGroup.push(t);
  }
  flushPara();

  if (!nodes.length) return <p className="text-[15px] text-slate-700 leading-relaxed">{text}</p>;
  return <div className="space-y-2">{nodes}</div>;
}

const DEFAULT_QUESTIONS = [
  "What is this document about?",
  "What services require prior authorization?",
  "What documentation is required?",
  "Which procedures require pre-certification?",
  "Are telehealth visits covered under this policy?",
];

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: AskResponse;
  timestamp: Date;
  isError?: boolean;
}

export default function AssistantPage() {
  const { selectedDoc } = useDocumentContext();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [expandedReasoning, setExpandedReasoning] = useState<Record<number, boolean>>({});
  const [expandedCitations, setExpandedCitations] = useState<Record<number, boolean>>({});
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const toggleReasoning = (i: number) =>
    setExpandedReasoning((prev) => ({ ...prev, [i]: !prev[i] }));

  const ask = async (question: string) => {
    if (!question.trim()) return;
    const userMsg: Message = { role: "user", content: question, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.askQuestion(question, selectedDoc ? [selectedDoc.id] : undefined, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, response: res, timestamp: new Date() },
      ]);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Backend unreachable.";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${errMsg} — Make sure the backend is running on port 8000 and a document has been uploaded.`,
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Follow-up questions from last assistant response
  const lastResponse = [...messages].reverse().find((m) => m.role === "assistant" && m.response)?.response;
  const suggestedQuestions = lastResponse?.follow_up_questions?.length
    ? lastResponse.follow_up_questions
    : DEFAULT_QUESTIONS;

  // Derived session context from real messages
  const assistantMsgs = messages.filter((m) => m.role === "assistant" && m.response);
  const avgConf = assistantMsgs.length > 0
    ? Math.round(assistantMsgs.reduce((s, m) => s + (m.response?.confidence ?? 0), 0) / assistantMsgs.length * 100) + "%"
    : "—";
  const allDocNames = [...new Set(assistantMsgs.flatMap((m) => m.response?.citations.map((c) => c.document_name) ?? []))];
  const srcDocLabel = allDocNames.length > 0 ? allDocNames[0] : "No document yet";
  const totalCitations = messages.reduce((s, m) => s + (m.response?.citations.length ?? 0), 0);

  return (
    <DashboardLayout>
      <div className="max-w-350 mx-auto px-10 py-10">

        <PageHero
          eyebrow="Policy Intelligence"
          title="AI Policy Assistant"
          subtitle="Ask any question about your uploaded healthcare policies. Every answer is grounded in source citations with page references and confidence scoring."
          gradient="#94a3b8"
          action={
            selectedDoc ? (
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-sky-500/8 border border-sky-500/18 text-sky-400 text-[13px] font-semibold max-w-xs truncate">
                <FileText className="w-3.5 h-3.5 shrink-0" />
                <span className="truncate">{selectedDoc.filename}</span>
              </div>
            ) : (
              <Badge variant="info">Session active</Badge>
            )
          }
        />

        <div className="grid gap-7 items-start" style={{ gridTemplateColumns: "minmax(0,58fr) minmax(0,42fr)" }}>

          {/* ── Chat Column ── */}
          <div className="rounded-2xl border border-black/7 bg-white overflow-hidden flex flex-col" style={{ minHeight: 600 }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8" style={{ maxHeight: 660 }}>

              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center gap-4 py-16">
                  <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                    <Bot className="w-8 h-8 text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-[18px] font-bold text-slate-600 mb-2">Ready to answer questions</p>
                    <p className="text-[14px] text-slate-600 max-w-xs leading-relaxed">
                      Upload a policy document first, then ask any question about it below.
                    </p>
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                    msg.role === "user" ? "bg-indigo-500/20 text-indigo-400" : msg.isError ? "bg-red-500/20 text-red-400" : "bg-sky-500/20 text-sky-400"
                  }`}>
                    {msg.role === "user" ? <User className="w-4 h-4" /> : msg.isError ? <AlertCircle className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div className={`flex-1 max-w-[92%] space-y-3 ${msg.role === "user" ? "items-end" : ""}`}>
                    <div className={`rounded-2xl px-5 py-4 ${
                      msg.role === "user"
                        ? "bg-indigo-600/18 border border-indigo-500/18 text-slate-700 ml-auto text-[15px] leading-relaxed"
                        : msg.isError
                        ? "bg-red-500/8 border border-red-500/18 text-red-300 text-[15px] leading-relaxed"
                        : "bg-black/4 border border-black/7"
                    }`}>
                      {msg.role === "assistant" && !msg.isError
                        ? renderAnswerText(msg.content)
                        : msg.content}
                    </div>

                    {msg.response && (
                      <div className="space-y-4 pl-1">
                        <div className="flex items-center gap-3">
                          <ConfidenceMeter score={msg.response.confidence} showBar={false} />
                          <div className="flex-1 h-px" style={{ background: "rgba(0,0,0,0.03)" }} />
                          <span className="text-[11px] text-slate-600 font-mono shrink-0">
                            {msg.response.citations.length} source{msg.response.citations.length !== 1 ? "s" : ""} retrieved
                          </span>
                        </div>

                        {msg.response.citations.length > 0 && (
                          <div>
                            <button
                              onClick={() => setExpandedCitations((prev) => ({ ...prev, [i]: !prev[i] }))}
                              className="flex items-center gap-2 text-[12px] text-slate-500 hover:text-sky-400 transition-colors py-1"
                            >
                              <BookOpen className="w-3 h-3" />
                              <span>{expandedCitations[i] ? "Hide" : "Show"} {msg.response.citations.length} citation{msg.response.citations.length !== 1 ? "s" : ""}</span>
                              <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${expandedCitations[i] ? "rotate-180" : ""}`} />
                            </button>
                            <AnimatePresence>
                              {expandedCitations[i] && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: "auto", opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  transition={{ duration: 0.2 }}
                                  className="overflow-hidden"
                                >
                                  <div className="mt-2 space-y-2">
                                    {msg.response.citations.map((c, ci) => (
                                      <motion.div
                                        key={ci}
                                        initial={{ opacity: 0, x: -4 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: ci * 0.06 }}
                                        className="rounded-xl border border-sky-500/12 bg-sky-500/4 px-4 py-3.5"
                                      >
                                        <div className="flex items-center justify-between mb-2 gap-3">
                                          <div className="flex items-center gap-2 min-w-0">
                                            <FileText className="w-3 h-3 text-sky-400 shrink-0" />
                                            <span className="text-[13px] font-semibold text-sky-400 truncate">{c.document_name}</span>
                                          </div>
                                          <div className="flex items-center gap-1.5 shrink-0">
                                            <Badge variant="info">p.{c.page_number}</Badge>
                                            <Badge variant="muted">{Math.round(c.relevance_score * 100)}% match</Badge>
                                          </div>
                                        </div>
                                        <p className="text-[13px] text-slate-400 italic leading-relaxed">&quot;{c.text}&quot;</p>
                                      </motion.div>
                                    ))}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-3">
                          <div className="rounded-xl border border-black/6 bg-black/3 p-4">
                            <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-2.5">Supporting Evidence</p>
                            <p className="text-[13px] text-slate-600 leading-relaxed">{msg.response.evidence}</p>
                          </div>
                          <div className="rounded-xl border border-amber-500/14 bg-amber-500/5 p-4">
                            <p className="text-[10px] font-bold text-amber-500 uppercase tracking-wider mb-2.5 flex items-center gap-1">
                              <Lightbulb className="w-3 h-3" /> Recommended Action
                            </p>
                            <p className="text-[13px] text-slate-600 leading-relaxed">{msg.response.next_action}</p>
                          </div>
                        </div>

                        {msg.response.follow_up_questions && msg.response.follow_up_questions.length > 0 && (
                          <div className="space-y-2">
                            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Ask a follow-up</p>
                            <div className="flex flex-wrap gap-2">
                              {msg.response.follow_up_questions.map((q) => (
                                <button
                                  key={q}
                                  onClick={() => ask(q)}
                                  className="text-[12px] text-sky-400 bg-sky-500/6 border border-sky-500/14 rounded-full px-3 py-1.5 hover:bg-sky-500/12 hover:border-sky-500/25 transition-all text-left"
                                >
                                  {q}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.response.reasoning_steps && msg.response.reasoning_steps.length > 0 && (
                          <div>
                            <button
                              onClick={() => toggleReasoning(i)}
                              className="flex items-center gap-2 text-[12px] text-slate-600 hover:text-slate-400 transition-colors py-1"
                            >
                              <Brain className="w-3 h-3" />
                              <span>AI reasoning trace · {msg.response.reasoning_steps.length} steps</span>
                              <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${expandedReasoning[i] ? "rotate-180" : ""}`} />
                            </button>
                            <AnimatePresence>
                              {expandedReasoning[i] && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: "auto", opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  transition={{ duration: 0.2 }}
                                  className="overflow-hidden"
                                >
                                  <div className="mt-2 rounded-xl border border-indigo-500/10 bg-indigo-500/4 p-4 space-y-3">
                                    {msg.response.reasoning_steps.map((step, si) => (
                                      <div key={si} className="flex items-start gap-2.5">
                                        <span className="text-[10px] font-bold text-indigo-400/60 font-mono shrink-0 mt-0.5 w-5">
                                          {String(si + 1).padStart(2, "0")}
                                        </span>
                                        <p className="text-[12px] text-slate-400 leading-relaxed">{step}</p>
                                      </div>
                                    ))}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        )}

                        <div className="flex items-center gap-1 flex-wrap pt-0.5">
                          <Link href="/audit">
                            <button className="flex items-center gap-1.5 text-[12px] text-slate-500 hover:text-sky-400 transition-colors px-3 py-1.5 rounded-lg hover:bg-sky-500/6 border border-transparent hover:border-sky-500/15">
                              <ScrollText className="w-3.5 h-3.5" /> View Audit Trail
                            </button>
                          </Link>
                          <Link href="/rules">
                            <button className="flex items-center gap-1.5 text-[12px] text-slate-500 hover:text-indigo-400 transition-colors px-3 py-1.5 rounded-lg hover:bg-indigo-500/6 border border-transparent hover:border-indigo-500/15">
                              <FileCode2 className="w-3.5 h-3.5" /> Extract Rule
                            </button>
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}

              {loading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-black/4 border border-black/7 rounded-2xl px-5 py-4 flex items-center gap-2">
                    <div className="loading-dot" /><div className="loading-dot" /><div className="loading-dot" />
                    <span className="text-[14px] text-slate-600 ml-2">Searching policy documents...</span>
                  </div>
                </motion.div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="border-t border-black/5 p-5">
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && ask(input)}
                  placeholder="Ask about prior authorization, coverage, billing codes..."
                  className="flex-1 bg-black/4 border border-black/8 rounded-xl px-4 py-3 text-[15px] text-slate-700 placeholder:text-slate-600 focus:outline-none focus:border-black/20 transition-colors"
                />
                <Button
                  onClick={() => ask(input)}
                  disabled={!input.trim() || loading}
                  loading={loading}
                  icon={<Send className="w-4 h-4" />}
                >
                  Ask
                </Button>
              </div>
            </div>
          </div>

          {/* ── Right Panel ── */}
          <div className="space-y-5">
            {/* Suggested questions */}
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <div className="flex items-center gap-2.5 mb-5">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <p className="text-[17px] font-bold text-gray-900" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                  {lastResponse?.follow_up_questions?.length ? "Follow-up Questions" : "Suggested Questions"}
                </p>
              </div>
              <div className="space-y-1">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => ask(q)}
                    className="w-full text-left text-[14px] text-slate-400 hover:text-sky-400 py-2.5 px-3 rounded-xl hover:bg-sky-500/6 transition-all flex items-start gap-2.5 group"
                  >
                    <ArrowRight className="w-3.5 h-3.5 mt-0.5 text-slate-700 group-hover:text-sky-400 shrink-0 transition-colors" />
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* How it works */}
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <p className="text-[17px] font-bold text-gray-900 mb-5" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                How It Works
              </p>
              <div className="space-y-4">
                {[
                  { step: "1", text: "Your question is embedded using BAAI/bge-small-en-v1.5", color: "#111827" },
                  { step: "2", text: "Top 5 most relevant policy chunks are retrieved",           color: "#94a3b8" },
                  { step: "3", text: "AI generates an answer with source mapping",                 color: "#94a3b8" },
                  { step: "4", text: "Confidence is scored across all evidence",                   color: "#34d399" },
                ].map((s) => (
                  <div key={s.step} className="flex gap-3.5 items-start">
                    <span className="w-6 h-6 rounded-full text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5"
                      style={{ background: `${s.color}14`, color: s.color, border: `1px solid ${s.color}28` }}>
                      {s.step}
                    </span>
                    <p className="text-[14px] text-slate-400 leading-relaxed">{s.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Session context — real data */}
            <div className="rounded-2xl border border-black/7 bg-white p-7">
              <p className="text-[17px] font-bold text-gray-900 mb-4" style={{ fontFamily: "var(--font-heading, sans-serif)" }}>
                Session Context
              </p>
              <div className="space-y-3 text-[14px]">
                {[
                  { label: "Questions asked",    value: String(messages.filter((m) => m.role === "user").length), valueColor: "text-slate-700" },
                  { label: "Citations retrieved", value: String(totalCitations),                                   valueColor: "text-slate-700" },
                  { label: "Avg confidence",      value: avgConf,                                                   valueColor: avgConf === "—" ? "text-slate-500" : "text-emerald-400" },
                  { label: "Source document",     value: srcDocLabel,                                               valueColor: allDocNames.length > 0 ? "text-sky-400" : "text-slate-600" },
                ].map((item) => (
                  <div key={item.label} className="flex justify-between items-center">
                    <span className="text-slate-500">{item.label}</span>
                    <span className={`font-semibold font-mono text-[13px] ${item.valueColor} max-w-40 truncate text-right`}>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
