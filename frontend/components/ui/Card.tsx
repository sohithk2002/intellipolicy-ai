"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

// ── GlassCard ──────────────────────────────────────────────────────────────────
interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export function GlassCard({ children, className, style, onClick }: GlassCardProps) {
  return (
    <motion.div
      whileHover={{
        y: -2,
        borderColor: "rgba(255,255,255,0.11)",
        boxShadow: "0 8px 40px rgba(0,0,0,0.35), 0 1px 0 rgba(255,255,255,0.04) inset",
      }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      onClick={onClick}
      style={{
        background: "radial-gradient(120% 80% at 50% 0%, rgba(255,255,255,0.025) 0%, rgba(9,15,30,0.82) 70%)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 20,
        backdropFilter: "blur(20px)",
        boxShadow: "0 1px 3px rgba(0,0,0,0.25), 0 4px 20px rgba(0,0,0,0.18)",
        cursor: onClick ? "pointer" : undefined,
        ...style,
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// ── StatCard ───────────────────────────────────────────────────────────────────
interface StatCardProps {
  value: string;
  label: string;
  delta?: string;
  icon?: React.ElementType;
  from?: string;
  to?: string;
  glow?: string;
}

export function StatCard({ value, label, delta, icon: Icon, from = "#0ea5e9", to = "#6366f1", glow }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -3, borderColor: "rgba(255,255,255,0.12)" }}
      transition={{ duration: 0.2 }}
      style={{
        position: "relative",
        borderRadius: 16,
        padding: 20,
        border: "1px solid rgba(255,255,255,0.07)",
        overflow: "hidden",
        background: `linear-gradient(135deg, ${from}10, ${to}07)`,
        boxShadow: glow ? `0 0 24px ${glow}` : undefined,
        backdropFilter: "blur(20px)",
        cursor: "pointer",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 16 }}>
        {Icon && (
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: `${from}1a`,
              border: `1px solid ${from}28`,
            }}
          >
            <Icon style={{ width: 20, height: 20, color: from }} />
          </div>
        )}
      </div>

      <p
        style={{
          fontSize: 30,
          fontWeight: 900,
          color: "white",
          letterSpacing: "-0.02em",
          lineHeight: 1,
          margin: 0,
          fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)",
        }}
      >
        {value}
      </p>
      <p style={{ fontSize: 13, color: "rgba(148,163,184,0.8)", marginTop: 4, fontWeight: 500 }}>{label}</p>
      {delta && (
        <p style={{ fontSize: 12, color: from, marginTop: 8, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {delta}
        </p>
      )}
    </motion.div>
  );
}

// ── Legacy exports for backward compatibility ──────────────────────────────────
interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  hover?: boolean;
}

export function Card({ children, className, glow, hover }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-white/8 bg-[#0d1525]/80 backdrop-blur-sm",
        glow && "glow-blue",
        hover && "card-hover cursor-pointer",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("p-5 border-b border-white/5", className)}>
      {children}
    </div>
  );
}

export function CardContent({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("p-5", className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <h3 className={cn("text-sm font-semibold text-slate-200", className)}>
      {children}
    </h3>
  );
}
