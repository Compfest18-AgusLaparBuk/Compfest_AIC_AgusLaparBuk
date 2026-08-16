"use client";

import { useCallback, useRef, useState } from "react";

interface UploadZoneProps {
  label: string;
  subLabel: string;
  accept?: string;
  file: File | null;
  previewUrl: string | null;
  onFileSelect: (file: File, previewUrl: string) => void;
  id: string;
}

export default function UploadZone({
  label,
  subLabel,
  accept = "image/*",
  file,
  previewUrl,
  onFileSelect,
  id,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (selected: File) => {
      const url = URL.createObjectURL(selected);
      onFileSelect(selected, url);
    },
    [onFileSelect]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-widest text-indigo-400">
          {label}
        </span>
        <span className="text-xs text-slate-500">{subLabel}</span>
      </div>

      <div
        role="button"
        tabIndex={0}
        id={id}
        aria-label={`Upload ${label}`}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`
          relative min-h-[220px] rounded-2xl border-2 border-dashed transition-all duration-300
          flex flex-col items-center justify-center gap-4 cursor-pointer overflow-hidden
          ${
            isDragging
              ? "border-indigo-400 bg-indigo-950/40 scale-[1.02]"
              : file
              ? "border-indigo-500/50 bg-slate-800/60"
              : "border-slate-600/50 bg-slate-800/30 hover:border-indigo-500/50 hover:bg-slate-800/50"
          }
        `}
      >
        {previewUrl ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={previewUrl}
              alt={`Preview ${label}`}
              className="w-full h-full object-contain max-h-[200px] rounded-xl"
            />
            <div className="absolute bottom-2 right-2 bg-indigo-600/90 text-white text-xs px-2 py-1 rounded-lg backdrop-blur-sm">
              ✓ Tersedia
            </div>
          </>
        ) : (
          <>
            <div
              className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                isDragging ? "bg-indigo-600/40 scale-110" : "bg-slate-700/60"
              }`}
            >
              <svg
                className={`w-7 h-7 transition-colors duration-300 ${
                  isDragging ? "text-indigo-300" : "text-slate-400"
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                />
              </svg>
            </div>
            <div className="text-center px-4">
              <p className="text-sm text-slate-300 font-medium">
                {isDragging ? "Lepaskan file di sini" : "Seret & lepas atau klik"}
              </p>
              <p className="text-xs text-slate-500 mt-1">PNG, JPG, WEBP hingga 10MB</p>
            </div>
          </>
        )}
      </div>

      {file && (
        <div className="flex items-center gap-2 px-1">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-slate-400 truncate">{file.name}</span>
          <span className="text-xs text-slate-600 ml-auto shrink-0">
            {(file.size / 1024).toFixed(0)} KB
          </span>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={onInputChange}
        aria-hidden="true"
      />
    </div>
  );
}
