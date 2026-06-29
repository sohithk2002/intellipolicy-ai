import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Inter, JetBrains_Mono } from "next/font/google";
import { DocumentProvider } from "@/lib/DocumentContext";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-code",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "IntelliPolicy AI — Agentic Healthcare Policy Intelligence",
  description: "Traceable agentic AI platform for healthcare policy intelligence, claims validation, and audit-ready rule extraction.",
  keywords: ["healthcare AI", "policy intelligence", "claims validation", "prior authorization", "audit trail"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${jakarta.variable} ${inter.variable} ${jetbrains.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-[#04070f] text-[#e2e8f7]">
        <DocumentProvider>{children}</DocumentProvider>
      </body>
    </html>
  );
}
