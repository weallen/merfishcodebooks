"""Bitmask utilities — encode/decode round-trips, popcount, t-set enumeration."""

import numpy as np
import pytest

from merfish_codebooks.bitmask import (
    all_kset_masks,
    decode_set,
    encode_set,
    encode_set_array,
    decode_set_array,
    binary_to_masks,
    find_compatible_pair,
    masks_to_binary,
    popcount64,
    popcount_array,
    tsets_of_kset_minhd4,
)


def test_popcount_scalar():
    cases = [(0, 0), (1, 1), (3, 2), (0xFF, 8), (0xFFFF, 16), (0xFFFFFFFFFFFFFFFF, 64), (1 << 63, 1)]
    for x, expected in cases:
        assert int(popcount64(np.uint64(x))) == expected


def test_popcount_array():
    arr = np.array([0, 1, 7, 0xFF, (1 << 63), (1 << 63) | 1], dtype=np.uint64)
    expected = [0, 1, 3, 8, 1, 2]
    np.testing.assert_array_equal(popcount_array(arr), expected)


def test_encode_decode_roundtrip():
    s = (1, 5, 7, 13)
    m = encode_set(s)
    assert decode_set(m) == s


def test_encode_decode_array_roundtrip():
    sets = np.array([[1, 2, 3, 4], [3, 7, 11, 15]], dtype=np.int64)
    masks = encode_set_array(sets)
    back = decode_set_array(masks, k=4)
    np.testing.assert_array_equal(np.sort(sets, axis=1), np.sort(back, axis=1))


def test_binary_to_masks_roundtrip():
    binary = np.array([[1, 1, 0, 0, 1], [0, 1, 1, 1, 0]], dtype=np.uint8)
    masks = binary_to_masks(binary)
    back = masks_to_binary(masks, v=5)
    np.testing.assert_array_equal(binary, back)


def test_all_kset_masks_count_and_weights():
    from math import comb
    for v, k in [(5, 2), (8, 3), (10, 4)]:
        masks = all_kset_masks(v, k)
        assert len(masks) == comb(v, k)
        assert (popcount_array(masks) == k).all()


def test_tsets_of_kset_minhd4():
    """For minHD=4, the t-sets of a k-set are the (k-1)-subsets — k of them."""
    k = 4
    code = encode_set([1, 2, 3, 4])
    tsets = tsets_of_kset_minhd4(code, k)
    assert len(tsets) == k
    # Decode and check that each is a 3-subset of {1,2,3,4}.
    expected = {(2, 3, 4), (1, 3, 4), (1, 2, 4), (1, 2, 3)}
    got = {decode_set(np.uint64(m)) for m in tsets}
    assert got == expected


def test_encode_set_rejects_out_of_range():
    with pytest.raises(ValueError):
        encode_set([0, 1, 2])    # bit 0 not allowed (1-indexed)
    with pytest.raises(ValueError):
        encode_set([1, 65])      # exceeds MAX_BITS


def test_find_compatible_pair_finds_min_intersect():
    a = encode_set([1, 2, 3, 4])
    b = encode_set([1, 2, 3, 5])      # share 3 bits
    c = encode_set([6, 7, 8, 9])      # disjoint from a, b
    masks = np.array([a, b, c], dtype=np.uint64)

    # t=3: pair (a, b) share exactly 3 → invalid; (a, c) and (b, c) share 0 → valid.
    i, j = find_compatible_pair(masks, t=3)
    assert (i, j) in {(0, 2), (1, 2), (0, 1)}  # the kernel returns first found
    # Verify the returned pair is valid.
    intersect_count = bin(int(masks[i] & masks[j])).count("1")
    assert intersect_count < 3


def test_find_compatible_pair_returns_neg_when_none():
    # All pairs share 3 bits.
    a = encode_set([1, 2, 3, 4])
    b = encode_set([1, 2, 3, 5])
    c = encode_set([1, 2, 3, 6])
    masks = np.array([a, b, c], dtype=np.uint64)
    i, j = find_compatible_pair(masks, t=3)
    assert i == -1 and j == -1
