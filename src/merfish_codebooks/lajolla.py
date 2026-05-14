"""La Jolla Covering Repository fetcher.

Port of `ImportStartingCodebook_LaJolla.R`. Returns a (v, k, t)-covering design
sourced from the La Jolla Covering Repository — index at
https://ljcr.dmgordon.org/cover/table.html, per-design pages at
https://ljcr.dmgordon.org/cover/show_cover.php?v=V&k=K&t=T.

Lookup order:
    1. Bundled package data under ``merfish_codebooks/data/lajolla/`` — ships
       (k=4, t=3) covers for v∈[5, 70] and (k=6, t=5) covers for v∈[7, 49],
       which are the only (k, t) pairs the codebook generator uses (t=k-1).
       Refresh with ``scripts/fetch_lajolla_covers.py``.
    2. User disk cache at ``~/.cache/merfish_codebooks/lajolla/`` (populated
       by previous network fetches).
    3. Network fetch from LJCR.

Set ``MERFISH_CODEBOOKS_OFFLINE=1`` to skip the network fallback entirely.
"""

from __future__ import annotations

import gzip
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import numpy as np
import requests
from bs4 import BeautifulSoup


_LJCR_URL = "https://ljcr.dmgordon.org/cover/show_cover.php"
_DEFAULT_TIMEOUT = 30
_BUNDLED_PKG = "merfish_codebooks.data.lajolla"


def _cache_dir() -> Path:
    base = os.environ.get("MERFISH_CODEBOOKS_CACHE")
    if base:
        return Path(base) / "lajolla"
    return Path.home() / ".cache" / "merfish_codebooks" / "lajolla"


def _is_offline() -> bool:
    return os.environ.get("MERFISH_CODEBOOKS_OFFLINE", "").strip() not in ("", "0", "false", "False")


@dataclass
class LaJollaCover:
    """A covering design pulled from the La Jolla repository."""

    v: int
    k: int
    t: int
    blocks: np.ndarray         # (N, k) integer matrix of 1-indexed positions
    method: str                # one-line method description from the LJCR page

    @property
    def n_blocks(self) -> int:
        return int(self.blocks.shape[0])


def _parse_html(html: str) -> tuple[np.ndarray, str]:
    """Extract the (N, k) integer block table and method string from a LJCR page."""
    soup = BeautifulSoup(html, "html.parser")

    # Method text lives in the first <h2>.
    h2 = soup.find("h2")
    method = h2.get_text(strip=True) if h2 else ""

    # The block table lives in <pre> inside <body>.
    pre = soup.find("pre")
    if pre is None:
        raise ValueError("La Jolla response did not contain a <pre> block (likely no design exists for this (v,k,t)).")

    text = pre.get_text("\n", strip=True)
    if not text.strip():
        raise ValueError("La Jolla <pre> block was empty (likely no design for this (v,k,t)).")

    rows: list[list[int]] = []
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            rows.append([int(p) for p in parts])
        except ValueError:
            # Skip header / footer noise.
            continue
    if not rows:
        raise ValueError("La Jolla <pre> block contained no integer rows.")

    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ValueError(f"La Jolla block table has variable row width; first row has {width} entries.")
    return np.asarray(rows, dtype=np.int64), method


def _read_cache(path: Path) -> LaJollaCover | None:
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as f:
        meta = f["meta"]
        return LaJollaCover(
            v=int(meta[0]),
            k=int(meta[1]),
            t=int(meta[2]),
            blocks=f["blocks"].astype(np.int64),
            method=str(f["method"]),
        )


def _write_cache(path: Path, cover: LaJollaCover) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        meta=np.array([cover.v, cover.k, cover.t], dtype=np.int64),
        blocks=cover.blocks,
        method=np.array(cover.method),
    )


def _load_bundled_cover(v: int, k: int, t: int) -> LaJollaCover | None:
    """Return the bundled cover for (v, k, t), or None if we don't ship one."""
    name = f"v{v:03d}_k{k}_t{t}.txt.gz"
    try:
        ref = resources.files(_BUNDLED_PKG).joinpath(name)
    except (ModuleNotFoundError, FileNotFoundError):
        return None
    if not ref.is_file():
        return None
    with ref.open("rb") as raw, gzip.open(raw, "rt", encoding="utf-8") as f:
        lines = f.read().splitlines()
    method = ""
    rows: list[list[int]] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            tag, _, rest = s[1:].strip().partition(":")
            if tag.strip().lower() == "method":
                method = rest.strip()
            continue
        rows.append([int(p) for p in s.split()])
    if not rows:
        raise ValueError(f"Bundled cover {name} contains no blocks.")
    blocks = np.asarray(rows, dtype=np.int64)
    if blocks.shape[1] != k:
        raise ValueError(f"Bundled cover {name} has width {blocks.shape[1]}, expected k={k}.")
    return LaJollaCover(v=v, k=k, t=t, blocks=blocks, method=method)


def fetch_lajolla_cover(v: int, k: int, t: int, *, timeout: float = _DEFAULT_TIMEOUT) -> LaJollaCover:
    """Return a (v, k, t)-cover. Prefers bundled data, then user cache, then network."""
    bundled = _load_bundled_cover(v, k, t)
    if bundled is not None:
        return bundled

    cache_path = _cache_dir() / f"v{v}_k{k}_t{t}.npz"
    cached = _read_cache(cache_path)
    if cached is not None:
        return cached

    if _is_offline():
        raise RuntimeError(
            f"No bundled or cached cover for (v={v}, k={k}, t={t}) and MERFISH_CODEBOOKS_OFFLINE=1."
        )

    params = {"v": v, "k": k, "t": t}
    response = requests.get(_LJCR_URL, params=params, timeout=timeout)
    response.raise_for_status()
    blocks, method = _parse_html(response.text)
    if blocks.shape[1] != k:
        raise ValueError(f"Expected k={k} columns in LJCR table; got {blocks.shape[1]}.")
    cover = LaJollaCover(v=v, k=k, t=t, blocks=blocks, method=method)
    _write_cache(cache_path, cover)
    return cover


def parse_lajolla_html(html: str, v: int, k: int, t: int) -> LaJollaCover:
    """Parse an arbitrary HTML string (used in tests with cached fixtures)."""
    blocks, method = _parse_html(html)
    return LaJollaCover(v=v, k=k, t=t, blocks=blocks, method=method)
