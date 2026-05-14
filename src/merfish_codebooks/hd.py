"""Hamming distance evaluation between codes (vectorised).

Port of `EvaluateCodebookHD.R`, but operating on uint64 bitmasks. The R version computes
HD via `(A + A_i) %% 2` row-sums, which is row-by-row and per-bit; this version computes
the full N×N HD matrix in two C-level operations: an outer XOR and a vectorised popcount.

For very large N, prefer `evaluate_hd_columns(codes, indices)` to compute only the
columns you need.
"""

from __future__ import annotations

import numpy as np

from .bitmask import popcount_array


def evaluate_hd_matrix(codes: np.ndarray) -> np.ndarray:
    """Pairwise Hamming distance matrix for a uint64 mask array.

    Returns
    -------
    HD : (N, N) ndarray of uint8 (HD ≤ 64 fits in a byte).
    """
    codes = np.asarray(codes, dtype=np.uint64)
    xor = codes[:, None] ^ codes[None, :]
    return popcount_array(xor).astype(np.uint8)


def evaluate_hd_row(codes: np.ndarray, i: int) -> np.ndarray:
    """Hamming distance from `codes[i]` to every code (length-N vector)."""
    codes = np.asarray(codes, dtype=np.uint64)
    return popcount_array(codes ^ codes[i]).astype(np.uint8)


def validate_min_hd(codes: np.ndarray, min_hd: int) -> tuple[bool, int]:
    """Return (ok, n_violations). ok is True iff every off-diagonal pair has HD ≥ min_hd."""
    codes = np.asarray(codes, dtype=np.uint64)
    n = len(codes)
    if n <= 1:
        return True, 0
    HD = evaluate_hd_matrix(codes)
    bad = (HD < min_hd) & (~np.eye(n, dtype=bool))
    n_violations = int(bad.sum() // 2)
    return n_violations == 0, n_violations
