"""End-to-end pipeline tests."""

import os

import numpy as np
import pytest

from merfish_codebooks import generate_codebook
from merfish_codebooks.hd import validate_min_hd
from merfish_codebooks.pipeline import Start


def test_freshstart_returns_valid_codebook():
    result = generate_codebook(bits=10, hw=4, min_hd=4, start=Start.fresh(), rng=42)
    ok, n = validate_min_hd(result.masks, 4)
    assert ok, f"{n} violations in freshstart output"
    assert result.size > 1


@pytest.mark.skipif(
    os.environ.get("MERFISH_CODEBOOKS_OFFLINE") == "1",
    reason="LaJolla-dependent test; skipped in offline mode.",
)
def test_lajolla_start_22_4_4_hits_bound():
    """(22,4,4) starting from the LaJolla S(3,4,22) cover should hit the Johnson bound (385)."""
    result = generate_codebook(bits=22, hw=4, min_hd=4, start=Start.lajolla(), rng=42)
    assert result.size == result.johnson_bound == 385
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok


@pytest.mark.skipif(
    os.environ.get("MERFISH_CODEBOOKS_OFFLINE") == "1",
    reason="LaJolla-dependent test; skipped in offline mode.",
)
def test_lajolla_start_16_4_4_hits_bound():
    result = generate_codebook(bits=16, hw=4, min_hd=4, start=Start.lajolla(), rng=42)
    assert result.size == result.johnson_bound == 140
    ok, _ = validate_min_hd(result.masks, 4)
    assert ok


def test_csv_roundtrip(tmp_path):
    """Generate, write, read back, and verify minHD."""
    result = generate_codebook(bits=10, hw=4, min_hd=4, start=Start.fresh(), rng=7)
    paths = result.write(tmp_path, prefix="test")
    assert paths["binary"].exists()
    assert paths["set"].exists()
    assert paths["meta"].exists()

    # Read back the binary CSV and verify it represents the same codebook (as a set).
    from merfish_codebooks.io import read_codebook_csv
    masks_from_binary = read_codebook_csv(paths["binary"])
    assert set(int(m) for m in masks_from_binary) == set(int(m) for m in result.masks)

    masks_from_set = read_codebook_csv(paths["set"])
    assert set(int(m) for m in masks_from_set) == set(int(m) for m in result.masks)


def test_invalid_bits_rejected():
    with pytest.raises(ValueError):
        generate_codebook(bits=65, hw=4, min_hd=4, start=Start.fresh())
    with pytest.raises(ValueError):
        generate_codebook(bits=10, hw=11, min_hd=4, start=Start.fresh())
    with pytest.raises(NotImplementedError):
        generate_codebook(bits=10, hw=4, min_hd=6, start=Start.fresh())
