"""Binary <-> set-form <-> bitmask conversions.

Ports of `ConvertBinarytoSet.R` and `ConvertSettoBinary.R`. Set form uses 1-indexed
bit positions to maintain CSV parity with the R reference.
"""

from __future__ import annotations

import numpy as np

from .bitmask import (
    binary_to_masks,
    decode_set_array,
    encode_set_array,
    masks_to_binary,
)


def binary_to_set(binary: np.ndarray) -> np.ndarray:
    """Convert an N×v 0/1 matrix to an N×k matrix of 1-indexed bit positions."""
    binary = np.asarray(binary)
    if binary.ndim != 2:
        raise ValueError("binary_to_set expects an (N, v) matrix.")
    k = int(binary.sum(axis=1).max()) if binary.size else 0
    if binary.size and not (binary.sum(axis=1) == k).all():
        raise ValueError("All rows must have the same Hamming weight.")
    out = np.zeros((binary.shape[0], k), dtype=np.int64)
    for i, row in enumerate(binary):
        out[i] = np.flatnonzero(row) + 1
    return out


def set_to_binary(sets: np.ndarray, bits: int | None = None) -> np.ndarray:
    """Convert an N×k matrix of 1-indexed bit positions to an N×v 0/1 matrix.

    If `bits` is None, infers v from the maximum bit position used. Pass `bits` if your
    starting set doesn't happen to use the highest position.
    """
    sets = np.asarray(sets, dtype=np.int64)
    if sets.ndim != 2:
        raise ValueError("set_to_binary expects an (N, k) matrix.")
    if bits is None:
        bits = int(sets.max()) if sets.size else 0
    n = sets.shape[0]
    out = np.zeros((n, bits), dtype=np.uint8)
    for i in range(n):
        out[i, sets[i] - 1] = 1
    return out


# Re-exports of bitmask <-> matrix helpers, for convenience.
__all__ = [
    "binary_to_set",
    "set_to_binary",
    "binary_to_masks",
    "masks_to_binary",
    "encode_set_array",
    "decode_set_array",
]
