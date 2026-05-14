"""Post-hoc reorder a finished codebook so high-HD codes come first.

Port of `CodebookHDSorter.R`. Useful when assigning the most-expressed genes to the
codes with the largest mutual Hamming distance (and thus best error tolerance).

Two-phase greedy:

1. Try to seed with floor(v/k) bit-disjoint codes (any two codes share no bit, hence
   pairwise HD = 2k). If the random seeding can't find such a group within 300 tries,
   fall back to picking the pair with the largest HD as the seed.

2. Iteratively append the code with the maximum sum-HD to the currently-chosen prefix.
   Stop early when the max sum-HD per row falls to the codebook average (5 consecutive
   below-average codes), and dump the remaining codes in arbitrary order at the end.
"""

from __future__ import annotations

import numpy as np

from .hd import evaluate_hd_matrix
from .bitmask import popcount_array


def reorder_by_hd(
    codes: np.ndarray,
    *,
    rng: np.random.Generator | None = None,
    max_seed_attempts: int = 300,
    below_avg_tolerance: int = 5,
) -> tuple[np.ndarray, int]:
    """Reorder `codes` to maximise inter-row HD over the early prefix.

    Returns
    -------
    reordered : (N,) ndarray of uint64.
    n_reordered : index up to which active reordering was applied (subsequent rows are
                  in arbitrary order).
    """
    rng = rng if rng is not None else np.random.default_rng()
    codes = np.asarray(codes, dtype=np.uint64)
    n = len(codes)
    if n <= 1:
        return codes.copy(), n

    # k is constant; popcount of any code is k.
    k = int(popcount_array(codes[:1])[0])
    v = 64
    n_wanted = v // k  # may exceed actual capacity for narrow code spaces; that's OK

    # ---- Phase 1: try to find a bit-disjoint seed group of size n_wanted. ----
    chosen: list[int] = []
    seeded = False
    for attempt in range(max_seed_attempts):
        chosen = []
        used_bits = np.uint64(0)
        # Random starting code.
        order = rng.permutation(n)
        for idx in order:
            c = int(codes[idx])
            if (c & int(used_bits)) == 0:
                chosen.append(int(idx))
                used_bits = np.uint64(used_bits | np.uint64(c))
                if len(chosen) == n_wanted:
                    break
        if len(chosen) == n_wanted:
            seeded = True
            break

    HD = evaluate_hd_matrix(codes).astype(np.int32)
    # Penalty value to keep already-chosen rows from being re-picked.
    HD_for_pick = HD.copy()
    np.fill_diagonal(HD_for_pick, -10_000_000)

    if not seeded:
        # Fall back: pick a random start, then the row with max HD to it.
        start = int(rng.integers(n))
        chosen = [start]
        chosen.append(int(_argmax_random(HD_for_pick[:, start], rng)))

    # ---- Phase 2: iteratively append the code with max sum-HD to the chosen prefix. ----
    # Average HD value (excluding the diagonal zeros).
    if n > 1:
        non_diag_sum = float(HD.sum() - HD.trace())
        non_diag_count = float(n * (n - 1))
        avg_hd = non_diag_sum / non_diag_count
    else:
        avg_hd = 0.0

    chosen_arr = list(chosen)
    chosen_set = set(chosen_arr)
    # Penalise chosen rows so they aren't picked again (use the diagonal trick).
    for idx in chosen_arr:
        HD_for_pick[idx, :] = -10_000_000

    below_avg_streak = 0
    n_reordered = n
    while len(chosen_arr) < n:
        sum_hd = HD_for_pick[:, chosen_arr].sum(axis=1)
        max_sum = int(sum_hd.max())
        prefix_len = len(chosen_arr)
        if max_sum / prefix_len <= avg_hd:
            below_avg_streak += 1
            if below_avg_streak >= below_avg_tolerance:
                n_reordered = prefix_len
                break
        else:
            below_avg_streak = 0
        next_idx = int(_argmax_random(sum_hd, rng))
        chosen_arr.append(next_idx)
        chosen_set.add(next_idx)
        HD_for_pick[next_idx, :] = -10_000_000

    # Append any remaining codes in arbitrary (input) order.
    if len(chosen_arr) < n:
        remaining = [i for i in range(n) if i not in chosen_set]
        chosen_arr.extend(remaining)

    return codes[np.asarray(chosen_arr, dtype=np.int64)], n_reordered


def _argmax_random(arr: np.ndarray, rng: np.random.Generator) -> int:
    """Argmax with random tie-breaking — matches R's `sample.int(length(Choices),1)`."""
    max_val = arr.max()
    candidates = np.where(arr == max_val)[0]
    return int(candidates[int(rng.integers(candidates.size))])
