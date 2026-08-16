"""
Extraction module — document field extractor.

PUBLIC INTERFACE
----------------
    extract_document(image: np.ndarray, doc_type: str) -> ExtractedDocument

The function above is the only entry point that the rest of the application
should call. Swapping in a real OCR/vision-language model means replacing the
body of this function (or its internal delegation) without changing any
call sites upstream.

CURRENT IMPLEMENTATION
-----------------------
This scaffold uses a deterministic mock that returns pre-defined data so the
reconciliation engine can be exercised end-to-end immediately.

# TODO: replace _mock_extraction with a real fine-tuned vision-language model.
        The model should accept a preprocessed np.ndarray and return a dict
        conforming to ExtractedDocument. See STUB_INTERFACE.md (to be created
        when a real model is integrated) for the exact contract.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from schemas.document import DocumentItem, ExtractedDocument

# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def extract_document(
    image: np.ndarray,
    doc_type: Literal["surat_jalan", "invoice"],
) -> ExtractedDocument:
    """
    Extract structured fields from a preprocessed document image.

    Args:
        image:    Preprocessed image from preprocessing.image_processor.preprocess_image().
                  Shape: (H, W, 3), dtype: uint8, BGR channel order.
        doc_type: Either "surat_jalan" or "invoice".

    Returns:
        ExtractedDocument populated with fields from the document.

    Notes:
        - Currently delegates to _mock_extraction().
        # TODO: replace with fine-tuned vision-language model (e.g., PaddleOCR + LLM,
        #       TrOCR, or a fine-tuned VLM) when available.
        #       The model call should follow the signature:
        #           raw_text = ocr_model.run(image)          # → str
        #           fields = vlm_extractor.extract(raw_text) # → dict
        #       then pass `fields` to ExtractedDocument(**fields).
    """
    # TODO: replace with fine-tuned model
    return _mock_extraction(doc_type)


# ---------------------------------------------------------------------------
# Stub / mock implementation
# ---------------------------------------------------------------------------

# These two data dictionaries intentionally differ on qty (SKU-001) and
# alamat_tujuan so that the reconciliation engine will flag MISMATCH_DETECTED
# during a normal demo run.
#
# Scenario A (MISMATCH):  surat_jalan vs invoice → used when both uploads exist
# Scenario B (APPROVED):  would require identical data; can be tested directly
#                          via the reconciliation unit tests.

_MOCK_SURAT_JALAN: dict = {
    "doc_type": "surat_jalan",
    "doc_id": "SJ-2024-00142",
    "pengirim": "PT Maju Bersama Logistik",
    "penerima": "CV Sumber Makmur",
    "alamat_tujuan": "Jl. Industri Raya No. 45, Kawasan Berikat, Cakung, Jakarta Timur",
    "items": [
        {"sku": "SKU-001", "qty": 100, "berat_kg": 250.0},
        {"sku": "SKU-002", "qty": 50,  "berat_kg": 75.5},
    ],
    "total_harga": 15_000_000,
}

_MOCK_INVOICE: dict = {
    "doc_type": "invoice",
    "doc_id": "INV-2024-00389",
    "pengirim": "PT Maju Bersama Logistik",
    "penerima": "CV Sumber Makmur",
    # Intentional mismatch: different district suffix
    "alamat_tujuan": "Jl. Industri Raya No. 45, Kawasan Berikat, Cakung, Jakarta Utara",
    "items": [
        # Intentional mismatch: qty 80 vs 100
        {"sku": "SKU-001", "qty": 80,  "berat_kg": 250.0},
        {"sku": "SKU-002", "qty": 50,  "berat_kg": 75.5},
    ],
    "total_harga": 15_000_000,
}


def _mock_extraction(doc_type: Literal["surat_jalan", "invoice"]) -> ExtractedDocument:
    """
    Return a hard-coded ExtractedDocument for scaffold demonstration.

    # TODO: replace with fine-tuned model
    """
    data = _MOCK_SURAT_JALAN if doc_type == "surat_jalan" else _MOCK_INVOICE
    return ExtractedDocument(
        doc_type=data["doc_type"],  # type: ignore[arg-type]
        doc_id=data["doc_id"],
        pengirim=data["pengirim"],
        penerima=data["penerima"],
        alamat_tujuan=data["alamat_tujuan"],
        items=[DocumentItem(**item) for item in data["items"]],
        total_harga=data["total_harga"],
    )
