"""Command-line entrypoint: `merfish-codebook generate / validate / sort`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .hd import validate_min_hd
from .io import read_codebook_csv, write_binary_csv, write_set_csv
from .pipeline import Start, generate_codebook
from .sorter import reorder_by_hd


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="merfish-codebook", description="Generate/validate MERFISH codebooks.")
    sub = p.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a codebook")
    gen.add_argument("--bits", type=int, required=True, help="Barcode length (max 64).")
    gen.add_argument("--hw", type=int, default=4, help="Hamming weight (default 4).")
    gen.add_argument("--min-hd", type=int, default=4, help="Minimum Hamming distance (default 4).")
    gen.add_argument(
        "--start",
        choices=["fresh", "csv", "lajolla", "puncture", "range-puncture"],
        default="lajolla",
        help="Starting strategy (default: lajolla).",
    )
    gen.add_argument("--csv-path", type=Path, help="CSV path for --start csv")
    gen.add_argument("--puncture-source-v", type=int, help="Source v for --start puncture")
    gen.add_argument("--range-upper", type=int, help="Upper v for --start range-puncture")
    gen.add_argument("--max-iterations", type=int, default=300)
    gen.add_argument("--no-dynamic-iterations", action="store_true")
    gen.add_argument("--candidate-cutoff", type=int, default=1)
    gen.add_argument("--rng", type=int, help="RNG seed for reproducibility")
    gen.add_argument("--out", type=Path, required=True, help="Output directory")
    gen.add_argument("--prefix", type=str, default=None, help="Filename prefix override")
    gen.add_argument("--verbose", action="store_true")

    val = sub.add_parser("validate", help="Validate a codebook CSV against minHD")
    val.add_argument("path", type=Path, help="Codebook CSV (binary or set form)")
    val.add_argument("--min-hd", type=int, default=4)
    val.add_argument("--sep", default=" ")

    srt = sub.add_parser("sort", help="Reorder a codebook so high-HD codes come first")
    srt.add_argument("path", type=Path, help="Input codebook CSV")
    srt.add_argument("--out", type=Path, required=True, help="Output codebook CSV")
    srt.add_argument("--rng", type=int, help="RNG seed for reproducibility")
    srt.add_argument("--bits", type=int, help="Override v (otherwise inferred from input)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "generate":
        return _cmd_generate(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "sort":
        return _cmd_sort(args)
    return 1


def _cmd_generate(args: argparse.Namespace) -> int:
    if args.start == "fresh":
        start = Start.fresh()
    elif args.start == "csv":
        if not args.csv_path:
            raise SystemExit("--start csv requires --csv-path")
        start = Start.csv(args.csv_path)
    elif args.start == "lajolla":
        start = Start.lajolla()
    elif args.start == "puncture":
        if not args.puncture_source_v:
            raise SystemExit("--start puncture requires --puncture-source-v")
        start = Start.puncture(args.puncture_source_v)
    else:
        start = Start.range_puncture(args.range_upper)

    result = generate_codebook(
        bits=args.bits,
        hw=args.hw,
        min_hd=args.min_hd,
        start=start,
        max_iterations=args.max_iterations,
        dynamic_max_iterations=not args.no_dynamic_iterations,
        candidate_cutoff=args.candidate_cutoff,
        rng=args.rng,
        verbose=args.verbose,
    )
    paths = result.write(args.out, prefix=args.prefix)
    print(
        f"Wrote {result.size} codes ({result.pct_of_bound:.1f}% of Johnson bound = {result.johnson_bound}) "
        f"to {args.out}",
    )
    for k, p in paths.items():
        print(f"  {k}: {p}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    masks = read_codebook_csv(args.path, sep=args.sep)
    ok, n = validate_min_hd(masks, args.min_hd)
    if ok:
        print(f"OK: {len(masks)} codes, no minHD<{args.min_hd} violations.")
        return 0
    print(f"FAIL: {n} violation(s) below minHD={args.min_hd}.")
    return 2


def _cmd_sort(args: argparse.Namespace) -> int:
    masks = read_codebook_csv(args.path)
    rng = np.random.default_rng(args.rng)
    reordered, n_reordered = reorder_by_hd(masks, rng=rng)
    if args.bits is None:
        from .bitmask import popcount_array
        # Infer v from highest set bit
        bits = int(max(int(m).bit_length() for m in reordered))
    else:
        bits = args.bits
    write_binary_csv(args.out, reordered, bits)
    print(f"Reordered {len(reordered)} codes (active reordering up to row {n_reordered}); wrote {args.out}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
