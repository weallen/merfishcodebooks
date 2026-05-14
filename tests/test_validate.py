"""Tests for the codebook validator."""

import numpy as np
import pytest

from merfish_codebooks.bitmask import encode_set
from merfish_codebooks.validate import validate_codebook


# A perfectly balanced (v=9, hw=4, minHD=4) codebook of size 18 — Steiner-system
# derived; every bit position is "on" in exactly 18*4/9 = 8 codes. This matches
# codebooks_hw4_minhd4/v09/.
BALANCED_V9_HW4 = [
    [1, 2, 3, 7],
    [1, 2, 4, 5],
    [1, 2, 8, 9],
    [1, 3, 5, 8],
    [1, 3, 6, 9],
    [1, 4, 6, 8],
    [1, 4, 7, 9],
    [1, 5, 6, 7],
    [2, 3, 4, 8],
    [2, 3, 5, 6],
    [2, 4, 6, 9],
    [2, 5, 7, 9],
    [2, 6, 7, 8],
    [3, 4, 5, 9],
    [3, 4, 6, 7],
    [3, 7, 8, 9],
    [4, 5, 7, 8],
    [5, 6, 8, 9],
]


def _masks(sets):
    return np.array([encode_set(s) for s in sets], dtype=np.uint64)


def test_balanced_codebook_passes_all():
    masks = _masks(BALANCED_V9_HW4)
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)

    assert r.n_codes == 18
    assert r.hw_pass and r.hw_min == 4 and r.hw_max == 4
    assert r.min_hd_pass and r.min_hd_observed >= 4 and r.min_hd_n_violations == 0
    assert r.bit_balance_pass
    assert r.bit_count_min == 8 and r.bit_count_max == 8
    assert r.bit_count_spread == 0
    assert r.bit_balance_chi_square == pytest.approx(0.0)
    assert r.all_pass


def test_hw_mismatch_detected():
    # Add a weight-3 row to break the HW invariant.
    masks = np.concatenate([_masks(BALANCED_V9_HW4), _masks([[1, 2, 3]])])
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)
    assert not r.hw_pass
    assert r.hw_min == 3
    assert not r.all_pass


def test_min_hd_violation_detected():
    # Two codes that share 3 bits → HD = 2 < 4.
    masks = _masks([[1, 2, 3, 4], [1, 2, 3, 5]])
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)
    assert r.hw_pass  # weights are fine
    assert not r.min_hd_pass
    assert r.min_hd_observed == 2
    assert r.min_hd_n_violations == 1
    assert not r.all_pass


def test_bit_imbalance_detected():
    # Two codes that touch only bits {1,2,3,4} ignore bits 5..9 entirely → spread = 2.
    masks = _masks([[1, 2, 3, 4], [1, 2, 3, 4]])
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)
    assert r.bit_count_min == 0
    assert r.bit_count_max == 2
    assert r.bit_count_spread == 2
    assert not r.bit_balance_pass


def test_spread_of_one_passes_balance():
    # N*hw not divisible by v: N=2, hw=4, v=9 → expected 8/9 ≈ 0.89; perfect packing
    # would give 8 bits with count 1 and 1 bit with count 0, i.e. spread = 1.
    masks = _masks([[1, 2, 3, 4], [5, 6, 7, 8]])
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)
    assert r.bit_count_spread == 1
    assert r.bit_balance_pass


def test_per_bit_counts_length_matches_v():
    masks = _masks(BALANCED_V9_HW4)
    r = validate_codebook(masks, v=9, hw=4, min_hd=4)
    assert len(r.bit_counts) == 9
