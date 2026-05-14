"""uint64 bitmask utilities for MERFISH codes.

A code with v <= 64 bits and Hamming weight k is stored as a single uint64 where bit i
corresponds to position i+1 (1-indexed externally for parity with the R reference).

Speed-critical helpers (popcount, pair-conflict check) are JIT-compiled with Numba so
the inner loops in `exchange.py` run at native speed.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
from numba import njit

MAX_BITS = 64

_M1 = np.uint64(0x5555555555555555)
_M2 = np.uint64(0x3333333333333333)
_M4 = np.uint64(0x0F0F0F0F0F0F0F0F)
_H01 = np.uint64(0x0101010101010101)


# ---------------------------------------------------------------------------
# Popcount: SWAR (SIMD-within-a-register) — fast, branchless, dependency-free.
# Modern LLVM/Numba lowers this pattern to hardware POPCNT on x86-64 with SSE4.2.
# ---------------------------------------------------------------------------

@njit(cache=True, inline="always")
def popcount64(x: np.uint64) -> np.uint64:
    x = np.uint64(x)
    x = x - ((x >> np.uint64(1)) & _M1)
    x = (x & _M2) + ((x >> np.uint64(2)) & _M2)
    x = (x + (x >> np.uint64(4))) & _M4
    return (x * _H01) >> np.uint64(56)


def popcount_array(arr: np.ndarray) -> np.ndarray:
    """Vectorised popcount over a uint64 ndarray (SWAR algorithm).

    Returns a uint64 ndarray of the same shape.
    """
    if arr.dtype != np.uint64:
        arr = arr.astype(np.uint64)
    x = arr
    x = x - ((x >> np.uint64(1)) & _M1)
    x = (x & _M2) + ((x >> np.uint64(2)) & _M2)
    x = (x + (x >> np.uint64(4))) & _M4
    return (x * _H01) >> np.uint64(56)


# ---------------------------------------------------------------------------
# Mask construction and decoding.
# ---------------------------------------------------------------------------

def encode_set(bits: Iterable[int]) -> np.uint64:
    """Convert a 1-indexed iterable of bit positions to a uint64 bitmask."""
    mask = np.uint64(0)
    for b in bits:
        if b < 1 or b > MAX_BITS:
            raise ValueError(f"Bit position {b} out of range [1, {MAX_BITS}]")
        mask |= np.uint64(1) << np.uint64(b - 1)
    return mask


def decode_set(mask: np.uint64, *, sort: bool = True) -> tuple[int, ...]:
    """Convert a uint64 bitmask back to a 1-indexed tuple of bit positions."""
    m = int(mask)
    out: list[int] = []
    i = 1
    while m:
        if m & 1:
            out.append(i)
        m >>= 1
        i += 1
    return tuple(sorted(out)) if sort else tuple(out)


def encode_set_array(sets: Sequence[Sequence[int]]) -> np.ndarray:
    """Convert an N×k integer matrix of 1-indexed positions to an N-vector of uint64."""
    arr = np.asarray(sets, dtype=np.int64)
    if arr.ndim != 2:
        raise ValueError("encode_set_array expects a 2-D array of (N, k) shape.")
    if arr.size and (arr.min() < 1 or arr.max() > MAX_BITS):
        raise ValueError(f"Bit positions must lie in [1, {MAX_BITS}]; got [{arr.min()}, {arr.max()}].")
    masks = np.zeros(arr.shape[0], dtype=np.uint64)
    for col in range(arr.shape[1]):
        masks |= np.uint64(1) << (arr[:, col].astype(np.uint64) - np.uint64(1))
    return masks


def decode_set_array(masks: np.ndarray, k: int) -> np.ndarray:
    """Convert an N-vector of uint64 to an N×k matrix of 1-indexed positions (sorted)."""
    out = np.zeros((len(masks), k), dtype=np.int64)
    for i, m in enumerate(masks):
        positions = decode_set(np.uint64(m))
        if len(positions) != k:
            raise ValueError(f"Mask {int(m):#x} has weight {len(positions)}, expected {k}.")
        out[i] = positions
    return out


# ---------------------------------------------------------------------------
# Binary matrix <-> bitmask vector.
# ---------------------------------------------------------------------------

def binary_to_masks(binary: np.ndarray) -> np.ndarray:
    """Convert an N×v 0/1 matrix to an N-vector of uint64 bitmasks (1-indexed bits)."""
    binary = np.asarray(binary)
    if binary.ndim != 2:
        raise ValueError("binary_to_masks expects an (N, v) matrix.")
    n, v = binary.shape
    if v > MAX_BITS:
        raise ValueError(f"Barcode length v={v} exceeds {MAX_BITS}.")
    masks = np.zeros(n, dtype=np.uint64)
    bit_weights = (np.uint64(1) << np.arange(v, dtype=np.uint64))
    masks = (binary.astype(np.uint64) * bit_weights[None, :]).sum(axis=1, dtype=np.uint64)
    return masks


def masks_to_binary(masks: np.ndarray, v: int) -> np.ndarray:
    """Convert an N-vector of uint64 bitmasks to an N×v 0/1 matrix."""
    if v > MAX_BITS:
        raise ValueError(f"Barcode length v={v} exceeds {MAX_BITS}.")
    masks = np.asarray(masks, dtype=np.uint64)
    out = np.zeros((len(masks), v), dtype=np.uint8)
    for b in range(v):
        out[:, b] = ((masks >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
    return out


# ---------------------------------------------------------------------------
# t-set enumeration (k-1 subsets of a code, for minHD=4).
# ---------------------------------------------------------------------------

@njit(cache=True)
def tsets_of_kset_minhd4(kset_mask: np.uint64, k: int) -> np.ndarray:
    """Return the k t-sets of a k-set under minHD=4 (drop one bit at a time).

    For a code with bits {b_1, ..., b_k}, the k t-sets are obtained by removing each
    bit in turn. Result is a length-k uint64 array.
    """
    out = np.empty(k, dtype=np.uint64)
    m = kset_mask
    i = 0
    bit = np.uint64(0)
    while m != 0 and i < k:
        if m & np.uint64(1):
            out[i] = kset_mask & ~(np.uint64(1) << bit)
            i += 1
        m >>= np.uint64(1)
        bit += np.uint64(1)
    return out


@njit(cache=True)
def tsets_of_codes_minhd4(codes: np.ndarray, k: int) -> np.ndarray:
    """Return all (N*k) t-sets of an N-vector of k-set masks; flattened."""
    n = codes.shape[0]
    out = np.empty(n * k, dtype=np.uint64)
    for i in range(n):
        ts = tsets_of_kset_minhd4(codes[i], k)
        for j in range(k):
            out[i * k + j] = ts[j]
    return out


# ---------------------------------------------------------------------------
# All-combinations enumeration.
# ---------------------------------------------------------------------------

def all_kset_masks(v: int, k: int) -> np.ndarray:
    """Return a uint64 array of every k-element subset of {1..v} as a bitmask.

    Implementation note: emits masks in lexicographic order over the bit-position tuples,
    which matches the R `combn(1:v, k)` ordering when each tuple is sorted ascending.
    """
    if v > MAX_BITS:
        raise ValueError(f"v={v} exceeds {MAX_BITS}.")
    from math import comb
    n = comb(v, k)
    out = np.empty(n, dtype=np.uint64)
    # Iterative combination generator (Knuth Algorithm L variant).
    idx = list(range(k))
    for i in range(n):
        m = np.uint64(0)
        for p in idx:
            m |= np.uint64(1) << np.uint64(p)
        out[i] = m
        # advance
        j = k - 1
        while j >= 0 and idx[j] == v - k + j:
            j -= 1
        if j < 0:
            break
        idx[j] += 1
        for h in range(j + 1, k):
            idx[h] = idx[h - 1] + 1
    return out


# ---------------------------------------------------------------------------
# Pair-conflict kernel (used by the exchange loop's pair-swap phase).
# ---------------------------------------------------------------------------

@njit(cache=True)
def find_compatible_pair(masks: np.ndarray, t: int) -> tuple[int, int]:
    """Find any pair (i, j) in `masks` with popcount(masks[i] & masks[j]) < t.

    Returns (-1, -1) if no compatible pair exists. This is the inner kernel of the
    double-ghost pair-swap step; with Numba it runs at native speed and exits early
    on the first hit, which is the common case for typical candidate-list sizes.
    """
    n = masks.shape[0]
    for i in range(n - 1):
        a = masks[i]
        for j in range(i + 1, n):
            if popcount64(a & masks[j]) < t:
                return i, j
    return -1, -1
