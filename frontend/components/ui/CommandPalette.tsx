"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Search, Upload, MessageSquare, GitCompare, FileCode2,
  ShieldCheck, ScrollText, LayoutDashboard, ArrowRight,
} from "lucide-react";

const COMMANDS = [
  { label: "Dashboard",        desc: "Overview & metrics",           icon: LayoutDashboard, href: "/dashboard", category: "Navigate" },
  { label: "Upload Policy",    desc: "Ingest a new PDF document",    icon: Upload,          href: "/upload",    category: "Actions"  },
  { label: "Ask AI Assistant", desc: "Query your policy library",    icon: MessageSquare,   href: "/assistant", category: "Actions"  },
  { label: "Compare Policies", desc: "Detect version changes",       icon: GitCompare,      href: "/compare",   category: "Actions"  },
  { label: "Extract Rules",    desc: "Convert policy to JSON rules", icon: FileCode2,       href: "/rules",     category: "Actions"  },
  { label: "Validate Claim",   desc: "Check CPT + diagnosis code",   icon: ShieldCheck,     href: "/claims",    category: "Actions"  },
  { label: "Audit Trail",      desc: "Full AI trace logs",           icon: ScrollText,      href: "/audit",     category: "Navigate" },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

export function CommandPalette({ open, onClose }: Props) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = COMMANDS.filter(
    (c) =>
      !query ||
      c.label.toLowerCase().includes(query.toLowerCase()) ||
      c.desc.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (!open) return;
    setQuery(""); // eslint-disable-line react-hooks/set-state-in-effect
    setSelected(0);
    setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!open) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelected((s) => Math.min(s + 1, filtered.length - 1));
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelected((s) => Math.max(s - 1, 0));
      }
      if (e.key === "Enter" && filtered[selected]) {
        router.push(filtered[selected].href);
        onClose();
      }
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, filtered, selected, router, onClose]);

  const navigate = (href: string) => {
    router.push(href);
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.12 }}
            className="fixed inset-0 z-50"
            style={{ background: "rgba(0,0,0,0.35)", backdropFilter: "blur(4px)" }}
            onClick={onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -14 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -14 }}
            transition={{ duration: 0.14, ease: [0.22, 1, 0.36, 1] }}
            className="fixed top-[18%] left-1/2 -translate-x-1/2 w-full max-w-[520px] z-50 px-4"
          >
            <div
              className="rounded-2xl overflow-hidden"
              style={{
                background: "#ffffff",
                border: "1px solid rgba(0,0,0,0.09)",
                boxShadow: "0 20px 60px rgba(0,0,0,0.15), 0 4px 16px rgba(0,0,0,0.08)",
              }}
            >
              {/* Search row */}
              <div className="flex items-center gap-3 px-4 py-3.5 border-b border-black/6">
                <Search className="w-4.5 h-4.5 text-gray-400 shrink-0" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setSelected(0);
                  }}
                  placeholder="Search actions and pages..."
                  className="flex-1 bg-transparent text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none"
                />
                <kbd className="text-[10px] text-gray-400 bg-gray-100 border border-gray-200 px-1.5 py-0.5 rounded font-mono shrink-0">
                  ESC
                </kbd>
              </div>

              {/* Results */}
              <div className="py-1.5 max-h-80 overflow-y-auto">
                {filtered.length === 0 ? (
                  <p className="text-xs text-gray-400 text-center py-8">
                    No actions found for &ldquo;{query}&rdquo;
                  </p>
                ) : (
                  ["Navigate", "Actions"].map((cat) => {
                    const items = filtered.filter((c) => c.category === cat);
                    if (!items.length) return null;
                    return (
                      <div key={cat}>
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-4 pt-3 pb-1.5">
                          {cat}
                        </p>
                        {items.map((cmd) => {
                          const gIdx = filtered.indexOf(cmd);
                          const Icon = cmd.icon;
                          const isSel = selected === gIdx;
                          return (
                            <button
                              key={cmd.href}
                              className={`w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors ${
                                isSel ? "bg-gray-100" : "hover:bg-gray-50"
                              }`}
                              onClick={() => navigate(cmd.href)}
                              onMouseEnter={() => setSelected(gIdx)}
                            >
                              <div
                                className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all ${
                                  isSel
                                    ? "bg-gray-900 text-white"
                                    : "bg-gray-100 text-gray-500"
                                }`}
                              >
                                <Icon className="w-4 h-4" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p
                                  className={`text-sm font-semibold transition-colors ${
                                    isSel ? "text-gray-900" : "text-gray-700"
                                  }`}
                                  style={{ fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)" }}
                                >
                                  {cmd.label}
                                </p>
                                <p className="text-xs text-gray-400 truncate">{cmd.desc}</p>
                              </div>
                              {isSel && (
                                <ArrowRight className="w-3.5 h-3.5 text-gray-600 shrink-0" />
                              )}
                            </button>
                          );
                        })}
                      </div>
                    );
                  })
                )}
              </div>

              {/* Footer hint */}
              <div className="px-4 py-2.5 border-t border-black/5 flex items-center gap-4 text-[10px] text-gray-400">
                <span className="flex items-center gap-1">
                  <kbd className="bg-gray-100 border border-gray-200 rounded px-1 font-mono">↑↓</kbd> navigate
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="bg-gray-100 border border-gray-200 rounded px-1 font-mono">↵</kbd> open
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="bg-gray-100 border border-gray-200 rounded px-1 font-mono">ESC</kbd> close
                </span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
