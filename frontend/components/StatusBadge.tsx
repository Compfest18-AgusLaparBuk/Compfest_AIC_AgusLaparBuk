"use client";

interface StatusBadgeProps {
  status: "CLEARANCE_APPROVED" | "MISMATCH_DETECTED";
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const isApproved = status === "CLEARANCE_APPROVED";

  return (
    <div
      id="status-badge"
      className={`
        relative flex items-center gap-4 rounded-2xl px-8 py-6 overflow-hidden
        transition-all duration-500
        ${
          isApproved
            ? "bg-emerald-950/60 border border-emerald-500/30"
            : "bg-red-950/60 border border-red-500/30"
        }
      `}
    >
      {/* Glow effect */}
      <div
        className={`absolute inset-0 opacity-10 blur-3xl -z-10 rounded-2xl ${
          isApproved ? "bg-emerald-400" : "bg-red-500"
        }`}
      />

      {/* Icon */}
      <div
        className={`w-14 h-14 rounded-xl flex items-center justify-center shrink-0 ${
          isApproved
            ? "bg-emerald-500/20 text-emerald-400"
            : "bg-red-500/20 text-red-400"
        }`}
      >
        {isApproved ? (
          <svg
            className="w-8 h-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        ) : (
          <svg
            className="w-8 h-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        )}
      </div>

      {/* Text */}
      <div>
        <p
          className={`text-2xl font-bold tracking-tight ${
            isApproved ? "text-emerald-300" : "text-red-300"
          }`}
        >
          {isApproved ? "CLEARANCE APPROVED" : "MISMATCH DETECTED"}
        </p>
        <p className="text-sm mt-0.5 text-slate-400">
          {isApproved
            ? "Semua field cocok — dokumen siap diproses."
            : "Ditemukan ketidaksesuaian — tinjau rincian di bawah sebelum memproses."}
        </p>
      </div>

      {/* Animated pulse ring */}
      <div
        className={`ml-auto shrink-0 relative w-4 h-4 ${
          isApproved ? "text-emerald-400" : "text-red-400"
        }`}
      >
        <span
          className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${
            isApproved ? "bg-emerald-400" : "bg-red-400"
          }`}
        />
        <span
          className={`relative inline-flex rounded-full h-4 w-4 ${
            isApproved ? "bg-emerald-400" : "bg-red-400"
          }`}
        />
      </div>
    </div>
  );
}
