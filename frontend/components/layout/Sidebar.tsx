"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Upload, MessageSquare, GitCompare,
  FileCode2, ShieldCheck, ScrollText, Zap, ExternalLink,
  Building2, Search,
} from "lucide-react";
import { useDocumentContext } from "@/lib/DocumentContext";

const navItems = [
  { href: "/dashboard", label: "Dashboard",        icon: LayoutDashboard, desc: "Overview & metrics"     },
  { href: "/upload",    label: "Upload Documents",  icon: Upload,          desc: "Ingest policy PDFs"     },
  { href: "/assistant", label: "AI Assistant",      icon: MessageSquare,   desc: "Ask policy questions"   },
  { href: "/compare",   label: "Policy Compare",    icon: GitCompare,      desc: "Detect version changes" },
  { href: "/rules",     label: "Rule Extraction",   icon: FileCode2,       desc: "Extract JSON rules"     },
  { href: "/claims",    label: "Claims Validator",  icon: ShieldCheck,     desc: "Validate CPT claims"    },
  { href: "/audit",     label: "Audit Trail",       icon: ScrollText,      desc: "Full AI trace logs"     },
];

export default function Sidebar({ onCmdK }: { onCmdK?: () => void }) {
  const pathname = usePathname();
  const { selectedDoc, documents, setSelectedDoc } = useDocumentContext();

  return (
    <aside
      style={{
        width: 280,
        flexShrink: 0,
        height: "100vh",
        position: "sticky",
        top: 0,
        display: "flex",
        flexDirection: "column",
        background: "#ffffff",
        borderRight: "1px solid rgba(0,0,0,0.04)",
      }}
    >
      {/* Logo area — 64px tall */}
      <div
        style={{
          height: 64,
          padding: "0 20px",
          display: "flex",
          alignItems: "center",
          borderBottom: "1px solid rgba(0,0,0,0.03)",
          flexShrink: 0,
        }}
      >
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", flex: 1, minWidth: 0 }}>
          {/* Logo icon with animated glow */}
          <div style={{ position: "relative", flexShrink: 0 }}>
            <div
              style={{
                position: "absolute",
                inset: -4,
                borderRadius: 16,
                background: "rgba(0,0,0,0.05)",
                filter: "blur(8px)",
              }}
            />
            <div
              style={{
                position: "relative",
                width: 36,
                height: 36,
                borderRadius: 12,
                background: "linear-gradient(135deg, #1e293b, #334155)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Zap style={{ width: 16, height: 16, color: "white" }} />
            </div>
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <p
              style={{
                fontSize: 16,
                fontWeight: 700,
                color: "#111827",
                lineHeight: 1.2,
                margin: 0,
                fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)",
              }}
            >
              IntelliPolicy AI
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 3 }}>
              <motion.div
                animate={{ opacity: [1, 0.4, 1] }}
                transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", flexShrink: 0 }}
              />
              <p style={{ fontSize: 10, color: "#34d399", fontWeight: 600, letterSpacing: "0.04em", margin: 0 }}>
                AI Platform · Live
              </p>
            </div>
          </div>

          <ExternalLink style={{ width: 13, height: 13, color: "rgba(100,116,139,0.5)", flexShrink: 0 }} />
        </Link>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "16px 12px", overflowY: "auto" }}>
        <p
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: "rgba(100,116,139,0.6)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            padding: "0 12px",
            marginBottom: 12,
          }}
        >
          PLATFORM
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link key={item.href} href={item.href} style={{ textDecoration: "none" }}>
                <motion.div
                  whileHover={active ? {} : { x: 2 }}
                  whileTap={{ scale: 0.98 }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 12px",
                    borderRadius: 12,
                    cursor: "pointer",
                    transition: "all 0.15s",
                    background: active ? "rgba(0,0,0,0.05)" : "transparent",
                    border: active ? "1px solid rgba(0,0,0,0.11)" : "1px solid transparent",
                  }}
                >
                  {/* Icon pill */}
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 10,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      background: active ? "rgba(0,0,0,0.09)" : "rgba(0,0,0,0.02)",
                      transition: "all 0.15s",
                    }}
                  >
                    <Icon
                      style={{
                        width: 15,
                        height: 15,
                        color: active ? "#111827" : "rgba(100,116,139,0.7)",
                        transition: "color 0.15s",
                      }}
                    />
                  </div>

                  <div style={{ minWidth: 0, flex: 1 }}>
                    <p
                      style={{
                        fontSize: 15,
                        fontWeight: 600,
                        color: active ? "#111827" : "rgba(100,116,139,0.9)",
                        margin: 0,
                        lineHeight: 1.2,
                        fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)",
                        transition: "color 0.15s",
                      }}
                    >
                      {item.label}
                    </p>
                    <p
                      style={{
                        fontSize: 11,
                        color: active ? "rgba(0,0,0,0.30)" : "rgba(71,85,105,0.8)",
                        margin: "2px 0 0",
                        lineHeight: 1.3,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {item.desc}
                    </p>
                  </div>

                  {active && (
                    <div
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        background: "#111827",
                        flexShrink: 0,
                      }}
                    />
                  )}
                </motion.div>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom section */}
      <div style={{ borderTop: "1px solid rgba(0,0,0,0.03)", flexShrink: 0 }}>
        {/* Active document picker */}
        <div style={{ padding: "10px 12px 4px" }}>
          <p style={{ fontSize: 9, fontWeight: 700, color: "rgba(100,116,139,0.5)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>
            Active Document
          </p>
          {documents.length === 0 ? (
            <Link href="/upload" style={{ textDecoration: "none" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 7, padding: "7px 10px", borderRadius: 10, border: "1px dashed rgba(0,0,0,0.06)", cursor: "pointer" }}>
                <Upload style={{ width: 12, height: 12, color: "rgba(71,85,105,0.7)", flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: "rgba(71,85,105,0.7)" }}>Upload a document</span>
              </div>
            </Link>
          ) : (
            <select
              value={selectedDoc?.id ?? ""}
              onChange={(e) => {
                const doc = documents.find((d) => d.id === e.target.value);
                setSelectedDoc(doc ?? null);
              }}
              style={{
                width: "100%",
                padding: "6px 10px",
                borderRadius: 10,
                border: "1px solid rgba(0,0,0,0.15)",
                background: "rgba(0,0,0,0.04)",
                color: "#111827",
                fontSize: 11,
                fontWeight: 600,
                cursor: "pointer",
                appearance: "none",
                outline: "none",
              }}
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id} style={{ background: "#ffffff", color: "#111827" }}>
                  {d.filename.length > 28 ? d.filename.slice(0, 26) + "…" : d.filename}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* ⌘K search trigger */}
        <div style={{ padding: "12px 12px 4px" }}>
          <button
            onClick={onCmdK}
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 12px",
              borderRadius: 12,
              border: "1px solid rgba(0,0,0,0.04)",
              background: "rgba(0,0,0,0.02)",
              cursor: "pointer",
              transition: "all 0.15s",
              textAlign: "left",
            }}
          >
            <Search style={{ width: 13, height: 13, color: "rgba(71,85,105,0.8)", flexShrink: 0 }} />
            <span style={{ flex: 1, fontSize: 12, color: "rgba(71,85,105,0.8)" }}>Search actions...</span>
            <div style={{ display: "flex", gap: 2, flexShrink: 0 }}>
              <kbd
                style={{
                  fontSize: 9,
                  padding: "2px 5px",
                  borderRadius: 4,
                  background: "rgba(0,0,0,0.03)",
                  border: "1px solid rgba(0,0,0,0.05)",
                  color: "rgba(71,85,105,0.9)",
                  fontFamily: "monospace",
                }}
              >
                ⌘
              </kbd>
              <kbd
                style={{
                  fontSize: 9,
                  padding: "2px 5px",
                  borderRadius: 4,
                  background: "rgba(0,0,0,0.03)",
                  border: "1px solid rgba(0,0,0,0.05)",
                  color: "rgba(71,85,105,0.9)",
                  fontFamily: "monospace",
                }}
              >
                K
              </kbd>
            </div>
          </button>
        </div>

        {/* Agent status pill */}
        <div style={{ padding: "8px 12px", borderBottom: "1px solid rgba(0,0,0,0.03)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 12px",
              borderRadius: 10,
              background: "rgba(52,211,153,0.06)",
              border: "1px solid rgba(52,211,153,0.12)",
            }}
          >
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
              style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", flexShrink: 0 }}
            />
            <span style={{ fontSize: 12, color: "#34d399", fontWeight: 600 }}>5 agents operational</span>
          </div>
        </div>

        {/* Org card */}
        <div style={{ padding: "8px 12px 12px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "8px 10px",
              borderRadius: 12,
              cursor: "pointer",
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 10,
                background: "rgba(0,0,0,0.04)",
                border: "1px solid rgba(0,0,0,0.07)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Building2 style={{ width: 15, height: 15, color: "#111827" }} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: "rgba(17,24,39,0.9)",
                  margin: 0,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  fontFamily: "var(--font-heading, sans-serif)",
                }}
              >
                Cotiviti Health
              </p>
              <p
                style={{
                  fontSize: 11,
                  color: "rgba(71,85,105,0.9)",
                  margin: "2px 0 0",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                Enterprise POC
              </p>
            </div>
            <span
              style={{
                fontSize: 9,
                padding: "2px 6px",
                borderRadius: 6,
                background: "rgba(0,0,0,0.06)",
                color: "#111827",
                border: "1px solid rgba(0,0,0,0.12)",
                fontWeight: 700,
                letterSpacing: "0.05em",
                flexShrink: 0,
              }}
            >
              POC
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
