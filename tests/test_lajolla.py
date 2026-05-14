"""La Jolla parser tests using a small inlined HTML fixture (no network)."""

import numpy as np

from merfish_codebooks.lajolla import parse_lajolla_html


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
