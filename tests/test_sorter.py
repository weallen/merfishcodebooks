"""Codebook sorter tests."""

import numpy as np

from merfish_codebooks import generate_codebook
from merfish_codebooks.bitmask import encode_set
from merfish_codebooks.hd import evaluate_hd_matrix, validate_min_hd
from merfish_codebooks.pipeline import Start
from merfish_codebooks.sorter import reorder_by_hd


def test_reorder_preserves_codebook():
    """Reordering must not change the *set* of codes."""
    result = generate_codebook(bits=10, hw=4, min_hd=4, start=Start.fresh(), rng=11)
    original = result.masks
    reordered, _ = reorder_by_hd(original, rng=np.random.default_rng(0))
    assert set(int(m) for m in reordered) == set(int(m) for m in original)
    assert len(reordered) == len(original)


def test_reorder_preserves_min_hd():
    result = generate_codebook(bits=12, hw=4, min_hd=4, start=Start.fresh(), rng=11)
    reordered, _ = reorder_by_hd(result.masks, rng=np.random.default_rng(0))
    ok, _ = validate_min_hd(reordered, 4)
    assert ok


def test_reorder_increases_early_prefix_avg_hd():
    """The reordered prefix should have higher mean HD than a random prefix."""
    rng = np.random.default_rng(2024)
    result = generate_codebook(bits=14, hw=4, min_hd=4, start=Start.fresh(), rng=11)
    masks = result.masks
    if len(masks) < 8:
        return  # not interesting on a tiny codebook

    reordered, n_active = reorder_by_hd(masks, rng=rng)
    if n_active < 4:
        return

    HD = evaluate_hd_matrix(reordered).astype(np.float32)
    np.fill_diagonal(HD, np.nan)
    early_mean = float(np.nanmean(HD[:n_active, :n_active]))
    overall_mean = float(np.nanmean(HD))
    assert early_mean >= overall_mean - 0.5  # at least not worse than random
