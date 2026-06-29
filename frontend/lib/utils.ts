import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function getConfidenceColor(score: number): string {
  if (score >= 0.85) return "text-emerald-400";
  if (score >= 0.65) return "text-amber-400";
  return "text-red-400";
}

export function getConfidenceBg(score: number): string {
  if (score >= 0.85) return "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
  if (score >= 0.65) return "bg-amber-500/10 border-amber-500/20 text-amber-400";
  return "bg-red-500/10 border-red-500/20 text-red-400";
}

export function getRiskColor(risk: string): string {
  switch (risk?.toLowerCase()) {
    case "low": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    case "medium": return "text-amber-400 bg-amber-500/10 border-amber-500/20";
    case "high": return "text-red-400 bg-red-500/10 border-red-500/20";
    default: return "text-slate-400 bg-slate-500/10 border-slate-500/20";
  }
}

export function getDecisionColor(decision: string): string {
  switch (decision?.toLowerCase()) {
    case "approved": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    case "denied": return "text-red-400 bg-red-500/10 border-red-500/20";
    case "needs review": return "text-amber-400 bg-amber-500/10 border-amber-500/20";
    default: return "text-slate-400 bg-slate-500/10 border-slate-500/20";
  }
}
