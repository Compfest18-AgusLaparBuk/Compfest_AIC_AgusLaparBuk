"use client";

import { useState, useCallback } from "react";
import UploadZone from "@/components/UploadZone";
import ResultPanel from "@/components/ResultPanel";
import { ReconciliationResult } from "@/types/api";

type AppState = "idle" | "loading" | "success" | "error";

export default function Home() {
  const [sjFile, setSjFile] = useState<File | null>(null);
  const [sjPreview, setSjPreview] = useState<string | null>(null);
  const [invFile, setInvFile] = useState<File | null>(null);
  const [invPreview, setInvPreview] = useState<string | null>(null);
  const [appState, setAppState] = useState<AppState>("idle");
  const [result, setResult] = useState<ReconciliationResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSjSelect = useCallback((file: File, url: string) => {
    setSjFile(file);
    setSjPreview(url);
    setResult(null);
    setAppState("idle");
  }, []);

  const handleInvSelect = useCallback((file: File, url: string) => {
    setInvFile(file);
    setInvPreview(url);
    setResult(null);
    setAppState("idle");
  }, []);

  const handleSubmit = async () => {
    if (!sjFile || !invFile) return;

    setAppState("loading");
    setResult(null);
    setErrorMessage(null);

    try {
      const form = new FormData();
      form.append("surat_jalan", sjFile);
      form.append("invoice", invFile);

      const res = await fetch("/api/reconcile", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data: ReconciliationResult = await res.json();
      setResult(data);
      setAppState("success");

      // Scroll to result
      setTimeout(() => {
        document.getElementById("result-panel")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Terjadi kesalahan yang tidak diketahui."
      );
      setAppState("error");
    }
  };

  const canSubmit = !!sjFile && !!invFile && appState !== "loading";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 antialiased">
      {/* Ambient background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-900/20 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-violet-900/15 blur-[100px]" />
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <header className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 mb-4">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
            <span className="text-xs font-medium text-indigo-300 tracking-wide uppercase">
              Smart Logistics · AI Reconciliation
            </span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-br from-white via-slate-200 to-slate-400 bg-clip-text text-transparent leading-tight">
            Surat Jalan Auditor
          </h1>
          <p className="mt-3 text-slate-400 max-w-xl mx-auto text-base">
            Unggah <span className="text-slate-200 font-medium">Surat Jalan</span> dan{" "}
            <span className="text-slate-200 font-medium">Invoice</span> untuk verifikasi
            otomatis sebelum barang meninggalkan gudang.
          </p>
        </header>

        {/* Upload Card */}
        <main>
          <section
            aria-label="Upload dokumen"
            className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-6 sm:p-8 shadow-2xl mb-8"
          >
            <h2 className="text-base font-semibold text-slate-200 mb-6 flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-300 text-xs font-bold">
                1
              </span>
              Pilih Dokumen
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <UploadZone
                id="upload-surat-jalan"
                label="Surat Jalan"
                subLabel="Dokumen pengiriman dari gudang"
                file={sjFile}
                previewUrl={sjPreview}
                onFileSelect={handleSjSelect}
              />
              <UploadZone
                id="upload-invoice"
                label="Invoice"
                subLabel="Faktur tagihan dari supplier"
                file={invFile}
                previewUrl={invPreview}
                onFileSelect={handleInvSelect}
              />
            </div>

            {/* Submit */}
            <div className="mt-8 flex flex-col items-center gap-3">
              <button
                id="btn-rekonsiliasi"
                onClick={handleSubmit}
                disabled={!canSubmit}
                className={`
                  relative w-full max-w-sm py-4 rounded-2xl font-semibold text-base transition-all duration-300
                  ${
                    canSubmit
                      ? "bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-900/40 hover:shadow-indigo-900/60 hover:scale-[1.02] active:scale-[0.98]"
                      : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50"
                  }
                `}
              >
                {appState === "loading" ? (
                  <span className="flex items-center justify-center gap-3">
                    <svg
                      className="animate-spin h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      />
                    </svg>
                    Memproses Dokumen…
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                    Rekonsiliasi Dokumen
                  </span>
                )}
              </button>

              {!sjFile && !invFile && (
                <p className="text-xs text-slate-600">
                  Unggah kedua dokumen untuk mengaktifkan rekonsiliasi
                </p>
              )}
              {(sjFile || invFile) && (!sjFile || !invFile) && (
                <p className="text-xs text-amber-500/80">
                  {!sjFile ? "Surat Jalan belum diunggah" : "Invoice belum diunggah"}
                </p>
              )}
            </div>
          </section>

          {/* Error state */}
          {appState === "error" && errorMessage && (
            <div
              role="alert"
              id="error-message"
              className="bg-red-950/50 border border-red-500/30 rounded-2xl px-6 py-4 mb-8 flex items-start gap-3"
            >
              <svg
                className="w-5 h-5 text-red-400 shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                />
              </svg>
              <div>
                <p className="text-sm font-semibold text-red-300">Gagal memproses</p>
                <p className="text-sm text-red-400/80 mt-0.5">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Result panel */}
          {appState === "success" && result && (
            <section aria-label="Hasil rekonsiliasi">
              <div className="flex items-center gap-3 mb-5">
                <div className="h-px flex-1 bg-slate-700/50" />
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-500 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-300 text-xs font-bold">
                    2
                  </span>
                  Hasil Rekonsiliasi
                </span>
                <div className="h-px flex-1 bg-slate-700/50" />
              </div>
              <ResultPanel
                result={result}
                sjPreviewUrl={sjPreview}
                invPreviewUrl={invPreview}
              />
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 text-center text-xs text-slate-700">
          <p>
            Scaffold v0.1 ·{" "}
            <span className="text-slate-600">
              Extraction: mock stub · Reconciliation: fully implemented
            </span>
          </p>
        </footer>
      </div>
    </div>
  );
}
