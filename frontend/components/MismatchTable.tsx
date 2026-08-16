"use client";

import { MismatchDetail, Severity } from "@/types/api";

interface MismatchTableProps {
  mismatches: MismatchDetail[];
}

const SEVERITY_CONFIG: Record<
  Severity,
  { label: string; badgeClass: string; rowClass: string }
> = {
  high: {
    label: "TINGGI",
    badgeClass: "bg-red-500/20 text-red-300 border border-red-500/30",
    rowClass: "border-l-2 border-red-500/60",
  },
  medium: {
    label: "SEDANG",
    badgeClass: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
    rowClass: "border-l-2 border-amber-500/60",
  },
  low: {
    label: "RENDAH",
    badgeClass: "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30",
    rowClass: "border-l-2 border-yellow-500/60",
  },
};

export default function MismatchTable({ mismatches }: MismatchTableProps) {
  if (mismatches.length === 0) return null;

  // Sort: high → medium → low
  const sorted = [...mismatches].sort((a, b) => {
    const order: Record<Severity, number> = { high: 0, medium: 1, low: 2 };
    return order[a.severity] - order[b.severity];
  });

  return (
    <div id="mismatch-table" className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-400">
          Rincian Ketidaksesuaian
        </h2>
        <span className="bg-red-500/20 text-red-300 text-xs font-bold px-2.5 py-0.5 rounded-full border border-red-500/30">
          {mismatches.length} field
        </span>
      </div>

      <div className="rounded-xl overflow-hidden border border-slate-700/50">
        {/* Header */}
        <div className="grid grid-cols-[1fr_1.5fr_1.5fr_auto] gap-4 px-5 py-3 bg-slate-800/80 border-b border-slate-700/50">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Field</span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Nilai Surat Jalan
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Nilai Invoice
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Prioritas
          </span>
        </div>

        {/* Rows */}
        <div className="divide-y divide-slate-700/30">
          {sorted.map((mismatch, idx) => {
            const cfg = SEVERITY_CONFIG[mismatch.severity];
            return (
              <div
                key={idx}
                className={`grid grid-cols-[1fr_1.5fr_1.5fr_auto] gap-4 px-5 py-4 bg-slate-800/40 ${cfg.rowClass} hover:bg-slate-800/70 transition-colors duration-150`}
              >
                {/* Field name */}
                <div className="flex items-start">
                  <code className="text-xs bg-slate-700/60 text-indigo-300 px-2 py-1 rounded font-mono break-all">
                    {mismatch.field}
                  </code>
                </div>

                {/* SJ value */}
                <div className="flex items-start">
                  <span className="text-sm text-slate-200 leading-relaxed">
                    {mismatch.surat_jalan_value}
                  </span>
                </div>

                {/* Invoice value */}
                <div className="flex items-start gap-2">
                  <svg
                    className="w-4 h-4 text-red-400 shrink-0 mt-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  <span className="text-sm text-red-300 leading-relaxed">
                    {mismatch.invoice_value}
                  </span>
                </div>

                {/* Severity badge */}
                <div className="flex items-start justify-end">
                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-full ${cfg.badgeClass} whitespace-nowrap`}
                  >
                    {cfg.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
