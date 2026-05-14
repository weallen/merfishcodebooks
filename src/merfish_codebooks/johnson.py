"""Johnson bound A(v, d, w) for constant-weight codes.

Port of `JohnsonBoundCalculator.R`. The +1e-6 nudge from the R reference is preserved
to avoid floor artefacts (e.g., 0.333... * 3 floored as 0 instead of 1).
"""

from __future__ import annotations

import math
from functools import lru_cache


@lru_cache(maxsize=None)
def johnson_bound(v: int, k: int, min_hd: int) -> int:
    """Recursive Johnson bound for binary constant-weight codes.

    Returns ⌊v/k · ⌊(v-1)/(k-1) · ⌊… ⌊(v-w+e)/(...)⌋ …⌋⌋⌋.

    Parameters
    ----------
    v       : barcode length (number of bits).
    k       : Hamming weight (constant for all codes).
    min_hd  : minimum Hamming distance.
    """
    if k <= 0 or k > v:
        return 0
    e = math.ceil(min_hd / 2)
    j_start = v - k + e
    if j_start > v:
        return 1
    bound = 1.0
    for j in range(j_start, v + 1):
        bound = math.floor(bound * (j / (j - v + k)) + 1e-6)
    return int(bound)
