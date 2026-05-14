# R reference implementation

Original R source for the iterative set-exchange codebook generator from
Boström, Zapała & Adameyko, *Science Advances* 11 (18), eadr4026 (2025)
(DOI: [10.1126/sciadv.adr4026](https://doi.org/10.1126/sciadv.adr4026); PMID
40315316; PMC12047430).

This directory is preserved as the reference implementation. The Python package
at the top level of this repository is a from-scratch port whose algorithm
semantics match these scripts; representation is bitmask-based and inner loops
are vectorised via NumPy and JIT-compiled via Numba.

## Files

| File | Purpose |
| --- | --- |
| `0_CodebookGeneratingPipeline.R` | Top-level pipeline entry point (`ErrorRobustCodebookGeneratorPunct`). |
| `1_CodebookEvaluator_HammingDistanceChecker.R` | Validates an output codebook (HW, pairwise minHD). |
| `IterativeSetExchangeLoop.R` | Core iterative set-exchange loop (the hot path). |
| `PruningToConformToMinHD.R` | Greedy minHD-violation pruning. |
| `CodebookHDSorter.R` | Post-hoc reorder by mutual Hamming distance. |
| `ImportStartingCodebook_LaJolla.R` | Fetches a La Jolla covering-design starting codebook. |
| `JohnsonBoundCalculator.R` | Computes the Johnson bound (theoretical max). |
| `ConvertBinarytoSet.R` / `ConvertSettoBinary.R` | Representation conversions. |
| `EvaluateCodebookHD.R` | Standalone HD evaluator. |
| `SimulatingCode.R` | Helper for simulating codebooks. |

## Running

The R scripts have no formal package structure. Source the files into an R
session and call `ErrorRobustCodebookGeneratorPunct(...)`. The
`CodeFolder` and `Outputfolder` parameters in
`0_CodebookGeneratingPipeline.R` are Windows paths in the original and must be
adjusted for your environment.

For new work, prefer the Python package at the top level of this repository.
