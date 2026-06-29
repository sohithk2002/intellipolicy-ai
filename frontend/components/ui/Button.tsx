"use client";

import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
}

const heights = { sm: 36, md: 40, lg: 44 };
const fontSizes = { sm: 13, md: 14, lg: 15 };
const paddings = { sm: "0 14px", md: "0 20px", lg: "0 24px" };

function getVariantStyles(variant: string): React.CSSProperties {
  switch (variant) {
    case "primary":
      return {
        background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
        color: "white",
        border: "none",
        boxShadow: "0 2px 12px rgba(14,165,233,0.22)",
      };
    case "secondary":
      return {
        background: "rgba(255,255,255,0.05)",
        color: "rgba(226,232,240,0.9)",
        border: "1px solid rgba(255,255,255,0.1)",
        backdropFilter: "blur(8px)",
      };
    case "ghost":
      return {
        background: "transparent",
        color: "rgba(203,213,225,0.9)",
        border: "1px solid transparent",
      };
    case "danger":
      return {
        background: "rgba(248,113,113,0.1)",
        color: "#f87171",
        border: "1px solid rgba(248,113,113,0.2)",
      };
    case "outline":
      return {
        background: "rgba(255,255,255,0.03)",
        color: "#38bdf8",
        border: "1px solid rgba(56,189,248,0.3)",
        backdropFilter: "blur(8px)",
      };
    default:
      return {
        background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
        color: "white",
        border: "none",
        boxShadow: "0 2px 12px rgba(14,165,233,0.22)",
      };
  }
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  style,
  disabled,
  ...props
}: ButtonProps) {
  const variantStyle = getVariantStyles(variant);

  const baseStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: size === "sm" ? 6 : size === "lg" ? 10 : 8,
    height: heights[size],
    padding: paddings[size],
    borderRadius: 12,
    fontSize: fontSizes[size],
    fontWeight: 600,
    letterSpacing: "-0.02em",
    cursor: disabled || loading ? "not-allowed" : "pointer",
    opacity: disabled || loading ? 0.5 : 1,
    transition: "all 0.2s",
    fontFamily: "var(--font-body, Inter, sans-serif)",
    whiteSpace: "nowrap",
    flexShrink: 0,
    ...variantStyle,
    ...style,
  };

  return (
    <motion.button
      whileHover={
        disabled || loading
          ? {}
          : variant === "primary"
          ? {
              y: -2,
              boxShadow: "0 6px 24px rgba(14,165,233,0.32)",
            }
          : variant === "secondary"
          ? { background: "rgba(255,255,255,0.08)", borderColor: "rgba(255,255,255,0.18)" }
          : variant === "ghost"
          ? { background: "rgba(255,255,255,0.05)" }
          : variant === "danger"
          ? { background: "rgba(248,113,113,0.18)" }
          : variant === "outline"
          ? { background: "rgba(14,165,233,0.08)", borderColor: "rgba(56,189,248,0.5)" }
          : {}
      }
      whileTap={disabled || loading ? {} : { scale: 0.98 }}
      disabled={disabled || loading}
      style={baseStyle}
      {...(props as React.ComponentPropsWithoutRef<typeof motion.button>)}
    >
      {loading ? (
        <Loader2 style={{ width: 15, height: 15, animation: "spin 1s linear infinite" }} />
      ) : icon ? (
        icon
      ) : null}
      {children}
    </motion.button>
  );
}
