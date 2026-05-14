"""Iterative set exchange loop tests on small, known-optimum cases."""

import numpy as np

from merfish_codebooks.bitmask import encode_set
from merfish_codebooks.exchange import iterative_set_exchange
from merfish_codebooks.hd import validate_min_hd
from merfish_codebooks.johnson import johnson_bound


def test_steiner_triple_system_v7():
    """(v=7, k=3, d=4): the Fano plane is a Steiner system reaching the Johnson bound (7)."""
    bound = johnson_bound(7, 3, 4)
    assert bound == 7
    start = np.array([encode_set([1, 2, 3])], dtype=np.uint64)
    result = iterative_set_exchange(
        v=7, k=3, codes=start, min_hd=4,
        max_iterations=200, theoretical_max=bound,
        rng=np.random.default_rng(42),
    )
    assert len(result.masks) == bound
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok


def test_no_minhd_violations_in_output():
    """Across several FreshStart runs, the output is always conflict-free."""
    for v, k in [(8, 4), (10, 4), (12, 4)]:
        start = np.array([encode_set(list(range(1, k + 1)))], dtype=np.uint64)
        result = iterative_set_exchange(
            v=v, k=k, codes=start, min_hd=4,
            max_iterations=200, theoretical_max=johnson_bound(v, k, 4),
            rng=np.random.default_rng(123),
        )
        ok, n_violations = validate_min_hd(result.masks, 4)
        assert ok, f"({v},{k}): {n_violations} violations"


def test_deterministic_with_same_seed():
    start = np.array([encode_set([1, 2, 3, 4])], dtype=np.uint64)
    a = iterative_set_exchange(
        v=12, k=4, codes=start, min_hd=4,
        max_iterations=100, rng=np.random.default_rng(7),
    )
    b = iterative_set_exchange(
        v=12, k=4, codes=start, min_hd=4,
        max_iterations=100, rng=np.random.default_rng(7),
    )
    np.testing.assert_array_equal(np.sort(a.masks), np.sort(b.masks))


def test_starts_already_optimal_returns_immediately():
    """If the input is already at the Johnson bound, no growth iterations are needed."""
    bound = johnson_bound(7, 3, 4)
    # Build a Fano plane from a standard reference.
    fano = [
        [1, 2, 3], [1, 4, 5], [1, 6, 7],
        [2, 4, 6], [2, 5, 7], [3, 4, 7], [3, 5, 6],
    ]
    masks = np.array([encode_set(b) for b in fano], dtype=np.uint64)
    result = iterative_set_exchange(
        v=7, k=3, codes=masks, min_hd=4,
        max_iterations=50, theoretical_max=bound,
        rng=np.random.default_rng(0),
    )
    assert len(result.masks) == bound
