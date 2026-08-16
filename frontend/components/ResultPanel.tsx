"use client";

import { ExtractedDocument, ReconciliationResult } from "@/types/api";
import MismatchTable from "./MismatchTable";
import StatusBadge from "./StatusBadge";

interface ResultPanelProps {
  result: ReconciliationResult;
  sjPreviewUrl: string | null;
  invPreviewUrl: string | null;
}

function DocumentCard({
  doc,
  title,
  previewUrl,
}: {
  doc: ExtractedDocument;
  title: string;
  previewUrl: string | null;
}) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl bg-slate-800/50 border border-slate-700/50 p-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-widest text-indigo-400">
          {title}
        </span>
        <span className="text-xs text-slate-500 font-mono">{doc.doc_id}</span>
      </div>

      {/* Image thumbnail */}
      {previewUrl && (
        <div className="rounded-xl overflow-hidden border border-slate-700/50 bg-slate-900/40">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt={`Preview ${title}`}
            className="w-full object-contain max-h-48"
          />
        </div>
      )}

      {/* Extracted fields */}
      <div className="flex flex-col gap-2.5">
        <Field label="Pengirim" value={doc.pengirim} />
        <Field label="Penerima" value={doc.penerima} />
        <Field label="Alamat Tujuan" value={doc.alamat_tujuan} />
        <Field
          label="Total Harga"
          value={`Rp ${doc.total_harga.toLocaleString("id-ID")}`}
        />

        {/* Items */}
        <div className="mt-1">
          <span className="text-xs text-slate-500 uppercase tracking-wider font-medium block mb-2">
            Line Items
          </span>
          <div className="flex flex-col gap-1.5">
            {doc.items.map((item) => (
              <div
                key={item.sku}
                className="flex items-center justify-between bg-slate-900/50 rounded-lg px-3 py-2"
              >
                <code className="text-xs text-indigo-300 font-mono">
                  {item.sku}
                </code>
                <div className="flex gap-3 text-xs text-slate-400">
                  <span>
                    <span className="text-slate-300 font-medium">{item.qty}</span> unit
                  </span>
                  <span>
                    <span className="text-slate-300 font-medium">{item.berat_kg}</span> kg
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">
        {label}
      </span>
      <span className="text-sm text-slate-200 leading-relaxed">{value}</span>
    </div>
  );
}

export default function ResultPanel({
  result,
  sjPreviewUrl,
  invPreviewUrl,
}: ResultPanelProps) {
  return (
    <div
      id="result-panel"
      className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500"
    >
      {/* Status */}
      <StatusBadge status={result.status} />

      {/* Split view: SJ document | Invoice document */}
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-400 mb-3">
          Data Terekstraksi
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DocumentCard
            doc={result.extracted.surat_jalan}
            title="Surat Jalan"
            previewUrl={sjPreviewUrl}
          />
          <DocumentCard
            doc={result.extracted.invoice}
            title="Invoice"
            previewUrl={invPreviewUrl}
          />
        </div>
      </div>

      {/* Mismatch details */}
      {result.mismatches.length > 0 && (
        <MismatchTable mismatches={result.mismatches} />
      )}

      {result.status === "CLEARANCE_APPROVED" && (
        <div className="text-center py-4">
          <p className="text-sm text-emerald-400/80">
            ✓ Semua{" "}
            {Object.keys(result.extracted.surat_jalan).length} field diperiksa
            — tidak ada selisih ditemukan.
          </p>
        </div>
      )}
    </div>
  );
}
