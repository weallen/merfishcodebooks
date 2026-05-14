"""Precompute HW=6, minHD=4 codebooks for v in {12, 13, ..., 30}.

For HW=6 with minHD=4, t = hw - 1 = 5, so the starting covers are (v, 6, 5)-designs.
The only Steiner systems S(5, 6, v) are at v=12 and v=24. For target v <= 24 we
range-puncture up through v=24 (the next Steiner); for 25 <= v <= 30 we use a
small +6 local window above the target.

Usage:
    python scripts/precompute_hw6_minhd4.py [--out DIR] [--rng SEED] [--max-iter N]

Outputs three files per value of v in <DIR>/v{v:02d}/:
    {v}Bit_HW6_HD4_finalsize{N}Binary.csv
    {v}Bit_HW6_HD4_finalsize{N}Set.csv
    meta_{v}Bit_HW6_HD4_finalsize{N}.txt

Plus a top-level summary.md table.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from merfish_codebooks import generate_codebook, johnson_bound
from merfish_codebooks.pipeline import Start


# Known HW=6 Steiner systems S(5, 6, v).
HW6_STEINERS = (12, 24)


def next_target(v: int, *, local_window: int = 6) -> int:
    """Pick a range-puncture upper limit for target v.

    Returns the smallest known HW=6 Steiner v' >= v if one exists, otherwise
    v + local_window (a small local window above the target).
    """
    for s in HW6_STEINERS:
        if s >= v:
            return s
    return v + local_window


def precompute(
    bits_list: list[int],
    out_dir: Path,
    *,
    rng_seed: int = 42,
    max_iterations: int = 500,
    verbose: bool = False,
) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for v in bits_list:
        sub_dir = out_dir / f"v{v:02d}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        bound = johnson_bound(v, 6, 4)
        upper = next_target(v)

        print(f"\n=== v={v:2d}, Johnson bound={bound} (range puncture v..{upper}) ===")
        t0 = time.perf_counter()
        result = generate_codebook(
            bits=v,
            hw=6,
            min_hd=4,
            start=Start.range_puncture(upper_limit=upper),
            max_iterations=max_iterations,
            rng=rng_seed,
            verbose=verbose,
        )
        elapsed = time.perf_counter() - t0

        prefix = f"{v}Bit_HW6_HD4_finalsize{result.size}"
        result.write(sub_dir, prefix=prefix)

        rows.append({
            "v": v,
            "size": result.size,
            "bound": bound,
            "pct": result.pct_of_bound,
            "iters": result.iterations_used,
            "pruned": result.pruning_n_removed,
            "elapsed_s": elapsed,
            "method": result.start_method,
        })
        print(
            f"  -> {result.size}/{bound} = {result.pct_of_bound:.2f}%  "
            f"iters={result.iterations_used}  time={elapsed:.2f}s"
        )

    _write_summary(out_dir / "summary.md", rows, rng_seed=rng_seed, max_iterations=max_iterations)
    return rows


def _write_summary(path: Path, rows: list[dict], *, rng_seed: int, max_iterations: int) -> None:
    lines = [
        "# HW=6, minHD=4 codebook precomputation summary",
        "",
        f"- RNG seed: `{rng_seed}`",
        f"- Max iterations per run: `{max_iterations}`",
        f"- Strategy: range-puncture from target v up through the next HW=6 Steiner (v=24) or +6 local window",
        "",
        "| v  | Size | Johnson bound | %      | Iterations | Pruned | Time (s) | Start method |",
        "|----|------|---------------|--------|------------|--------|----------|--------------|",
    ]
    for r in rows:
        method = (r["method"] or "").replace("|", "/")
        lines.append(
            f"| {r['v']:>2} | {r['size']:>4} | {r['bound']:>13} | "
            f"{r['pct']:>5.2f}% | {r['iters']:>10} | {r['pruned']:>6} | "
            f"{r['elapsed_s']:>8.2f} | {method} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote summary to {path}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--out",
        type=Path,
        default=Path("./codebooks_hw6_minhd4"),
        help="Output directory (default: ./codebooks_hw6_minhd4).",
    )
    p.add_argument(
        "--bits",
        type=int,
        nargs="+",
        default=list(range(12, 31)),
        help="List of barcode lengths to precompute (default: 12..30).",
    )
    p.add_argument("--rng", type=int, default=42, help="RNG seed for reproducibility (default 42).")
    p.add_argument(
        "--max-iter",
        type=int,
        default=500,
        help="Max consecutive non-improving iterations in the exchange loop (default 500).",
    )
    p.add_argument("--verbose", action="store_true", help="Print per-iteration progress.")
    args = p.parse_args()

    rows = precompute(
        bits_list=args.bits,
        out_dir=args.out,
        rng_seed=args.rng,
        max_iterations=args.max_iter,
        verbose=args.verbose,
    )

    print("\n=== Final summary ===")
    for r in rows:
        print(f"v={r['v']:2d}: {r['size']:>4}/{r['bound']:>4} ({r['pct']:>5.2f}%) in {r['elapsed_s']:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
