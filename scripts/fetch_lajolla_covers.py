"""Fetch covering designs from the La Jolla Covering Repository and bundle them.

LJCR (https://ljcr.dmgordon.org/cover/table.html) is the source of truth for
(v, k, t)-coverings used as starting points by the codebook generator. The
public site exposes each design via
``https://ljcr.dmgordon.org/cover/show_cover.php?v=V&k=K&t=T`` with no bulk
download. This script walks a chosen (v, k, t) set, fetches each design, and
writes a compact gzipped text representation under
``src/merfish_codebooks/data/lajolla/`` so the package can ship offline copies
and survive the upstream site going away.

Storage format (``v{v:03d}_k{k}_t{t}.txt.gz``):
    # method: <method-of-construction string from LJCR>
    <k space-separated 1-indexed ints>
    <k space-separated 1-indexed ints>
    ...

Empty / missing designs on LJCR (which return a stub page with no <pre> body)
are recorded in ``MISSING.txt`` next to the data files, with the (v, k, t) and
upstream URL, so we don't keep re-requesting them.

Usage:
    python scripts/fetch_lajolla_covers.py [--sleep SEC] [--force]
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


LJCR_URL = "https://ljcr.dmgordon.org/cover/show_cover.php"
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "merfish_codebooks" / "data" / "lajolla"
MISSING_FILE = DATA_DIR / "MISSING.txt"


# Bundled scope: t = k - 1 (the only case the codebook generator uses), for
# the HW values our precomputed codebooks ship (HW=4, HW=6). v ranges are
# chosen to cover the README's stated v <= 64 plus puncture-range headroom,
# bounded by what LJCR actually publishes — k=6 designs thin out past v~50.
BUNDLE_SET: list[tuple[int, int, int]] = []
for v in range(4, 71):
    BUNDLE_SET.append((v, 4, 3))
for v in range(6, 51):
    BUNDLE_SET.append((v, 6, 5))


def fetch_and_parse(v: int, k: int, t: int, timeout: float = 30.0) -> tuple[str, list[list[int]]] | None:
    """Return (method, blocks) for an LJCR design, or None if upstream has none."""
    response = requests.get(LJCR_URL, params={"v": v, "k": k, "t": t}, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    pre = soup.find("pre")
    if pre is None:
        return None
    text = pre.get_text("\n", strip=True)
    if not text.strip():
        return None

    rows: list[list[int]] = []
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            rows.append([int(p) for p in parts])
        except ValueError:
            continue
    if not rows:
        return None
    if any(len(r) != k for r in rows):
        raise ValueError(f"({v},{k},{t}): rows have inconsistent or wrong width")

    h2 = soup.find("h2")
    method = h2.get_text(strip=True) if h2 else ""
    return method, rows


def write_cover(path: Path, method: str, blocks: list[list[int]]) -> None:
    lines = [f"# method: {method}"]
    lines.extend(" ".join(str(x) for x in row) for row in blocks)
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb", compresslevel=9) as f:
        f.write(payload)


def read_missing() -> set[tuple[int, int, int]]:
    if not MISSING_FILE.exists():
        return set()
    missing: set[tuple[int, int, int]] = set()
    for line in MISSING_FILE.read_text().splitlines():
        m = re.match(r"\((\d+),\s*(\d+),\s*(\d+)\)", line.strip())
        if m:
            missing.add((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return missing


def append_missing(v: int, k: int, t: int) -> None:
    MISSING_FILE.parent.mkdir(parents=True, exist_ok=True)
    url = f"{LJCR_URL}?v={v}&k={k}&t={t}"
    with MISSING_FILE.open("a") as f:
        f.write(f"({v}, {k}, {t})  {url}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds between requests (default 0.5).")
    ap.add_argument("--force", action="store_true", help="Re-fetch even if a local file already exists.")
    args = ap.parse_args()

    missing = read_missing()
    n_fetched = 0
    n_skipped = 0
    n_missing = 0

    for v, k, t in BUNDLE_SET:
        path = DATA_DIR / f"v{v:03d}_k{k}_t{t}.txt.gz"
        if path.exists() and not args.force:
            n_skipped += 1
            continue
        if (v, k, t) in missing and not args.force:
            n_skipped += 1
            continue

        print(f"fetch v={v} k={k} t={t} ... ", end="", flush=True)
        try:
            result = fetch_and_parse(v, k, t)
        except Exception as exc:
            print(f"ERROR: {exc}")
            return 1

        if result is None:
            print("(no design upstream)")
            if (v, k, t) not in missing:
                append_missing(v, k, t)
                missing.add((v, k, t))
            n_missing += 1
        else:
            method, blocks = result
            write_cover(path, method, blocks)
            size = path.stat().st_size
            print(f"{len(blocks)} blocks, {size} bytes gz, method={method!r}")
            n_fetched += 1

        time.sleep(args.sleep)

    print(f"\nDone. fetched={n_fetched} skipped={n_skipped} missing={n_missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
