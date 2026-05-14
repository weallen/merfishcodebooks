# Algorithm walkthrough

This document expands on the high-level summary in the top-level README and
ties each step of `generate_codebook(...)` to its counterpart in the R
reference and in the original publication.

## Reference

> **Boström J., Zapała M., Adameyko I.** *Boosting multiplexing capabilities
> for error-robust spatial transcriptomic methods using a set exchange
> approach.* Science Advances 11 (18), eadr4026 (2 May 2025).
> [DOI:10.1126/sciadv.adr4026](https://doi.org/10.1126/sciadv.adr4026)

## Problem statement

We want a maximum-cardinality set `C ⊆ {0,1}^v` such that

1. every codeword has Hamming weight exactly `k`, and
2. every pair `(c_i, c_j)` satisfies `HD(c_i, c_j) ≥ d`.

For `d = 4` and binary weight-`k` codes, this is the canonical "constant-weight
code" problem studied in coding theory. The largest possible `|C|` for given
`(v, k, d)` is the **constant-weight code bound `A(v, d, k)`**; this code uses
the **Johnson bound** as a tractable upper bound on `A`, computed in
[`johnson.py`](../src/merfish_codebooks/johnson.py).

## Representation

Each codeword is packed into a single `uint64` whose bit `i` is set iff
position `i+1` is "on" in the codeword. This caps `v` at 64, which is more
than sufficient for current MERFISH probesets.

- *Binary form* — the dense 0/1 vector (used in the R reference and for human
  inspection).
- *Set form* — the 1-indexed list of on-positions (used by the La Jolla
  covering repository and by the R reference's `Set.csv`).
- *Mask form* — the `uint64` representation. All hot-path computation uses
  this; conversions live in [`bitmask.py`](../src/merfish_codebooks/bitmask.py)
  and [`conversion.py`](../src/merfish_codebooks/conversion.py).

Pairwise HD between two masks reduces to a single `popcount(a ^ b)`. The
vectorised pairwise distance routine is in
[`hd.py`](../src/merfish_codebooks/hd.py).

## Pipeline

The public entry point `generate_codebook(...)` in
[`pipeline.py`](../src/merfish_codebooks/pipeline.py) mirrors the R function
`ErrorRobustCodebookGeneratorPunct(...)` in
[`R/0_CodebookGeneratingPipeline.R`](../R/0_CodebookGeneratingPipeline.R).

### 1. Seed (choose a starting codebook)

Five `Start` strategies, matching the five "Starting Points" in the R
pipeline:

| Strategy | R flag | Python factory |
| --- | --- | --- |
| Empty/trivial | `FreshStart = TRUE` | `Start.fresh()` |
| User CSV | `CustomStartingFile = "..."` | `Start.csv(path)` |
| La Jolla `(v, k, k-1)` covering | `StartWithCoveringDesign = TRUE` | `Start.lajolla()` |
| Puncture a specific higher-`v` covering | `PunctureSpecificCoveringStart = N` | `Start.puncture(N)` |
| Try a range of higher-`v` coverings, keep the best | `PunctureCoveringRange = TRUE` | `Start.range_puncture(upper)` |

Covering designs are fetched from the
[La Jolla covering repository](https://ljcr.dmgordon.org/) and cached on disk
by [`lajolla.py`](../src/merfish_codebooks/lajolla.py). The choice of
`t = k - 1` (i.e. `(v, k, k-1)`-covering) is what makes the seed dense in
weight-`k` blocks suitable for an `HD ≥ 4` codebook.

### 2. Prune

Coverings frequently contain block pairs with `HD < 4`. The pruner in
[`pruning.py`](../src/merfish_codebooks/pruning.py) builds the violation graph
and greedily removes the highest-degree node until no violations remain. The
R counterpart is
[`R/PruningToConformToMinHD.R`](../R/PruningToConformToMinHD.R).

### 3. Iterative set exchange (scavenging)

This is the algorithmic heart of the paper. Given a valid (post-pruning)
codebook `C`, we look for weight-`k` codewords not in `C` that have `HD ≥ d`
to every existing codeword — these can be added directly. When none remain,
we try *exchanges*: swap out one codeword `c ∈ C` such that two or more new
weight-`k` words become simultaneously addable. The implementation in
[`exchange.py`](../src/merfish_codebooks/exchange.py) is the Numba-compiled
hot path; it corresponds to
[`R/IterativeSetExchangeLoop.R`](../R/IterativeSetExchangeLoop.R).

The loop terminates when:

- the Johnson bound is hit (provably optimal), or
- a configurable iteration cap is reached
  (`max_iterations`, optionally `dynamic_max_iterations`), or
- no further candidate exchange improves the size.

`candidate_cutoff` controls the minimum payoff for an exchange to be
attempted.

### 4. Final validation

`generate_codebook` re-runs `validate_min_hd(masks, min_hd)` before
returning, so a returned `CodebookResult` is guaranteed conforming.

### 5. (Optional) Sorting

`sorter.reorder_by_hd(...)` permutes the codebook so that the prefix of the
first `n` codewords maximises mutual HD — useful when the consumer plans to
truncate to fewer than `|C|` probes. R counterpart:
[`R/CodebookHDSorter.R`](../R/CodebookHDSorter.R).

## Why the Python port runs faster

- `uint64` masks replace dense 0/1 matrices; pairwise HD is one XOR + popcount
  per pair.
- Inner loops are JIT-compiled with Numba and parallelised where the work
  decomposes cleanly.
- The exchange loop avoids rebuilding the candidate universe from scratch on
  each iteration; deltas are propagated through the bitmask representation.

Algorithm semantics, including the random tie-breaking distribution, are
preserved — given the same seed, the Python pipeline produces codebooks of
the same size class as the R reference. Cross-checks are in
[`validation_report.md`](../validation_report.md).
