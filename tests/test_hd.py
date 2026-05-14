"""Hamming distance evaluation tests."""

import numpy as np

from merfish_codebooks.bitmask import encode_set
from merfish_codebooks.hd import evaluate_hd_matrix, evaluate_hd_row, validate_min_hd


def test_hd_matrix_self_zero():
    codes = np.array([encode_set([1, 2, 3, 4]), encode_set([1, 2, 5, 6])], dtype=np.uint64)
    HD = evaluate_hd_matrix(codes)
    assert (HD.diagonal() == 0).all()


def test_hd_matrix_symmetric():
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([3, 4, 5, 6]), encode_set([1, 5, 7, 8])],
        dtype=np.uint64,
    )
    HD = evaluate_hd_matrix(codes)
    np.testing.assert_array_equal(HD, HD.T)


def test_hd_known_values():
    # Two codes sharing 2 bits each have HD = 2*(k - shared) = 2*(4-2) = 4.
    a = encode_set([1, 2, 3, 4])
    b = encode_set([1, 2, 5, 6])
    codes = np.array([a, b], dtype=np.uint64)
    HD = evaluate_hd_matrix(codes)
    assert int(HD[0, 1]) == 4

    # Two codes sharing 3 bits → HD = 2.
    c = encode_set([1, 2, 3, 5])
    codes = np.array([a, c], dtype=np.uint64)
    HD = evaluate_hd_matrix(codes)
    assert int(HD[0, 1]) == 2


def test_validate_min_hd_pass():
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([5, 6, 7, 8]), encode_set([1, 2, 5, 6])],
        dtype=np.uint64,
    )
    ok, n = validate_min_hd(codes, 4)
    assert ok and n == 0


def test_validate_min_hd_fail():
    codes = np.array(
        [encode_set([1, 2, 3, 4]), encode_set([1, 2, 3, 5])],   # HD = 2
        dtype=np.uint64,
    )
    ok, n = validate_min_hd(codes, 4)
    assert not ok and n == 1


def test_hd_row_matches_matrix():
    codes = np.array([encode_set([1, 2, 3, 4]), encode_set([3, 4, 5, 6]), encode_set([5, 6, 7, 8])], dtype=np.uint64)
    HD = evaluate_hd_matrix(codes)
    for i in range(len(codes)):
        np.testing.assert_array_equal(evaluate_hd_row(codes, i), HD[i])
