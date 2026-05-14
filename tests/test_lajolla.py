"""La Jolla parser tests using a small inlined HTML fixture (no network)."""

import os

import numpy as np
import pytest

from merfish_codebooks.lajolla import fetch_lajolla_cover, parse_lajolla_html


_FIXTURE_HTML = """
<html><body>
<h1>Covering Design</h1>
<h2>Method of Construction: lex covering</h2>
<pre>
1 2 3
1 4 5
1 6 7
2 4 6
2 5 7
3 4 7
3 5 6
</pre>
</body></html>
"""


def test_parse_fixture():
    cover = parse_lajolla_html(_FIXTURE_HTML, v=7, k=3, t=2)
    assert cover.v == 7
    assert cover.k == 3
    assert cover.t == 2
    assert cover.n_blocks == 7
    assert cover.blocks.shape == (7, 3)
    assert cover.blocks.min() >= 1 and cover.blocks.max() <= 7
    assert "lex covering" in cover.method


def test_parse_known_block_values():
    cover = parse_lajolla_html(_FIXTURE_HTML, v=7, k=3, t=2)
    np.testing.assert_array_equal(cover.blocks[0], [1, 2, 3])
    np.testing.assert_array_equal(cover.blocks[-1], [3, 5, 6])


@pytest.mark.parametrize("v,k,t,expected_blocks", [(40, 4, 3, 2470), (15, 6, 5, 578)])
def test_bundled_cover_offline(monkeypatch, tmp_path, v, k, t, expected_blocks):
    """Bundled covers must load with no network and without touching the user cache."""
    monkeypatch.setenv("MERFISH_CODEBOOKS_OFFLINE", "1")
    monkeypatch.setenv("MERFISH_CODEBOOKS_CACHE", str(tmp_path))
    cover = fetch_lajolla_cover(v, k, t)
    assert cover.v == v and cover.k == k and cover.t == t
    assert cover.n_blocks == expected_blocks
    assert cover.blocks.shape == (expected_blocks, k)
    assert cover.blocks.min() >= 1 and cover.blocks.max() <= v
    assert cover.method  # non-empty
    # Bundled hit should not have written to the user cache.
    assert not any(tmp_path.rglob("*.npz"))
