"""Greedy minHD-violation pruning.

Port of `PruningToConformToMinHD.R`. Given a candidate codebook with HD < min_hd
violations, iteratively delete codes (vertices in the conflict graph) until the
remaining codebook is conflict-free. The rule cascade matches the R reference:

    1. If any vertex has degree 1, delete *its neighbor* (the deg-1 vertex has only
       one obstruction; killing the neighbor frees it without collateral).
    2. If max-degree == 2 with no deg-1 vertices, delete a deg-2 vertex (breaks the
       only configuration that exists at this point — a simple cycle).
    3. Triangle rule: if a deg-2 vertex's two neighbors are themselves connected,
       delete *both neighbors* (out of the 3, keeping the deg-2 one is provably safe
       since its only conflicts were with the two we're removing).
    4. Otherwise: delete the vertex with the highest degree (standard vertex-cover
       heuristic).

For a fixed-weight code with min_hd=4, the only invalid pair distance is HD=2, so the
conflict graph is built as `HD == 2`; for general min_hd, we use `HD < min_hd & HD > 0`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hd import evaluate_hd_matrix


@dataclass
class PruningResult:
    n_removed: int
    n_after_pruning: int
    masks: np.ndarray   # (M,) uint64, conflict-free


def _conflict_graph(codes: np.ndarray, min_hd: int) -> np.ndarray:
    HD = evaluate_hd_matrix(codes)
    graph = (HD < min_hd) & (HD > 0)
    return graph


def prune_to_min_hd(codes: np.ndarray, min_hd: int, *, rng: np.random.Generator | None = None) -> PruningResult:
    """Prune codes until pairwise Hamming distance is ≥ min_hd everywhere.

    Parameters
    ----------
    codes  : (N,) ndarray of uint64 bitmasks.
    min_hd : minimum required Hamming distance.
    rng    : optional np.random.Generator for the triangle-rule random tie break.
    """
    rng = rng if rng is not None else np.random.default_rng()
    codes = np.asarray(codes, dtype=np.uint64).copy()
    if len(codes) <= 1:
        return PruningResult(n_removed=0, n_after_pruning=len(codes), masks=codes)

    starting_n = len(codes)

    # Set non-conflicting rows aside up front to save memory and work.
    graph = _conflict_graph(codes, min_hd)
    degrees = graph.sum(axis=1)
    no_conflict_mask = degrees == 0
    if no_conflict_mask.any() and degrees.sum() > 0:
        free_codes = codes[no_conflict_mask]
        codes = codes[~no_conflict_mask]
        graph = graph[~no_conflict_mask][:, ~no_conflict_mask]
        degrees = graph.sum(axis=1)
    else:
        free_codes = np.empty(0, dtype=np.uint64)

    iteration = 0
    while True:
        iteration += 1
        degrees = graph.sum(axis=1)
        if degrees.sum() == 0:
            break
        max_deg = int(degrees.max())

        # Rule 1: delete a neighbor of a deg-1 vertex.
        ones = np.where(degrees == 1)[0]
        if ones.size:
            v = int(ones[0])
            neighbor = int(np.where(graph[v])[0][0])
            codes, graph = _delete_row(codes, graph, neighbor)
            continue

        # Rule 2a: simple cycle (max-degree == 2 with no deg-1) -> delete a deg-2 vertex.
        if max_deg == 2:
            twos = np.where(degrees == 2)[0]
            v = int(twos[0])
            codes, graph = _delete_row(codes, graph, v)
            continue

        # Rule 2b: triangle rule.
        if (degrees == 2).any():
            removed = _try_triangle_rule(codes, graph, rng)
            if removed is not None:
                codes, graph = removed
                continue

        # Fallback: remove the highest-degree vertex.
        highest = int(np.where(degrees == max_deg)[0][0])
        codes, graph = _delete_row(codes, graph, highest)

    survivors = np.concatenate([free_codes, codes])
    # Random shuffle to mirror the R version's `Codes[sample(nrow(Codes)),]`.
    rng.shuffle(survivors)
    return PruningResult(
        n_removed=starting_n - len(survivors),
        n_after_pruning=len(survivors),
        masks=survivors,
    )


def _delete_row(codes: np.ndarray, graph: np.ndarray, idx: int) -> tuple[np.ndarray, np.ndarray]:
    keep = np.ones(len(codes), dtype=bool)
    keep[idx] = False
    return codes[keep], graph[keep][:, keep]


def _delete_rows(codes: np.ndarray, graph: np.ndarray, indices: list[int]) -> tuple[np.ndarray, np.ndarray]:
    keep = np.ones(len(codes), dtype=bool)
    keep[np.asarray(indices, dtype=np.int64)] = False
    return codes[keep], graph[keep][:, keep]


def _try_triangle_rule(
    codes: np.ndarray,
    graph: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Look for a deg-2 vertex whose two neighbors are themselves connected.

    If found: delete both neighbors. Returns (codes', graph') or None if no triangle.
    """
    degrees = graph.sum(axis=1)
    twos = np.where(degrees == 2)[0]
    triangles: list[tuple[int, int]] = []  # pairs of (n1, n2) to delete
    for v in twos:
        nbrs = np.where(graph[v])[0]
        if nbrs.size != 2:
            continue
        n1, n2 = int(nbrs[0]), int(nbrs[1])
        if graph[n1, n2]:
            triangles.append((n1, n2))
    if not triangles:
        return None
    pick_idx = int(rng.integers(len(triangles)))
    n1, n2 = triangles[pick_idx]
    return _delete_rows(codes, graph, [n1, n2])
