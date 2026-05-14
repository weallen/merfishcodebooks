"""Per-codebook validators: Hamming weight, minimum HD, and per-round bit balance.

A MERFISH codebook is a set of N binary codes of length v. The three properties this
module quantifies:

* **Hamming weight (HW)**: every code has exactly `hw` "on" bits.
* **Minimum Hamming distance (minHD)**: every pair of codes differs in at least
  `min_hd` positions.
* **Bit balance across rounds**: each of the v bit positions (one per imaging round)
  is "on" in roughly the same number of codes. With N codes of weight k the per-round
  ideal load is N*k/v; the column sums of the N×v binary matrix should bracket that.

`validate_codebook` returns a `CodebookValidation` record covering all three.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np

from .bitmask import masks_to_binary, popcount_array
from .hd import evaluate_hd_matrix
from .io import read_codebook_csv


@dataclass
class CodebookValidation:
    """Aggregated validation result for a single codebook."""

    path: str
    v: int
    n_codes: int

    hw_expected: int
    hw_min: int
    hw_max: int
    hw_pass: bool

    min_hd_expected: int
    min_hd_observed: int
    min_hd_pass: bool
    min_hd_n_violations: int

    bit_counts: list[int]
    bit_count_mean: float
    bit_count_min: int
    bit_count_max: int
    bit_count_spread: int            # max - min
    bit_count_std: float
    bit_balance_pass: bool           # spread <= 1 (the tightest achievable bound)
    bit_balance_chi_square: float    # Σ((obs - expected)² / expected)

    @property
    def all_pass(self) -> bool:
        return self.hw_pass and self.min_hd_pass and self.bit_balance_pass

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _binary_matrix(masks: np.ndarray, v: int) -> np.ndarray:
    return masks_to_binary(masks, v)


def validate_codebook(
    masks: np.ndarray,
    *,
    v: int,
    hw: int,
    min_hd: int,
    path: str | Path = "",
) -> CodebookValidation:
    """Validate a codebook represented as uint64 bitmasks.

    Parameters
    ----------
    masks : (N,) uint64 array of bitmasks.
    v : barcode length (number of rounds).
    hw : expected Hamming weight of every code.
    min_hd : required minimum pairwise Hamming distance.
    path : optional source path, recorded in the result for reporting.
    """
    masks = np.asarray(masks, dtype=np.uint64)
    n = int(len(masks))

    # --- Hamming weight ---
    weights = popcount_array(masks).astype(np.int64)
    if n:
        hw_min = int(weights.min())
        hw_max = int(weights.max())
    else:
        hw_min = hw_max = 0
    hw_pass = bool(n and hw_min == hw and hw_max == hw)

    # --- Minimum Hamming distance ---
    if n >= 2:
        HD = evaluate_hd_matrix(masks)
        iu = np.triu_indices(n, k=1)
        off = HD[iu]
        min_hd_observed = int(off.min())
        min_hd_n_violations = int((off < min_hd).sum())
    else:
        min_hd_observed = 0
        min_hd_n_violations = 0
    min_hd_pass = n < 2 or min_hd_observed >= min_hd

    # --- Bit balance across rounds (columns of N×v binary matrix) ---
    binary = _binary_matrix(masks, v) if n else np.zeros((0, v), dtype=np.uint8)
    bit_counts = binary.sum(axis=0).astype(np.int64)
    expected = (n * hw) / v if v else 0.0
    if n:
        bc_min = int(bit_counts.min())
        bc_max = int(bit_counts.max())
        bc_std = float(bit_counts.std(ddof=0))
        spread = bc_max - bc_min
    else:
        bc_min = bc_max = 0
        bc_std = 0.0
        spread = 0
    # The tightest physically achievable spread when N*hw is not divisible by v is 1
    # (some bits get ⌈N*hw/v⌉ uses, the rest ⌊N*hw/v⌋). Allow spread ≤ 1 to pass.
    bit_balance_pass = bool(n == 0 or spread <= 1)
    if expected > 0:
        chi2 = float(np.sum((bit_counts - expected) ** 2 / expected))
    else:
        chi2 = 0.0

    return CodebookValidation(
        path=str(path),
        v=v,
        n_codes=n,
        hw_expected=hw,
        hw_min=hw_min,
        hw_max=hw_max,
        hw_pass=hw_pass,
        min_hd_expected=min_hd,
        min_hd_observed=min_hd_observed,
        min_hd_pass=min_hd_pass,
        min_hd_n_violations=min_hd_n_violations,
        bit_counts=bit_counts.tolist(),
        bit_count_mean=float(bit_counts.mean()) if n else 0.0,
        bit_count_min=bc_min,
        bit_count_max=bc_max,
        bit_count_spread=int(spread),
        bit_count_std=bc_std,
        bit_balance_pass=bit_balance_pass,
        bit_balance_chi_square=chi2,
    )


def validate_codebook_file(
    path: str | Path,
    *,
    v: int,
    hw: int,
    min_hd: int,
) -> CodebookValidation:
    """Read a codebook CSV (binary or set form) and validate it."""
    masks = read_codebook_csv(path)
    return validate_codebook(masks, v=v, hw=hw, min_hd=min_hd, path=path)
