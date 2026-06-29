"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { Document } from "./types";
import { api } from "./api";

interface DocCtx {
  documents: Document[];
  selectedDoc: Document | null;
  setSelectedDoc: (d: Document | null) => void;
  refreshDocs: () => Promise<void>;
}

const DocumentContext = createContext<DocCtx>({
  documents: [],
  selectedDoc: null,
  setSelectedDoc: () => {},
  refreshDocs: async () => {},
});

const STORAGE_KEY = "intellipolicy_selected_doc_id";

function getSavedDocId(): string | null {
  try {
    return typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
  } catch {
    return null;
  }
}

function saveDocId(id: string | null) {
  try {
    if (typeof window === "undefined") return;
    if (id) localStorage.setItem(STORAGE_KEY, id);
    else localStorage.removeItem(STORAGE_KEY);
  } catch {}
}

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDocState] = useState<Document | null>(null);

  const refreshDocs = useCallback(async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
      setSelectedDocState((prev) => {
        // 1. Keep current selection if still valid
        if (prev && docs.find((d) => d.id === prev.id)) return prev;
        // 2. Restore from localStorage
        const savedId = getSavedDocId();
        if (savedId) {
          const saved = docs.find((d) => d.id === savedId && d.status === "ready");
          if (saved) return saved;
        }
        // 3. Auto-pick first ready doc
        return docs.find((d) => d.status === "ready") ?? docs[0] ?? null;
      });
    } catch {}
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshDocs();
  }, [refreshDocs]);

  const setSelectedDoc = (d: Document | null) => {
    setSelectedDocState(d);
    saveDocId(d?.id ?? null);
  };

  return (
    <DocumentContext.Provider value={{ documents, selectedDoc, setSelectedDoc, refreshDocs }}>
      {children}
    </DocumentContext.Provider>
  );
}

export const useDocumentContext = () => useContext(DocumentContext);
