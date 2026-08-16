"""
FastAPI entry point — Surat Jalan Auditor API.

Endpoints
---------
GET  /health              → liveness probe (used by Docker healthcheck)
POST /api/reconcile       → main pipeline: upload 2 images → extract → reconcile
"""

from __future__ import annotations

import io
from typing import Annotated

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from extraction.extractor import extract_document
from preprocessing.image_processor import preprocess_image
from reconciliation.engine import reconcile
from schemas.document import ReconciliationResult

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Surat Jalan Auditor API",
    description=(
        "AI-powered reconciliation of Surat Jalan and Invoice documents. "
        "Scaffold version — extraction uses stub data; reconciliation is fully implemented."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Liveness probe used by Docker Compose healthcheck."""
    return {"status": "ok"}


@app.post(
    "/api/reconcile",
    response_model=ReconciliationResult,
    summary="Upload and reconcile documents",
    tags=["reconciliation"],
)
async def api_reconcile(
    surat_jalan: Annotated[UploadFile, File(description="Surat Jalan image (JPEG/PNG)")],
    invoice: Annotated[UploadFile, File(description="Invoice image (JPEG/PNG)")],
) -> ReconciliationResult:
    """
    Main pipeline endpoint.

    Accepts two document images via multipart/form-data, runs them through the
    preprocessing → extraction → reconciliation pipeline, and returns a structured
    ReconciliationResult.

    **Scaffold note**: The extraction step currently uses mock data (see
    `extraction/extractor.py`). The reconciliation logic is fully implemented.
    """
    # --- Read uploaded files ---
    sj_bytes = await surat_jalan.read()
    inv_bytes = await invoice.read()

    if not sj_bytes:
        raise HTTPException(status_code=400, detail="surat_jalan file is empty.")
    if not inv_bytes:
        raise HTTPException(status_code=400, detail="invoice file is empty.")

    # --- Preprocessing ---
    try:
        sj_image: np.ndarray = preprocess_image(sj_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=f"Could not process surat_jalan image: {exc}"
        ) from exc

    try:
        inv_image: np.ndarray = preprocess_image(inv_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=f"Could not process invoice image: {exc}"
        ) from exc

    # --- Extraction (stub) ---
    # TODO: replace with fine-tuned model — see extraction/extractor.py
    sj_doc = extract_document(sj_image, "surat_jalan")
    inv_doc = extract_document(inv_image, "invoice")

    # --- Reconciliation (full implementation) ---
    result = reconcile(sj_doc, inv_doc)

    return result
