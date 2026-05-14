"""Johnson bound regression — values cross-checked against R reference outputs."""

import pytest

from merfish_codebooks.johnson import johnson_bound


# (v, k, min_hd, expected_johnson_bound). Cross-checked against the R
# JohnsonBoundCalculator function and known constant-weight code tables.
@pytest.mark.parametrize(
    "v,k,d,expected",
    [
        (7, 3, 4, 7),       # Steiner triple system on 7 points (Fano plane)
        (8, 4, 4, 14),      # Steiner system S(3,4,8)
        (16, 4, 4, 140),    # S(3,4,16)
        (22, 4, 4, 385),    # S(3,4,22)
        (24, 5, 4, 2011),   # matches R JohnsonBoundCalculator output
        (56, 4, 4, 6930),   # tested in R impl
        (4, 4, 4, 1),       # one code only
        (3, 3, 4, 1),
    ],
)
def test_johnson_bound(v, k, d, expected):
    assert johnson_bound(v, k, d) == expected


def test_johnson_bound_caches():
    # Same call should return cached value, not re-iterate.
    a = johnson_bound(40, 4, 4)
    b = johnson_bound(40, 4, 4)
    assert a == b
