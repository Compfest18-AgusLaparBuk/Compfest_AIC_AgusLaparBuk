"""
Unit tests for the reconciliation engine.

Two scenarios as required by the Definition of Done:

  Scenario 1 — CLEARANCE_APPROVED
    Both documents have identical data → no mismatches.

  Scenario 2 — MISMATCH_DETECTED
    Documents differ on qty (SKU-001: 100 vs 80) and alamat_tujuan
    (different city district suffix) → two mismatches flagged.

Run with:
    cd backend
    pytest reconciliation/test_engine.py -v
"""

from __future__ import annotations

import sys
import os

# Allow imports from the backend root (schemas, reconciliation)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from schemas.document import DocumentItem, ExtractedDocument
from reconciliation.engine import reconcile


# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------


def _make_sj(
    alamat: str = "Jl. Industri Raya No. 45, Cakung, Jakarta Timur",
    qty_sku001: int = 100,
    total_harga: int = 15_000_000,
) -> ExtractedDocument:
    return ExtractedDocument(
        doc_type="surat_jalan",
        doc_id="SJ-2024-00142",
        pengirim="PT Maju Bersama Logistik",
        penerima="CV Sumber Makmur",
        alamat_tujuan=alamat,
        items=[
            DocumentItem(sku="SKU-001", qty=qty_sku001, berat_kg=250.0),
            DocumentItem(sku="SKU-002", qty=50,         berat_kg=75.5),
        ],
        total_harga=total_harga,
    )


def _make_inv(
    alamat: str = "Jl. Industri Raya No. 45, Cakung, Jakarta Timur",
    qty_sku001: int = 100,
    total_harga: int = 15_000_000,
) -> ExtractedDocument:
    return ExtractedDocument(
        doc_type="invoice",
        doc_id="INV-2024-00389",
        pengirim="PT Maju Bersama Logistik",
        penerima="CV Sumber Makmur",
        alamat_tujuan=alamat,
        items=[
            DocumentItem(sku="SKU-001", qty=qty_sku001, berat_kg=250.0),
            DocumentItem(sku="SKU-002", qty=50,         berat_kg=75.5),
        ],
        total_harga=total_harga,
    )


# ---------------------------------------------------------------------------
# Scenario 1 — CLEARANCE_APPROVED
# ---------------------------------------------------------------------------


class TestClearanceApproved:
    def test_status_is_clearance_approved(self):
        result = reconcile(_make_sj(), _make_inv())
        assert result.status == "CLEARANCE_APPROVED"

    def test_no_mismatches(self):
        result = reconcile(_make_sj(), _make_inv())
        assert result.mismatches == []

    def test_extracted_pair_preserved(self):
        sj = _make_sj()
        inv = _make_inv()
        result = reconcile(sj, inv)
        assert result.extracted.surat_jalan.doc_id == sj.doc_id
        assert result.extracted.invoice.doc_id == inv.doc_id

    def test_fuzzy_name_variation_passes(self):
        """Minor capitalization or spacing differences should still pass."""
        sj = _make_sj()
        inv = _make_inv()
        inv.pengirim = "PT  MAJU BERSAMA LOGISTIK"  # extra space + uppercase
        result = reconcile(sj, inv)
        # Should still be approved — fuzzy matching handles this
        assert result.status == "CLEARANCE_APPROVED"


# ---------------------------------------------------------------------------
# Scenario 2 — MISMATCH_DETECTED
# ---------------------------------------------------------------------------


class TestMismatchDetected:
    def test_status_is_mismatch_detected(self):
        sj = _make_sj(qty_sku001=100)
        inv = _make_inv(qty_sku001=80)
        result = reconcile(sj, inv)
        assert result.status == "MISMATCH_DETECTED"

    def test_qty_mismatch_flagged(self):
        sj = _make_sj(qty_sku001=100)
        inv = _make_inv(qty_sku001=80)
        result = reconcile(sj, inv)
        qty_mismatch = next(
            (m for m in result.mismatches if "SKU-001" in m.field and "qty" in m.field),
            None,
        )
        assert qty_mismatch is not None
        assert qty_mismatch.surat_jalan_value == "100"
        assert qty_mismatch.invoice_value == "80"
        assert qty_mismatch.severity == "high"

    def test_address_mismatch_flagged(self):
        sj = _make_sj(alamat="Jl. Industri Raya No. 45, Cakung, Jakarta Timur")
        inv = _make_inv(alamat="Jl. Industri Raya No. 45, Cakung, Bandung")  # diff city
        result = reconcile(sj, inv)
        addr_mismatch = next(
            (m for m in result.mismatches if m.field == "alamat_tujuan"), None
        )
        assert addr_mismatch is not None
        assert addr_mismatch.severity == "medium"

    def test_total_harga_mismatch_flagged(self):
        sj = _make_sj(total_harga=15_000_000)
        inv = _make_inv(total_harga=12_000_000)
        result = reconcile(sj, inv)
        harga_mismatch = next(
            (m for m in result.mismatches if m.field == "total_harga"), None
        )
        assert harga_mismatch is not None
        assert harga_mismatch.severity == "high"

    def test_missing_sku_flagged(self):
        """An SKU present in SJ but missing in Invoice should be HIGH severity."""
        sj = _make_sj()
        inv = _make_inv()
        # Remove SKU-002 from invoice
        inv.items = [item for item in inv.items if item.sku != "SKU-002"]
        result = reconcile(sj, inv)
        missing = next(
            (m for m in result.mismatches if "SKU-002" in m.field), None
        )
        assert missing is not None
        assert missing.severity == "high"

    def test_multiple_mismatches_all_returned(self):
        """All mismatches should be returned, not just the first one."""
        sj = _make_sj(
            alamat="Jl. Industri Raya No. 45, Cakung, Jakarta Timur",
            qty_sku001=100,
            total_harga=15_000_000,
        )
        inv = _make_inv(
            alamat="Jl. Raya Industri No. 45, Bandung Barat",  # very different
            qty_sku001=80,
            total_harga=12_000_000,
        )
        result = reconcile(sj, inv)
        fields = [m.field for m in result.mismatches]
        assert any("qty" in f for f in fields)
        assert "total_harga" in fields
        assert "alamat_tujuan" in fields
        assert len(result.mismatches) >= 3
