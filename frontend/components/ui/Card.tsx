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
        borderColor: "rgba(0,0,0,0.12)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)",
      }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      onClick={onClick}
      style={{
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.07)",
        borderRadius: 20,
        boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)",
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

export function StatCard({ value, label, delta, icon: Icon, from = "#374151", to = "#6b7280" }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2, borderColor: "rgba(0,0,0,0.12)", boxShadow: "0 6px 24px rgba(0,0,0,0.08)" }}
      transition={{ duration: 0.2 }}
      style={{
        position: "relative",
        borderRadius: 16,
        padding: 20,
        border: "1px solid rgba(0,0,0,0.07)",
        overflow: "hidden",
        background: "#ffffff",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
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
              background: "rgba(0,0,0,0.05)",
              border: "1px solid rgba(0,0,0,0.08)",
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
          color: "#111827",
          letterSpacing: "-0.02em",
          lineHeight: 1,
          margin: 0,
          fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)",
        }}
      >
        {value}
      </p>
      <p style={{ fontSize: 13, color: "#6b7280", marginTop: 4, fontWeight: 500 }}>{label}</p>
      {delta && (
        <p style={{ fontSize: 12, color: from, marginTop: 8, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {delta}
        </p>
      )}
    </motion.div>
  );
}

// ── Legacy Card components ─────────────────────────────────────────────────────
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
        "rounded-xl border border-black/7 bg-white",
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
    <div className={cn("p-5 border-b border-black/6", className)}>
      {children}
    </div>
  );
}

export function CardContent({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("p-5", className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <h3 className={cn("text-sm font-semibold text-gray-800", className)}>
      {children}
    </h3>
  );
}
