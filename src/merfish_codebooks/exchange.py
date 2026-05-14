"""Iterative set-exchange loop — the core scavenging algorithm.

Port of `IterativeSetExchangeLoop.R`. Algorithm summary (for minHD=4, where t=k-1):

For a current codebook C of k-sets:
  used_t   := {t-sets contained in some c in C}
  unused_t := all C(v,t) t-sets minus used_t
  ghost_ksets := { tau | (1 << b) : tau in unused_t, b in [1..v] not in tau } (multiset)

A k-set g appears in ghost_ksets exactly once per t-set of g that is unused. Hence
  count(g) == k                  ⇒ all of g's t-sets are unused           → EasyPicking
  count(g) == k-1 = t            ⇒ exactly one t-set of g is used         → Candidate

Each iteration:
  A. If any EasyPicking exists, append one to C   (net +1 code)
  B. Otherwise, group Candidates by the codeword they "block" on (i.e., the codeword
     that owns the one used t-set of the candidate). For any codeword with ≥ 2
     candidates, try to find a pair g_i, g_j with |g_i ∩ g_j| < t. If found, remove
     the blocking codeword and add both candidates                          (net +1)
  C. Otherwise, randomly swap one Candidate with the codeword whose t-set it blocks on
     (no size gain, but reshuffles used_t for next iteration).

This implementation differs from the R reference in three speed-critical ways:
  1. Codes are uint64 bitmasks; HD/intersection use bitwise XOR/AND + popcount.
  2. used_t_to_code is maintained incrementally (dict), not rebuilt every iteration.
  3. The pair-compatibility kernel is JIT-compiled with Numba.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from math import comb

import numpy as np

from .bitmask import (
    all_kset_masks,
    find_compatible_pair,
    popcount_array,
    tsets_of_kset_minhd4,
    tsets_of_codes_minhd4,
)


@dataclass
class ExchangeResult:
    masks: np.ndarray                                          # final codebook, uint64
    iterations_used: int
    time_first_100: float | None = None                        # seconds from start to iter 100
    time_last_improvement: float | None = None                 # seconds from start to last grow
    log: list[str] = field(default_factory=list)


def iterative_set_exchange(
    v: int,
    k: int,
    codes: np.ndarray,
    *,
    min_hd: int = 4,
    max_iterations: int = 300,
    dynamic_max_iterations: bool = True,
    candidate_cutoff: int = 1,
    theoretical_max: int | None = None,
    rng: np.random.Generator | None = None,
    verbose: bool = False,
) -> ExchangeResult:
    """Run the iterative set-exchange scavenging loop on `codes`.

    `codes` is an N-vector of uint64 bitmasks satisfying the minHD constraint already
    (call `prune_to_min_hd` first if not).
    """
    if min_hd != 4:
        raise NotImplementedError("Only min_hd=4 is currently supported (paper's main case).")
    t = k - (min_hd // 2 - 1)        # = k - 1 for minHD=4
    if t != k - 1:
        raise NotImplementedError("Generalised t != k-1 is not implemented in this port.")

    rng = rng if rng is not None else np.random.default_rng()
    codes_list: list[int] = [int(m) for m in np.asarray(codes, dtype=np.uint64)]

    # Precompute the universe of t-masks once. For minHD=4, that's C(v, k-1) entries.
    all_t_masks = all_kset_masks(v, t)
    all_t_set: set[int] = set(int(x) for x in all_t_masks)

    # Initial used_t_to_code: every t-set of every starting codeword maps back to that
    # codeword's mask. (Codeword identity, not list index — survives deletions.)
    used_t_to_code: dict[int, int] = {}
    if codes_list:
        for c in codes_list:
            for tau in tsets_of_kset_minhd4(np.uint64(c), k):
                used_t_to_code[int(tau)] = c

    log: list[str] = []
    iter_counter = 0
    max_iter_loop = max_iterations
    start_time = time.perf_counter()
    time_first_100: float | None = None
    time_last_improvement: float | None = None

    bit_powers_u64 = (np.uint64(1) << np.arange(v, dtype=np.uint64))

    while True:
        iter_counter += 1
        if iter_counter == 100:
            time_first_100 = time.perf_counter() - start_time
        if iter_counter > max_iter_loop:
            break

        # If we've already reached the (caller-provided) theoretical max, stop.
        if theoretical_max is not None and len(codes_list) >= theoretical_max:
            break

        # --- Build unused t-set vector from the running used_t_to_code map. ---
        used_t_set = used_t_to_code.keys()
        unused_t = np.fromiter(
            (m for m in all_t_set if m not in used_t_set),
            dtype=np.uint64,
            count=len(all_t_set) - len(used_t_to_code),
        )

        # --- Generate ghost k-sets: for each unused τ and each bit b ∉ τ, τ | (1<<b). ---
        if unused_t.size == 0:
            break
        ghost_with_dups = unused_t[:, None] | bit_powers_u64[None, :]
        # Keep only entries where the OR added a new bit (i.e., b ∉ τ).
        keep = ghost_with_dups != unused_t[:, None]
        ghosts = ghost_with_dups[keep]

        # Multiplicities: count == k → EasyPicking, count == t → Candidate.
        unique_ghosts, counts = np.unique(ghosts, return_counts=True)

        # --- Phase A: EasyPicking. ---
        easy = unique_ghosts[counts == k]
        if easy.size:
            pick = int(easy[int(rng.integers(easy.size))])
            codes_list.append(pick)
            for tau in tsets_of_kset_minhd4(np.uint64(pick), k):
                used_t_to_code[int(tau)] = pick
            time_last_improvement = time.perf_counter() - start_time
            if dynamic_max_iterations:
                max_iter_loop = max(max_iter_loop, iter_counter + max_iterations)
            if verbose:
                msg = f"iter {iter_counter}: +1 EasyPicking, codebook now {len(codes_list)}"
                log.append(msg)
                print(msg)
            continue

        # --- Phase B: Candidate matching. ---
        candidates = unique_ghosts[counts == t]
        if candidates.size < candidate_cutoff:
            log.append(f"iter {iter_counter}: out of candidates")
            break

        # Group candidates by the codeword they block on.
        blocked: dict[int, list[int]] = {}
        cand_to_block: dict[int, int] = {}   # candidate mask → codeword mask it conflicts with
        for g in candidates:
            g_int = int(g)
            ts = tsets_of_kset_minhd4(np.uint64(g_int), k)
            for tau in ts:
                tau_int = int(tau)
                if tau_int in used_t_to_code:
                    block_code = used_t_to_code[tau_int]
                    blocked.setdefault(block_code, []).append(g_int)
                    cand_to_block[g_int] = block_code
                    break
            # If no t-set of g was used, then g is actually an EasyPicking we missed.
            # That can't happen given the multiplicity == t condition, but be defensive.

        # Try pair-compatible swaps for blocking codes with >= 2 candidates.
        found_pair = False
        # Iterate in deterministic order by codeword mask for reproducibility.
        for block_code in sorted(blocked.keys()):
            cand_list = blocked[block_code]
            if len(cand_list) < 2:
                continue
            cand_arr = np.asarray(cand_list, dtype=np.uint64)
            i, j = find_compatible_pair(cand_arr, t)
            if i < 0:
                continue
            g_i, g_j = int(cand_arr[i]), int(cand_arr[j])
            # Remove the blocking codeword from the codebook + used_t_to_code.
            try:
                codes_list.remove(block_code)
            except ValueError:
                continue
            for tau in tsets_of_kset_minhd4(np.uint64(block_code), k):
                used_t_to_code.pop(int(tau), None)
            # Add both candidates.
            for new_c in (g_i, g_j):
                codes_list.append(new_c)
                for tau in tsets_of_kset_minhd4(np.uint64(new_c), k):
                    used_t_to_code[int(tau)] = new_c
            time_last_improvement = time.perf_counter() - start_time
            if dynamic_max_iterations:
                max_iter_loop = max(max_iter_loop, iter_counter + max_iterations)
            found_pair = True
            if verbose:
                msg = f"iter {iter_counter}: +1 via pair-swap, codebook now {len(codes_list)}"
                log.append(msg)
                print(msg)
            break

        if found_pair:
            continue

        # --- Phase C: Random shuffle (no size gain). ---
        # Pick a random candidate and swap it for the codeword it blocks on.
        cand_idx = int(rng.integers(candidates.size))
        g = int(candidates[cand_idx])
        block_code = cand_to_block.get(g)
        if block_code is None:
            # Defensive: candidate didn't get classified earlier (shouldn't happen).
            continue
        try:
            codes_list.remove(block_code)
        except ValueError:
            continue
        for tau in tsets_of_kset_minhd4(np.uint64(block_code), k):
            used_t_to_code.pop(int(tau), None)
        codes_list.append(g)
        for tau in tsets_of_kset_minhd4(np.uint64(g), k):
            used_t_to_code[int(tau)] = g
        if verbose:
            msg = f"iter {iter_counter}: random swap, size unchanged at {len(codes_list)}"
            log.append(msg)

    final = np.asarray(codes_list, dtype=np.uint64)
    return ExchangeResult(
        masks=final,
        iterations_used=iter_counter,
        time_first_100=time_first_100,
        time_last_improvement=time_last_improvement,
        log=log,
    )
