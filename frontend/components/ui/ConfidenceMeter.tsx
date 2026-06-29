"use client";

import { motion } from "framer-motion";
import { cn, formatConfidence } from "@/lib/utils";

interface ConfidenceMeterProps {
  score: number;
  label?: string;
  showBar?: boolean;
  className?: string;
}

export function ConfidenceMeter({ score, label = "Confidence Score", showBar = true, className }: ConfidenceMeterProps) {
  const pct = Math.round(score * 100);

  const barGradient =
    pct >= 85
      ? "linear-gradient(90deg, #0ea5e9, #34d399)"
      : pct >= 65
      ? "linear-gradient(90deg, #f59e0b, #fbbf24)"
      : "linear-gradient(90deg, #ef4444, #f87171)";

  const scoreColor =
    pct >= 85 ? "#34d399" : pct >= 65 ? "#fbbf24" : "#f87171";

  return (
    <div className={cn("space-y-1.5", className)}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: "rgba(100,116,139,0.8)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
          }}
        >
          {label}
        </span>
        <span
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: scoreColor,
          }}
        >
          {formatConfidence(score)}
        </span>
      </div>

      {showBar && (
        <div
          style={{
            height: 6,
            background: "rgba(255,255,255,0.06)",
            borderRadius: 99,
            overflow: "hidden",
          }}
        >
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            style={{
              height: "100%",
              borderRadius: 99,
              background: barGradient,
            }}
          />
        </div>
      )}
    </div>
  );
}
