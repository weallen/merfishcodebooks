# merfish_codebooks

Generate large constant-weight binary codebooks at a target minimum Hamming
distance — the kind of code library used by MERFISH and related error-robust
spatial transcriptomics methods to label hundreds to thousands of gene targets
with built-in error detection and correction.

This repository ships:

- A **Python package** (`merfish_codebooks`) — fast, tested, the recommended
  implementation for new work.
- The original **R reference scripts** under [`R/`](R/) — preserved verbatim
  for cross-checking.
- **Precomputed codebooks** at HW=4 and HW=6 for a useful range of barcode
  lengths (see [`codebooks_hw4_minhd4/`](codebooks_hw4_minhd4/) and
  [`codebooks_hw6_minhd4/`](codebooks_hw6_minhd4/)).

## Credit

This is a Python port of the R reference code released with the paper:

> **Boström J., Zapała M., Adameyko I.** *Boosting multiplexing capabilities
> for error-robust spatial transcriptomic methods using a set exchange
> approach.* **Science Advances** 11 (18), eadr4026 (2 May 2025).
> DOI: [10.1126/sciadv.adr4026](https://doi.org/10.1126/sciadv.adr4026) ·
> PMID: [40315316](https://pubmed.ncbi.nlm.nih.gov/40315316/) ·
> PMC: [PMC12047430](https://pmc.ncbi.nlm.nih.gov/articles/PMC12047430/).

If you use this software in published work, please cite the paper above.
A machine-readable citation is provided in [`CITATION.cff`](CITATION.cff).

## What it computes

Given:

- `v` — barcode length (number of decoding probes), up to 64,
- `k` (`hw`) — Hamming weight (number of "on" bits per code),
- `d` (`min_hd`) — required minimum pairwise Hamming distance (4 for SECDED),

the package returns as large a set of `v`-bit codewords as possible such that
every codeword has weight `k` and every pair has Hamming distance ≥ `d`. The
algorithm follows the *iterative set-exchange* approach of Boström et al.
(2025):

1. **Seed** with a (`v`, `k`, `k-1`) covering design from the
   [La Jolla covering repository](https://ljcr.dmgordon.org/cover/table.html)
   — or use a fresh start, a custom CSV, or a punctured higher-`v` covering.
2. **Prune** any pairs that violate `min_hd` greedily.
3. **Scavenge** missing codewords by repeated set exchanges between the kept
   blocks and the universe of weight-`k` words, until no further additions are
   possible (or the [Johnson bound](https://en.wikipedia.org/wiki/Johnson_bound)
   is reached).
4. **Sort** (optional) the final codebook so high-mutual-HD codes come first,
   useful when truncating to a smaller list.

Algorithm details are in the paper. Implementation notes are in
[`docs/algorithm.md`](docs/algorithm.md).

## Install

```bash
pip install -e .
```

Requires Python ≥ 3.10. Dependencies (NumPy, SciPy, Numba, requests,
BeautifulSoup) install automatically. For tests: `pip install -e ".[test]"`.

## Quick start — Python API

```python
from merfish_codebooks import generate_codebook, Start

result = generate_codebook(bits=22, hw=4, min_hd=4, start=Start.lajolla())
print(f"{result.size} codes ({result.pct_of_bound:.1f}% of Johnson bound)")
result.write("./out", prefix="22Bit_HW4_HD4")
```

This writes three files matching the R reference's output format:

- `22Bit_HW4_HD4Binary.csv` — one space-separated 0/1 row per codeword,
- `22Bit_HW4_HD4Set.csv` — set-form (1-indexed bit positions),
- `meta_22Bit_HW4_HD4.txt` — parameters, sizes, timing, starting strategy.

## Quick start — CLI

```bash
# Generate
merfish-codebook generate --bits 22 --hw 4 --min-hd 4 --start lajolla --out ./out

# Validate an existing codebook against minHD
merfish-codebook validate ./out/22Bit_HW4_HD4_finalsize123Binary.csv --min-hd 4

# Reorder so high-HD codes come first
merfish-codebook sort ./out/22Bit_HW4_HD4_finalsize123Binary.csv --out ./out/sorted.csv
```

Run `merfish-codebook --help` for all options.

## Starting strategies

| `Start` factory | When to use |
| --- | --- |
| `Start.lajolla()` | Default. Fetches the (`v`, `k`, `k-1`) La Jolla covering for the requested parameters. |
| `Start.puncture(source_v)` | Start from a larger covering at `source_v > bits` and drop blocks that use out-of-range bits. |
| `Start.range_puncture(upper)` | Try puncturing from each `v` up to `upper`, pick the one yielding the largest pruned starting set. |
| `Start.csv(path)` | Resume / seed from an existing codebook on disk. |
| `Start.fresh()` | Start from a single trivial codeword and let scavenging do the work (slow for large `v`). |

## Constraints

- `v` ≤ 64 (codewords are packed into `uint64`). Standard MERFISH parameters
  fit comfortably.
- `min_hd = 4` (the paper's main case) is currently supported in the pipeline;
  the pairwise-HD machinery is general.
- La Jolla starts: the package ships local copies of the
  ([v∈5..70](src/merfish_codebooks/data/lajolla), k=4, t=3) and
  (v∈7..49, k=6, t=5) covering designs from
  [the La Jolla repository](https://ljcr.dmgordon.org/cover/table.html), so
  HW=4 and HW=6 generation works fully offline. Out-of-range (`v`, `k`, `t`)
  triples fall back to a network fetch (cached under
  `~/.cache/merfish_codebooks/lajolla/`). Set `MERFISH_CODEBOOKS_OFFLINE=1`
  to disallow network fetches. Refresh the bundled set with
  `python scripts/fetch_lajolla_covers.py`.

## Precomputed codebooks

Ready-to-use codebooks are checked in under
[`codebooks_hw4_minhd4/`](codebooks_hw4_minhd4/) and
[`codebooks_hw6_minhd4/`](codebooks_hw6_minhd4/), each containing one
directory per `v` with the `Binary.csv`, `Set.csv`, and `meta_*.txt` triple.
The HW=4 summary table is in
[`codebooks_hw4_minhd4/summary.md`](codebooks_hw4_minhd4/summary.md).

To regenerate from scratch:

```bash
python scripts/precompute_hw4_minhd4.py
python scripts/precompute_hw6_minhd4.py
```

A standalone validation harness (used to compare Python output against the R
reference) is in [`validation_report.md`](validation_report.md), driven by
`scripts/validate_codebooks.py`.

## Package layout

```
src/merfish_codebooks/
├── bitmask.py     uint64 popcount, k-set ↔ bitmask conversions
├── johnson.py     Johnson bound (theoretical max)
├── conversion.py  binary ↔ set ↔ bitmask
├── hd.py          vectorised pairwise Hamming distance
├── lajolla.py     La Jolla cover loader (bundled data → user cache → network)
├── data/lajolla/  Bundled (v,k,t)-covering designs from ljcr.dmgordon.org
├── pruning.py     greedy minHD-violation pruning
├── exchange.py    iterative set-exchange loop (hot path)
├── sorter.py      post-hoc reorder by mutual HD
├── pipeline.py    public API (generate_codebook, Start, CodebookResult)
├── validate.py    standalone validation helpers
├── io.py          CSV read/write with R parity
└── cli.py         merfish-codebook command
```

Tests live under [`tests/`](tests/) and include parity checks against the R
reference output.

## Documentation

- [`docs/algorithm.md`](docs/algorithm.md) — algorithm walkthrough and
  correspondence to the paper / R reference.
- [`docs/output-format.md`](docs/output-format.md) — file format spec for the
  binary, set, and metadata outputs.
- [`R/README.md`](R/README.md) — guide to the original R scripts.

## License

MIT — see [`LICENSE`](LICENSE). The publication itself is published by AAAS
under Science Advances' terms; cite it rather than redistributing the
manuscript.
