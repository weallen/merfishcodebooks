"""Greedy pruning tests."""

import numpy as np

from merfish_codebooks.bitmask import encode_set
from merfish_codebooks.hd import validate_min_hd
from merfish_codebooks.pruning import prune_to_min_hd


def test_no_conflicts_returns_unchanged():
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([5, 6, 7, 8]), encode_set([1, 2, 5, 6])],
        dtype=np.uint64,
    )
    result = prune_to_min_hd(codes, min_hd=4, rng=np.random.default_rng(0))
    assert result.n_removed == 0
    assert result.n_after_pruning == len(codes)
    assert set(int(m) for m in result.masks) == set(int(m) for m in codes)


def test_simple_pair_removes_one():
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([1, 2, 3, 5])],   # HD=2
        dtype=np.uint64,
    )
    result = prune_to_min_hd(codes, min_hd=4, rng=np.random.default_rng(0))
    assert result.n_removed == 1
    assert result.n_after_pruning == 1
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok


def test_triangle_keeps_one():
    """Three codes mutually at HD=2: should keep exactly 1 after triangle rule fires."""
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([1, 2, 3, 5]), encode_set([1, 2, 3, 6])],
        dtype=np.uint64,
    )
    result = prune_to_min_hd(codes, min_hd=4, rng=np.random.default_rng(0))
    assert result.n_after_pruning == 1
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok


def test_isolated_plus_chain():
    """Two isolated codes plus a 3-node chain — pruning preserves the 2 isolated and trims the chain."""
    isolated_a = encode_set([1, 2, 3, 4])
    isolated_b = encode_set([5, 6, 7, 8])
    # Chain: x-y-z with x-y HD=2, y-z HD=2, x-z HD=4 (so y is the deg-2 connector)
    x = encode_set([9, 10, 11, 12])
    y = encode_set([9, 10, 11, 13])    # HD(x,y) = 2
    z = encode_set([9, 10, 11, 14])    # HD(y,z) = 2, HD(x,z) = 2
    # Actually all three share {9,10,11}, so it's a triangle. Use a real chain:
    x = encode_set([9, 10, 11, 12])
    y = encode_set([9, 10, 11, 13])    # share 3 with x → HD=2
    z = encode_set([9, 10, 13, 14])    # share 3 with y → HD=2; share 2 with x → HD=4
    codes = np.array([isolated_a, isolated_b, x, y, z], dtype=np.uint64)
    result = prune_to_min_hd(codes, min_hd=4, rng=np.random.default_rng(0))
    assert result.n_after_pruning >= 3   # at minimum: both isolates plus 1 from the chain
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok
