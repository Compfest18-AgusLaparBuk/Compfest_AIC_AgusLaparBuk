"""
Pydantic schemas for Surat Jalan Auditor API.
These models define the data contract between extraction, reconciliation, and the frontend.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Document-level models
# ---------------------------------------------------------------------------


class DocumentItem(BaseModel):
    """Represents a single line item on a document."""

    sku: str = Field(..., description="Stock Keeping Unit identifier")
    qty: int = Field(..., ge=0, description="Quantity of the item")
    berat_kg: float = Field(..., ge=0.0, description="Weight in kilograms")


class ExtractedDocument(BaseModel):
    """Structured data extracted from a single document (Surat Jalan or Invoice)."""

    doc_type: Literal["surat_jalan", "invoice"]
    doc_id: str = Field(..., description="Document number / reference ID")
    pengirim: str = Field(..., description="Sender name or company")
    penerima: str = Field(..., description="Recipient name or company")
    alamat_tujuan: str = Field(..., description="Delivery destination address")
    items: list[DocumentItem] = Field(default_factory=list)
    total_harga: int = Field(..., ge=0, description="Total price in IDR (integer)")


# ---------------------------------------------------------------------------
# Reconciliation result models
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MismatchDetail(BaseModel):
    """Describes a single field discrepancy between Surat Jalan and Invoice."""

    field: str = Field(..., description="Name of the mismatched field")
    surat_jalan_value: str = Field(..., description="Value from Surat Jalan")
    invoice_value: str = Field(..., description="Value from Invoice")
    severity: Severity


class ExtractedPair(BaseModel):
    """Container holding both extracted documents."""

    surat_jalan: ExtractedDocument
    invoice: ExtractedDocument


class ReconciliationResult(BaseModel):
    """Final API response returned to the frontend."""

    status: Literal["CLEARANCE_APPROVED", "MISMATCH_DETECTED"]
    mismatches: list[MismatchDetail] = Field(default_factory=list)
    extracted: ExtractedPair
