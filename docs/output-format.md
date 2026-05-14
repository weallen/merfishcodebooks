# Output file format

Every call to `result.write(out_dir, prefix=...)` produces three files,
matching the R reference's output convention so existing downstream tooling
keeps working.

Given `prefix = "22Bit_HW4_HD4_finalsize123"`:

```
out_dir/
├── 22Bit_HW4_HD4_finalsize123Binary.csv
├── 22Bit_HW4_HD4_finalsize123Set.csv
└── meta_22Bit_HW4_HD4_finalsize123.txt
```

If `prefix` is omitted, it defaults to
`{bits}Bit_HW{hw}_HD{min_hd}_finalsize{size}`.

## `*Binary.csv` — dense binary form

Each row is one codeword. Values are 0 or 1, separated by a single space.
No header.

Example (3 codes, `v = 6`):

```
1 1 1 1 0 0
1 1 0 0 1 1
0 0 1 1 1 1
```

Read with `numpy.loadtxt(path, dtype=int)` or via
`merfish_codebooks.io.read_codebook_csv(path)` (which returns uint64 masks).

## `*Set.csv` — set form

Each row is the **1-indexed** list of on-positions of one codeword, separated
by single spaces. No header.

Example (same codebook as above):

```
1 2 3 4
1 2 5 6
3 4 5 6
```

This is the format the La Jolla covering repository uses, and the format the R
scripts produce.

## `meta_*.txt` — metadata

Newline-separated `Key: Value` pairs. Keys are:

| Key | Meaning |
| --- | --- |
| `Barcode Length` | `v` |
| `Hamming Weight` | `k` |
| `Minimum Hamming Distance` | `d` |
| `Theoretical Max (Johnson Bound)` | Upper bound on `A(v,d,k)` |
| `StrategyUsed` | One of the start-strategy labels |
| `Final Codebook Size` | `|C|` |
| `Percentage Yield in %` | `100 * size / bound` |
| `Starting Code Method` | Free-text describing where the seed came from |
| `Pruning: Codes Removed` | Number of seed codewords dropped by pruning |
| `Pruning: Codebook Size After Pruning` | Codebook size after pruning, before scavenging |
| `Iterations Used` | Iterations the exchange loop ran |
| `Timing: total_s`, `Timing: ...` | Wall-clock seconds for each pipeline phase |

A consumer that needs only the codebook can read `*Binary.csv` and ignore the
other two files.

## Conversions

```python
from merfish_codebooks.io import read_codebook_csv, write_binary_csv, write_set_csv

masks = read_codebook_csv("path/to/Binary.csv")     # auto-detects binary vs set form
write_binary_csv("out_Binary.csv", masks, bits=22)
write_set_csv("out_Set.csv", masks, hw=4)
```

`read_codebook_csv` accepts either binary or set form transparently.
