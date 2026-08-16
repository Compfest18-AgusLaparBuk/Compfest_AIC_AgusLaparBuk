"""
Reconciliation Engine — full implementation (not a stub).

Compares two ExtractedDocument objects (Surat Jalan vs Invoice) and produces a
ReconciliationResult with an exhaustive list of mismatches.

Comparison rules
----------------
Field           | Method          | Threshold / Notes
----------------|-----------------|--------------------------------------------------
pengirim        | fuzzy (str)     | rapidfuzz token_sort_ratio ≥ FUZZY_THRESHOLD
penerima        | fuzzy (str)     | same
alamat_tujuan   | fuzzy (str)     | same (addresses often have abbreviations)
items[].qty     | exact (int)     | per SKU; extra/missing SKUs flagged separately
items[].berat_kg| numeric range   | |sj - inv| ≤ BERAT_KG_TOLERANCE
total_harga     | exact (int)     | full match required

Severity mapping
----------------
qty             → high
total_harga     → high
alamat_tujuan   → medium
pengirim        → medium
penerima        → medium
berat_kg        → low
missing_sku     → high

Environment variables (override defaults via .env)
--------------------------------------------------
FUZZY_THRESHOLD     (int,   default 85)   — min similarity score for string fields
BERAT_KG_TOLERANCE  (float, default 0.5)  — max allowed berat_kg difference in kg
"""

from __future__ import annotations

import os
from typing import Callable

from rapidfuzz import fuzz

from schemas.document import (
    ExtractedDocument,
    ExtractedPair,
    MismatchDetail,
    ReconciliationResult,
    Severity,
)

# ---------------------------------------------------------------------------
# Configuration (overridable via environment variables)
# ---------------------------------------------------------------------------

FUZZY_THRESHOLD: int = int(os.getenv("FUZZY_THRESHOLD", "85"))
BERAT_KG_TOLERANCE: float = float(os.getenv("BERAT_KG_TOLERANCE", "0.5"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def reconcile(
    sj: ExtractedDocument,
    inv: ExtractedDocument,
) -> ReconciliationResult:
    """
    Compare Surat Jalan and Invoice and return a ReconciliationResult.

    Args:
        sj:  Extracted data from the Surat Jalan document.
        inv: Extracted data from the Invoice document.

    Returns:
        ReconciliationResult with status CLEARANCE_APPROVED or MISMATCH_DETECTED,
        and a list of MismatchDetail objects for every discrepancy found.
    """
    mismatches: list[MismatchDetail] = []

    # 1. String fields (fuzzy)
    mismatches.extend(_compare_string(sj, inv, "pengirim", Severity.MEDIUM))
    mismatches.extend(_compare_string(sj, inv, "penerima", Severity.MEDIUM))
    mismatches.extend(_compare_string(sj, inv, "alamat_tujuan", Severity.MEDIUM))

    # 2. Numeric field — total_harga (exact)
    mismatches.extend(_compare_exact(sj, inv, "total_harga", Severity.HIGH))

    # 3. Line items (per SKU)
    mismatches.extend(_compare_items(sj, inv))

    status = "CLEARANCE_APPROVED" if not mismatches else "MISMATCH_DETECTED"

    return ReconciliationResult(
        status=status,  # type: ignore[arg-type]
        mismatches=mismatches,
        extracted=ExtractedPair(surat_jalan=sj, invoice=inv),
    )


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------


def _compare_string(
    sj: ExtractedDocument,
    inv: ExtractedDocument,
    field: str,
    severity: Severity,
) -> list[MismatchDetail]:
    """
    Compare a string attribute using rapidfuzz token_sort_ratio.

    token_sort_ratio normalises word order before scoring, which handles
    common address/name variations like "PT ABC Logistik" vs "Logistik PT ABC".
    """
    sj_val: str = str(getattr(sj, field, "") or "").strip()
    inv_val: str = str(getattr(inv, field, "") or "").strip()

    score = fuzz.token_sort_ratio(sj_val.lower(), inv_val.lower())
    if score < FUZZY_THRESHOLD:
        return [
            MismatchDetail(
                field=field,
                surat_jalan_value=sj_val,
                invoice_value=inv_val,
                severity=severity,
            )
        ]
    return []


def _compare_exact(
    sj: ExtractedDocument,
    inv: ExtractedDocument,
    field: str,
    severity: Severity,
) -> list[MismatchDetail]:
    """Compare a field that must match exactly (numeric or string)."""
    sj_val = getattr(sj, field)
    inv_val = getattr(inv, field)
    if sj_val != inv_val:
        return [
            MismatchDetail(
                field=field,
                surat_jalan_value=str(sj_val),
                invoice_value=str(inv_val),
                severity=severity,
            )
        ]
    return []


def _compare_items(
    sj: ExtractedDocument,
    inv: ExtractedDocument,
) -> list[MismatchDetail]:
    """
    Compare line items by SKU.

    Strategy:
    - Build a dict of {sku: item} for each document.
    - For each SKU present in either document:
        * If missing from one side → flag as missing_sku (high severity).
        * If present in both → compare qty (exact) and berat_kg (tolerance).
    """
    mismatches: list[MismatchDetail] = []

    sj_items = {item.sku: item for item in sj.items}
    inv_items = {item.sku: item for item in inv.items}

    all_skus = set(sj_items.keys()) | set(inv_items.keys())

    for sku in sorted(all_skus):
        sj_item = sj_items.get(sku)
        inv_item = inv_items.get(sku)

        if sj_item is None:
            mismatches.append(
                MismatchDetail(
                    field=f"items[{sku}].sku",
                    surat_jalan_value="(not found)",
                    invoice_value=sku,
                    severity=Severity.HIGH,
                )
            )
            continue

        if inv_item is None:
            mismatches.append(
                MismatchDetail(
                    field=f"items[{sku}].sku",
                    surat_jalan_value=sku,
                    invoice_value="(not found)",
                    severity=Severity.HIGH,
                )
            )
            continue

        # qty — exact match
        if sj_item.qty != inv_item.qty:
            mismatches.append(
                MismatchDetail(
                    field=f"items[{sku}].qty",
                    surat_jalan_value=str(sj_item.qty),
                    invoice_value=str(inv_item.qty),
                    severity=Severity.HIGH,
                )
            )

        # berat_kg — tolerance-based
        if abs(sj_item.berat_kg - inv_item.berat_kg) > BERAT_KG_TOLERANCE:
            mismatches.append(
                MismatchDetail(
                    field=f"items[{sku}].berat_kg",
                    surat_jalan_value=str(sj_item.berat_kg),
                    invoice_value=str(inv_item.berat_kg),
                    severity=Severity.LOW,
                )
            )

    return mismatches
