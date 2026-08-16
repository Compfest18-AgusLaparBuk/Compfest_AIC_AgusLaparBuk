// Type definitions matching the backend's Pydantic schemas

export interface DocumentItem {
  sku: string;
  qty: number;
  berat_kg: number;
}

export interface ExtractedDocument {
  doc_type: "surat_jalan" | "invoice";
  doc_id: string;
  pengirim: string;
  penerima: string;
  alamat_tujuan: string;
  items: DocumentItem[];
  total_harga: number;
}

export type Severity = "high" | "medium" | "low";

export interface MismatchDetail {
  field: string;
  surat_jalan_value: string;
  invoice_value: string;
  severity: Severity;
}

export interface ExtractedPair {
  surat_jalan: ExtractedDocument;
  invoice: ExtractedDocument;
}

export interface ReconciliationResult {
  status: "CLEARANCE_APPROVED" | "MISMATCH_DETECTED";
  mismatches: MismatchDetail[];
  extracted: ExtractedPair;
}
