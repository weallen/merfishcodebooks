"""Validate every precomputed codebook under codebooks_hw*_minhd*/ and emit a single report.

For each `vNN/` subdirectory the script:

1. Parses the expected (v, HW, minHD) from the directory/file naming.
2. Reads the `*Binary.csv` codebook.
3. Runs `validate_codebook`, which checks Hamming weight, pairwise minimum HD, and
   per-round bit balance.

All results are summarised in a single Markdown file (default
`./validation_report.md`) including a top-level pass/fail table and one detail block
per codebook with bit-usage counts.

Usage:
    python scripts/validate_codebooks.py [--root DIR] [--report PATH]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from merfish_codebooks.validate import CodebookValidation, validate_codebook_file


# Directory naming: codebooks_hw{hw}_minhd{hd}
DIR_RE = re.compile(r"codebooks_hw(?P<hw>\d+)_minhd(?P<hd>\d+)$")
# File naming:      {v}Bit_HW{hw}_HD{hd}_finalsize{N}Binary.csv
FILE_RE = re.compile(
    r"(?P<v>\d+)Bit_HW(?P<hw>\d+)_HD(?P<hd>\d+)_finalsize(?P<n>\d+)Binary\.csv$"
)


def _discover(root: Path) -> list[tuple[Path, int, int, int]]:
    """Yield (binary_csv_path, v, hw, min_hd) tuples for every codebook found under root."""
    entries: list[tuple[Path, int, int, int]] = []
    for cb_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        m = DIR_RE.match(cb_dir.name)
        if not m:
            continue
        dir_hw = int(m["hw"])
        dir_hd = int(m["hd"])
        for v_dir in sorted(p for p in cb_dir.iterdir() if p.is_dir()):
            for csv in sorted(v_dir.glob("*Binary.csv")):
                fm = FILE_RE.search(csv.name)
                if not fm:
                    continue
                v = int(fm["v"])
                hw = int(fm["hw"])
                hd = int(fm["hd"])
                # Sanity: directory and filename must agree on (hw, hd).
                if hw != dir_hw or hd != dir_hd:
                    raise SystemExit(
                        f"Naming mismatch: {csv} declares HW{hw}/HD{hd}, "
                        f"but parent directory is {cb_dir.name}."
                    )
                entries.append((csv, v, hw, hd))
    return entries


def _format_report(results: list[CodebookValidation], root: Path) -> str:
    lines: list[str] = []
    lines.append("# MERFISH codebook validation report")
    lines.append("")
    lines.append(f"- Root: `{root}`")
    lines.append(f"- Codebooks checked: {len(results)}")
    n_pass = sum(1 for r in results if r.all_pass)
    lines.append(f"- All checks pass: **{n_pass}/{len(results)}**")
    lines.append("")
    lines.append("Checks performed per codebook:")
    lines.append("- **HW**: every row has Hamming weight equal to the declared HW.")
    lines.append("- **MHD**: every pair of codes has Hamming distance ≥ the declared minHD.")
    lines.append("- **Balance**: per-round bit usage is within 1 of the optimum (⌈N·k/v⌉ vs ⌊N·k/v⌋).")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| Codebook | v | N | HW (min/max/exp) | minHD (obs/exp, violations) | "
        "Bit usage (min/max/expected) | Spread | χ² | All pass |"
    )
    lines.append(
        "|----------|---:|---:|:---:|:---:|:---:|---:|---:|:---:|"
    )
    for r in results:
        rel = Path(r.path).relative_to(root) if Path(r.path).is_absolute() else Path(r.path)
        expected = (r.n_codes * r.hw_expected) / r.v if r.v else 0.0
        all_ok = "PASS" if r.all_pass else "FAIL"
        lines.append(
            f"| `{rel}` | {r.v} | {r.n_codes} | "
            f"{r.hw_min}/{r.hw_max}/{r.hw_expected} "
            f"({'ok' if r.hw_pass else 'FAIL'}) | "
            f"{r.min_hd_observed}/{r.min_hd_expected}, {r.min_hd_n_violations} "
            f"({'ok' if r.min_hd_pass else 'FAIL'}) | "
            f"{r.bit_count_min}/{r.bit_count_max}/{expected:.2f} "
            f"({'ok' if r.bit_balance_pass else 'FAIL'}) | "
            f"{r.bit_count_spread} | {r.bit_balance_chi_square:.3f} | **{all_ok}** |"
        )
    lines.append("")
    lines.append("## Per-codebook detail")
    lines.append("")
    for r in results:
        rel = Path(r.path).relative_to(root) if Path(r.path).is_absolute() else Path(r.path)
        lines.append(f"### `{rel}`")
        lines.append("")
        lines.append(
            f"- v={r.v}, N={r.n_codes}, HW (expected)={r.hw_expected}, "
            f"minHD (expected)={r.min_hd_expected}"
        )
        lines.append(
            f"- HW: min={r.hw_min}, max={r.hw_max} → "
            f"{'PASS' if r.hw_pass else 'FAIL'}"
        )
        lines.append(
            f"- minHD: observed={r.min_hd_observed}, violations={r.min_hd_n_violations} → "
            f"{'PASS' if r.min_hd_pass else 'FAIL'}"
        )
        expected = (r.n_codes * r.hw_expected) / r.v if r.v else 0.0
        lines.append(
            f"- Bit balance: mean={r.bit_count_mean:.3f} (expected {expected:.3f}), "
            f"min={r.bit_count_min}, max={r.bit_count_max}, "
            f"spread={r.bit_count_spread}, std={r.bit_count_std:.3f}, "
            f"χ²={r.bit_balance_chi_square:.3f} → "
            f"{'PASS' if r.bit_balance_pass else 'FAIL'}"
        )
        lines.append(
            "- Per-bit counts: " + ", ".join(str(c) for c in r.bit_counts)
        )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Directory containing codebooks_hw*_minhd*/ trees (default: package root).",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Output report path (default: <root>/validation_report.md).",
    )
    args = p.parse_args()

    root: Path = args.root.resolve()
    report_path: Path = (args.report or (root / "validation_report.md")).resolve()

    entries = _discover(root)
    if not entries:
        raise SystemExit(f"No codebooks found under {root}.")

    results: list[CodebookValidation] = []
    for csv, v, hw, hd in entries:
        res = validate_codebook_file(csv, v=v, hw=hw, min_hd=hd)
        results.append(res)
        status = "PASS" if res.all_pass else "FAIL"
        print(
            f"[{status}] {csv.relative_to(root)}  "
            f"N={res.n_codes}  HW={res.hw_min}..{res.hw_max}/{res.hw_expected}  "
            f"minHD obs={res.min_hd_observed} viol={res.min_hd_n_violations}  "
            f"bit-spread={res.bit_count_spread}  χ²={res.bit_balance_chi_square:.3f}"
        )

    report_path.write_text(_format_report(results, root), encoding="utf-8")
    n_pass = sum(1 for r in results if r.all_pass)
    print(f"\nWrote report to {report_path}")
    print(f"Overall: {n_pass}/{len(results)} codebooks pass all checks.")
    return 0 if n_pass == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
