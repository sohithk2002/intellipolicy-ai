"use client";

import { ReactNode } from "react";
import { motion } from "framer-motion";

interface PageHeroProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  action?: ReactNode;
  gradient?: string;
}

export function PageHero({ eyebrow, title, subtitle, action, gradient = "#d1d5db" }: PageHeroProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      style={{
        position: "relative",
        borderBottom: "1px solid rgba(0,0,0,0.03)",
        marginBottom: 32,
        overflow: "hidden",
      }}
    >
      {/* Subtle radial blob background */}
      <div
        style={{
          position: "absolute",
          top: -40,
          left: -40,
          width: 300,
          height: 220,
          borderRadius: "50%",
          background: gradient,
          opacity: 0.08,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          maxWidth: 1400,
          margin: "0 auto",
          padding: "48px 40px",
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 32,
          position: "relative",
        }}
      >
        <div style={{ flex: 1, minWidth: 0 }}>
          {eyebrow && (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "4px 12px",
                borderRadius: 20,
                background: `${gradient}14`,
                border: `1px solid ${gradient}28`,
                marginBottom: 14,
              }}
            >
              <div
                style={{
                  width: 5,
                  height: 5,
                  borderRadius: "50%",
                  background: gradient,
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: gradient,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  fontFamily: "var(--font-body, Inter, sans-serif)",
                }}
              >
                {eyebrow}
              </span>
            </div>
          )}

          <h1
            style={{
              fontSize: "clamp(2rem, 3.5vw, 2.75rem)",
              fontWeight: 900,
              color: "#111827",
              letterSpacing: "-0.03em",
              lineHeight: 1.08,
              margin: 0,
              fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)",
            }}
          >
            {title}
          </h1>

          {subtitle && (
            <p
              style={{
                fontSize: 15,
                color: "rgba(148,163,184,0.9)",
                marginTop: 12,
                lineHeight: 1.7,
                maxWidth: 600,
              }}
            >
              {subtitle}
            </p>
          )}
        </div>

        {action && (
          <div style={{ flexShrink: 0, paddingTop: 8 }}>
            {action}
          </div>
        )}
      </div>
    </motion.div>
  );
}
