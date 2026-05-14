# HW=4, minHD=4 codebook precomputation summary

- RNG seed: `42`
- Max iterations per run: `500`
- Strategy: range-puncture from target v up through the next Steiner system

| v  | Size | Johnson bound | %      | Iterations | Pruned | Time (s) | Start method |
|----|------|---------------|--------|------------|--------|----------|--------------|
|  9 |   18 |            18 | 100.00% |          0 |      0 |     0.00 | range puncture from v=10: Created by: Jan de Heer |
| 12 |   51 |            54 | 94.44% |          3 |      8 |     0.20 | range puncture from v=12: Method of Construction: simple construction: induced on c(13,5,4) covering |
| 15 |  105 |           105 | 100.00% |          0 |      0 |     0.00 | range puncture from v=16: Method of Construction: lex covering |
| 18 |  198 |           202 | 98.02% |          1 |      6 |     0.01 | range puncture from v=19: Created by: Adolf Muehl and Dietmar Pree |
| 21 |  315 |           315 | 100.00% |          0 |      0 |     0.01 | range puncture from v=22: Method of Construction: steiner quadruple system |
| 24 |  494 |           504 | 98.02% |        501 |     16 |     0.11 | range puncture from v=24: Created by: Adolf Muehl |
| 27 |  702 |           702 | 100.00% |          0 |      0 |     0.03 | range puncture from v=28: Created by: Adolf Muehl |
| 30 | 1005 |          1012 | 99.31% |          1 |     10 |     0.09 | range puncture from v=31: Created by: Jan de Heer |
| 33 | 1320 |          1320 | 100.00% |          0 |      0 |     0.08 | range puncture from v=34: Method of Construction: Steiner System (derived) |
| 36 | 1773 |          1782 | 99.49% |          1 |     12 |     0.27 | range puncture from v=37: Created by: Mathias Liesener |
| 39 | 2223 |          2223 | 100.00% |          0 |      0 |     0.31 | range puncture from v=40: Created by: Colin Barker |
