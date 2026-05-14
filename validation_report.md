# MERFISH codebook validation report

- Root: `/Users/wea/src/allenlab/merfish.codebooks/python`
- Codebooks checked: 28
- All checks pass: **18/28**

Checks performed per codebook:
- **HW**: every row has Hamming weight equal to the declared HW.
- **MHD**: every pair of codes has Hamming distance ≥ the declared minHD.
- **Balance**: per-round bit usage is within 1 of the optimum (⌈N·k/v⌉ vs ⌊N·k/v⌋).

## Summary

| Codebook | v | N | HW (min/max/exp) | minHD (obs/exp, violations) | Bit usage (min/max/expected) | Spread | χ² | All pass |
|----------|---:|---:|:---:|:---:|:---:|---:|---:|:---:|
| `codebooks_hw4_minhd4/v09/9Bit_HW4_HD4_finalsize18Binary.csv` | 9 | 18 | 4/4/4 (ok) | 4/4, 0 (ok) | 8/8/8.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v12/12Bit_HW4_HD4_finalsize51Binary.csv` | 12 | 51 | 4/4/4 (ok) | 4/4, 0 (ok) | 17/17/17.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v15/15Bit_HW4_HD4_finalsize105Binary.csv` | 15 | 105 | 4/4/4 (ok) | 4/4, 0 (ok) | 28/28/28.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v18/18Bit_HW4_HD4_finalsize198Binary.csv` | 18 | 198 | 4/4/4 (ok) | 4/4, 0 (ok) | 44/44/44.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v21/21Bit_HW4_HD4_finalsize315Binary.csv` | 21 | 315 | 4/4/4 (ok) | 4/4, 0 (ok) | 60/60/60.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v24/24Bit_HW4_HD4_finalsize494Binary.csv` | 24 | 494 | 4/4/4 (ok) | 4/4, 0 (ok) | 82/83/82.33 (ok) | 1 | 0.065 | **PASS** |
| `codebooks_hw4_minhd4/v27/27Bit_HW4_HD4_finalsize702Binary.csv` | 27 | 702 | 4/4/4 (ok) | 4/4, 0 (ok) | 104/104/104.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v30/30Bit_HW4_HD4_finalsize1005Binary.csv` | 30 | 1005 | 4/4/4 (ok) | 4/4, 0 (ok) | 134/134/134.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v33/33Bit_HW4_HD4_finalsize1320Binary.csv` | 33 | 1320 | 4/4/4 (ok) | 4/4, 0 (ok) | 160/160/160.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v36/36Bit_HW4_HD4_finalsize1773Binary.csv` | 36 | 1773 | 4/4/4 (ok) | 4/4, 0 (ok) | 197/197/197.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw4_minhd4/v39/39Bit_HW4_HD4_finalsize2223Binary.csv` | 39 | 2223 | 4/4/4 (ok) | 4/4, 0 (ok) | 228/228/228.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v12/12Bit_HW6_HD4_finalsize132Binary.csv` | 12 | 132 | 6/6/6 (ok) | 4/4, 0 (ok) | 66/66/66.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v13/13Bit_HW6_HD4_finalsize150Binary.csv` | 13 | 150 | 6/6/6 (ok) | 4/4, 0 (ok) | 65/72/69.23 (FAIL) | 7 | 0.582 | **FAIL** |
| `codebooks_hw6_minhd4/v14/14Bit_HW6_HD4_finalsize219Binary.csv` | 14 | 219 | 6/6/6 (ok) | 4/4, 0 (ok) | 92/95/93.86 (FAIL) | 3 | 0.189 | **FAIL** |
| `codebooks_hw6_minhd4/v15/15Bit_HW6_HD4_finalsize355Binary.csv` | 15 | 355 | 6/6/6 (ok) | 4/4, 0 (ok) | 140/143/142.00 (FAIL) | 3 | 0.085 | **FAIL** |
| `codebooks_hw6_minhd4/v16/16Bit_HW6_HD4_finalsize568Binary.csv` | 16 | 568 | 6/6/6 (ok) | 4/4, 0 (ok) | 213/213/213.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v17/17Bit_HW6_HD4_finalsize853Binary.csv` | 17 | 853 | 6/6/6 (ok) | 4/4, 0 (ok) | 297/305/301.06 (FAIL) | 8 | 0.236 | **FAIL** |
| `codebooks_hw6_minhd4/v18/18Bit_HW6_HD4_finalsize1260Binary.csv` | 18 | 1260 | 6/6/6 (ok) | 4/4, 0 (ok) | 420/420/420.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v19/19Bit_HW6_HD4_finalsize1519Binary.csv` | 19 | 1519 | 6/6/6 (ok) | 4/4, 0 (ok) | 475/484/479.68 (FAIL) | 9 | 0.275 | **FAIL** |
| `codebooks_hw6_minhd4/v20/20Bit_HW6_HD4_finalsize2151Binary.csv` | 20 | 2151 | 6/6/6 (ok) | 4/4, 0 (ok) | 644/646/645.30 (FAIL) | 2 | 0.013 | **FAIL** |
| `codebooks_hw6_minhd4/v21/21Bit_HW6_HD4_finalsize2856Binary.csv` | 21 | 2856 | 6/6/6 (ok) | 4/4, 0 (ok) | 816/816/816.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v22/22Bit_HW6_HD4_finalsize3927Binary.csv` | 22 | 3927 | 6/6/6 (ok) | 4/4, 0 (ok) | 1071/1071/1071.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v23/23Bit_HW6_HD4_finalsize5313Binary.csv` | 23 | 5313 | 6/6/6 (ok) | 4/4, 0 (ok) | 1386/1386/1386.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v24/24Bit_HW6_HD4_finalsize7084Binary.csv` | 24 | 7084 | 6/6/6 (ok) | 4/4, 0 (ok) | 1771/1771/1771.00 (ok) | 0 | 0.000 | **PASS** |
| `codebooks_hw6_minhd4/v25/25Bit_HW6_HD4_finalsize7722Binary.csv` | 25 | 7722 | 6/6/6 (ok) | 4/4, 0 (ok) | 1839/1867/1853.28 (FAIL) | 28 | 0.901 | **FAIL** |
| `codebooks_hw6_minhd4/v26/26Bit_HW6_HD4_finalsize9958Binary.csv` | 26 | 9958 | 6/6/6 (ok) | 4/4, 0 (ok) | 2291/2306/2298.00 (FAIL) | 15 | 0.147 | **FAIL** |
| `codebooks_hw6_minhd4/v27/27Bit_HW6_HD4_finalsize11679Binary.csv` | 27 | 11679 | 6/6/6 (ok) | 4/4, 0 (ok) | 2575/2678/2595.33 (FAIL) | 103 | 3.254 | **FAIL** |
| `codebooks_hw6_minhd4/v28/28Bit_HW6_HD4_finalsize14773Binary.csv` | 28 | 14773 | 6/6/6 (ok) | 4/4, 0 (ok) | 3155/3171/3165.64 (FAIL) | 16 | 0.121 | **FAIL** |

## Per-codebook detail

### `codebooks_hw4_minhd4/v09/9Bit_HW4_HD4_finalsize18Binary.csv`

- v=9, N=18, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=8.000 (expected 8.000), min=8, max=8, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 8, 8, 8, 8, 8, 8, 8, 8, 8

### `codebooks_hw4_minhd4/v12/12Bit_HW4_HD4_finalsize51Binary.csv`

- v=12, N=51, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=17.000 (expected 17.000), min=17, max=17, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17

### `codebooks_hw4_minhd4/v15/15Bit_HW4_HD4_finalsize105Binary.csv`

- v=15, N=105, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=28.000 (expected 28.000), min=28, max=28, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28

### `codebooks_hw4_minhd4/v18/18Bit_HW4_HD4_finalsize198Binary.csv`

- v=18, N=198, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=44.000 (expected 44.000), min=44, max=44, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44

### `codebooks_hw4_minhd4/v21/21Bit_HW4_HD4_finalsize315Binary.csv`

- v=21, N=315, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=60.000 (expected 60.000), min=60, max=60, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60

### `codebooks_hw4_minhd4/v24/24Bit_HW4_HD4_finalsize494Binary.csv`

- v=24, N=494, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=82.333 (expected 82.333), min=82, max=83, spread=1, std=0.471, χ²=0.065 → PASS
- Per-bit counts: 83, 82, 82, 82, 83, 83, 82, 83, 82, 82, 82, 82, 82, 83, 82, 82, 82, 82, 83, 82, 82, 82, 83, 83

### `codebooks_hw4_minhd4/v27/27Bit_HW4_HD4_finalsize702Binary.csv`

- v=27, N=702, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=104.000 (expected 104.000), min=104, max=104, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104

### `codebooks_hw4_minhd4/v30/30Bit_HW4_HD4_finalsize1005Binary.csv`

- v=30, N=1005, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=134.000 (expected 134.000), min=134, max=134, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134, 134

### `codebooks_hw4_minhd4/v33/33Bit_HW4_HD4_finalsize1320Binary.csv`

- v=33, N=1320, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=160.000 (expected 160.000), min=160, max=160, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160

### `codebooks_hw4_minhd4/v36/36Bit_HW4_HD4_finalsize1773Binary.csv`

- v=36, N=1773, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=197.000 (expected 197.000), min=197, max=197, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 197

### `codebooks_hw4_minhd4/v39/39Bit_HW4_HD4_finalsize2223Binary.csv`

- v=39, N=2223, HW (expected)=4, minHD (expected)=4
- HW: min=4, max=4 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=228.000 (expected 228.000), min=228, max=228, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228, 228

### `codebooks_hw6_minhd4/v12/12Bit_HW6_HD4_finalsize132Binary.csv`

- v=12, N=132, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=66.000 (expected 66.000), min=66, max=66, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66

### `codebooks_hw6_minhd4/v13/13Bit_HW6_HD4_finalsize150Binary.csv`

- v=13, N=150, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=69.231 (expected 69.231), min=65, max=72, spread=7, std=1.761, χ²=0.582 → FAIL
- Per-bit counts: 70, 68, 72, 70, 69, 69, 68, 68, 69, 70, 70, 72, 65

### `codebooks_hw6_minhd4/v14/14Bit_HW6_HD4_finalsize219Binary.csv`

- v=14, N=219, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=93.857 (expected 93.857), min=92, max=95, spread=3, std=1.125, χ²=0.189 → FAIL
- Per-bit counts: 93, 95, 92, 94, 95, 94, 93, 95, 93, 93, 95, 92, 95, 95

### `codebooks_hw6_minhd4/v15/15Bit_HW6_HD4_finalsize355Binary.csv`

- v=15, N=355, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=142.000 (expected 142.000), min=140, max=143, spread=3, std=0.894, χ²=0.085 → FAIL
- Per-bit counts: 143, 141, 141, 142, 142, 143, 140, 142, 143, 142, 141, 143, 142, 142, 143

### `codebooks_hw6_minhd4/v16/16Bit_HW6_HD4_finalsize568Binary.csv`

- v=16, N=568, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=213.000 (expected 213.000), min=213, max=213, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213

### `codebooks_hw6_minhd4/v17/17Bit_HW6_HD4_finalsize853Binary.csv`

- v=17, N=853, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=301.059 (expected 301.059), min=297, max=305, spread=8, std=2.043, χ²=0.236 → FAIL
- Per-bit counts: 300, 300, 298, 301, 300, 301, 301, 299, 297, 305, 303, 303, 303, 300, 302, 304, 301

### `codebooks_hw6_minhd4/v18/18Bit_HW6_HD4_finalsize1260Binary.csv`

- v=18, N=1260, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=420.000 (expected 420.000), min=420, max=420, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420

### `codebooks_hw6_minhd4/v19/19Bit_HW6_HD4_finalsize1519Binary.csv`

- v=19, N=1519, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=479.684 (expected 479.684), min=475, max=484, spread=9, std=2.637, χ²=0.275 → FAIL
- Per-bit counts: 481, 480, 480, 481, 484, 481, 481, 479, 484, 477, 483, 482, 480, 475, 476, 479, 478, 475, 478

### `codebooks_hw6_minhd4/v20/20Bit_HW6_HD4_finalsize2151Binary.csv`

- v=20, N=2151, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=645.300 (expected 645.300), min=644, max=646, spread=2, std=0.640, χ²=0.013 → FAIL
- Per-bit counts: 646, 646, 644, 644, 646, 646, 646, 646, 646, 646, 645, 645, 645, 645, 645, 645, 645, 645, 645, 645

### `codebooks_hw6_minhd4/v21/21Bit_HW6_HD4_finalsize2856Binary.csv`

- v=21, N=2856, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=816.000 (expected 816.000), min=816, max=816, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816, 816

### `codebooks_hw6_minhd4/v22/22Bit_HW6_HD4_finalsize3927Binary.csv`

- v=22, N=3927, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=1071.000 (expected 1071.000), min=1071, max=1071, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071, 1071

### `codebooks_hw6_minhd4/v23/23Bit_HW6_HD4_finalsize5313Binary.csv`

- v=23, N=5313, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=1386.000 (expected 1386.000), min=1386, max=1386, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386, 1386

### `codebooks_hw6_minhd4/v24/24Bit_HW6_HD4_finalsize7084Binary.csv`

- v=24, N=7084, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=1771.000 (expected 1771.000), min=1771, max=1771, spread=0, std=0.000, χ²=0.000 → PASS
- Per-bit counts: 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771, 1771

### `codebooks_hw6_minhd4/v25/25Bit_HW6_HD4_finalsize7722Binary.csv`

- v=25, N=7722, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=1853.280 (expected 1853.280), min=1839, max=1867, spread=28, std=8.171, χ²=0.901 → FAIL
- Per-bit counts: 1845, 1839, 1842, 1845, 1844, 1847, 1850, 1851, 1849, 1851, 1847, 1849, 1843, 1862, 1865, 1867, 1866, 1864, 1857, 1858, 1857, 1854, 1862, 1858, 1860

### `codebooks_hw6_minhd4/v26/26Bit_HW6_HD4_finalsize9958Binary.csv`

- v=26, N=9958, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=2298.000 (expected 2298.000), min=2291, max=2306, spread=15, std=3.606, χ²=0.147 → FAIL
- Per-bit counts: 2294, 2298, 2295, 2297, 2306, 2294, 2300, 2291, 2300, 2297, 2293, 2295, 2298, 2301, 2298, 2300, 2299, 2305, 2294, 2299, 2297, 2296, 2305, 2297, 2299, 2300

### `codebooks_hw6_minhd4/v27/27Bit_HW6_HD4_finalsize11679Binary.csv`

- v=27, N=11679, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=2595.333 (expected 2595.333), min=2575, max=2678, spread=103, std=17.684, χ²=3.254 → FAIL
- Per-bit counts: 2602, 2604, 2584, 2598, 2600, 2602, 2597, 2591, 2594, 2596, 2594, 2595, 2595, 2678, 2589, 2587, 2592, 2590, 2593, 2579, 2587, 2575, 2600, 2593, 2592, 2579, 2588

### `codebooks_hw6_minhd4/v28/28Bit_HW6_HD4_finalsize14773Binary.csv`

- v=28, N=14773, HW (expected)=6, minHD (expected)=4
- HW: min=6, max=6 → PASS
- minHD: observed=4, violations=0 → PASS
- Bit balance: mean=3165.643 (expected 3165.643), min=3155, max=3171, spread=16, std=3.696, χ²=0.121 → FAIL
- Per-bit counts: 3163, 3163, 3170, 3170, 3166, 3169, 3162, 3170, 3163, 3164, 3167, 3165, 3171, 3163, 3169, 3164, 3164, 3170, 3169, 3170, 3165, 3169, 3162, 3166, 3160, 3165, 3155, 3164
