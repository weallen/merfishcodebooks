"""Top-level pipeline: pick a starting codebook, prune, scavenge, output.

Port of `0_CodebookGeneratingPipeline.R`. Public API is `generate_codebook(...)` and the
`Start` strategy factory.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from .bitmask import MAX_BITS, binary_to_masks, encode_set_array, popcount_array
from .conversion import set_to_binary
from .exchange import iterative_set_exchange
from .hd import validate_min_hd
from .io import read_codebook_csv, write_binary_csv, write_metadata, write_set_csv
from .johnson import johnson_bound
from .lajolla import LaJollaCover, fetch_lajolla_cover
from .pruning import prune_to_min_hd


# ---------------------------------------------------------------------------
# Start strategy
# ---------------------------------------------------------------------------

class _StartKind(str, Enum):
    fresh = "fresh"
    csv = "csv"
    lajolla = "lajolla"
    puncture = "puncture"
    range_puncture = "range_puncture"


@dataclass
class Start:
    kind: _StartKind
    csv_path: Path | None = None
    csv_sep: str = " "
    puncture_v: int | None = None
    range_upper_limit: int | None = None

    @classmethod
    def fresh(cls) -> "Start":
        return cls(kind=_StartKind.fresh)

    @classmethod
    def csv(cls, path: str | Path, sep: str = " ") -> "Start":
        return cls(kind=_StartKind.csv, csv_path=Path(path), csv_sep=sep)

    @classmethod
    def lajolla(cls) -> "Start":
        return cls(kind=_StartKind.lajolla)

    @classmethod
    def puncture(cls, source_v: int) -> "Start":
        """Use a (source_v, k, t) covering and drop blocks using bits > target v."""
        return cls(kind=_StartKind.puncture, puncture_v=source_v)

    @classmethod
    def range_puncture(cls, upper_limit: int | None = None) -> "Start":
        """Try (v..upper_limit) coverings, prune each, keep the largest."""
        return cls(kind=_StartKind.range_puncture, range_upper_limit=upper_limit)


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class CodebookResult:
    bits: int
    hw: int
    min_hd: int
    masks: np.ndarray                   # (N,) uint64 — final codebook
    johnson_bound: int
    iterations_used: int
    strategy: str
    start_method: str | None = None
    pruning_n_removed: int = 0
    pruning_n_after: int | None = None
    timing: dict[str, float] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return int(self.masks.shape[0])

    @property
    def pct_of_bound(self) -> float:
        if self.johnson_bound == 0:
            return 0.0
        return 100.0 * self.size / self.johnson_bound

    @property
    def codes_binary(self) -> np.ndarray:
        from .bitmask import masks_to_binary
        return masks_to_binary(self.masks, self.bits)

    @property
    def codes_set(self) -> np.ndarray:
        from .bitmask import decode_set_array
        return decode_set_array(self.masks, self.hw)

    def write(self, output_dir: str | Path, prefix: str | None = None) -> dict[str, Path]:
        """Write the three R-compatible output files. Returns the paths written."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        if prefix is None:
            prefix = f"{self.bits}Bit_HW{self.hw}_HD{self.min_hd}_finalsize{self.size}"
        binary_path = output_dir / f"{prefix}Binary.csv"
        set_path = output_dir / f"{prefix}Set.csv"
        meta_path = output_dir / f"meta_{prefix}.txt"

        write_binary_csv(binary_path, self.masks, self.bits)
        write_set_csv(set_path, self.masks, self.hw)
        write_metadata(meta_path, self._metadata_dict())

        return {"binary": binary_path, "set": set_path, "meta": meta_path}

    def _metadata_dict(self) -> dict[str, Any]:
        d = {
            "Barcode Length": self.bits,
            "Hamming Weight": self.hw,
            "Minimum Hamming Distance": self.min_hd,
            "Theoretical Max (Johnson Bound)": self.johnson_bound,
            "StrategyUsed": self.strategy,
            "Final Codebook Size": self.size,
            "Percentage Yield in %": round(self.pct_of_bound, 4),
            "Starting Code Method": self.start_method,
            "Pruning: Codes Removed": self.pruning_n_removed,
            "Pruning: Codebook Size After Pruning": self.pruning_n_after,
            "Iterations Used": self.iterations_used,
        }
        d.update({f"Timing: {k}": v for k, v in self.timing.items()})
        return d


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def generate_codebook(
    bits: int,
    hw: int = 4,
    min_hd: int = 4,
    *,
    start: Start | None = None,
    max_iterations: int = 300,
    dynamic_max_iterations: bool = True,
    candidate_cutoff: int = 1,
    rng: int | np.random.Generator | None = None,
    verbose: bool = False,
) -> CodebookResult:
    """Generate a MERFISH codebook.

    Parameters mirror the R reference's `ErrorRobustCodebookGeneratorPunct(...)` function.
    """
    if bits < 1 or bits > MAX_BITS:
        raise ValueError(f"bits must be in [1, {MAX_BITS}]; got {bits}.")
    if hw < 1 or hw > bits:
        raise ValueError(f"hw must be in [1, bits]; got hw={hw}, bits={bits}.")
    if min_hd != 4:
        raise NotImplementedError("Only min_hd=4 is currently supported.")
    rng = _coerce_rng(rng)
    start = start if start is not None else Start.lajolla()
    t = hw - (min_hd // 2 - 1)   # = hw - 1 for minHD=4

    timing: dict[str, float] = {}
    t_start = time.perf_counter()
    bound = johnson_bound(bits, hw, min_hd)

    # ---- Choose a starting codebook ----
    masks, start_method, strategy_label = _build_starting_codebook(
        bits=bits, hw=hw, t=t, start=start, rng=rng, verbose=verbose,
    )
    timing["start_chosen_s"] = time.perf_counter() - t_start

    # ---- Validate Hamming weights ----
    if masks.size:
        weights = popcount_array(masks)
        if not (weights == hw).all():
            raise ValueError("Starting codebook contains rows with the wrong Hamming weight.")

    # ---- Prune any minHD violations ----
    pruning_n_removed = 0
    pruning_n_after: int | None = None
    if masks.size:
        ok, n_violations = validate_min_hd(masks, min_hd)
        if not ok:
            if verbose:
                print(f"Detected {n_violations} minHD violations; pruning.")
            pruning_result = prune_to_min_hd(masks, min_hd, rng=rng)
            masks = pruning_result.masks
            pruning_n_removed = pruning_result.n_removed
            pruning_n_after = pruning_result.n_after_pruning
    timing["after_pruning_s"] = time.perf_counter() - t_start

    if verbose:
        print(f"Starting codebook: {len(masks)} codes ({100 * len(masks) / max(bound, 1):.1f}% of Johnson bound).")

    # ---- Iterative set exchange (scavenging) ----
    iterations_used = 0
    if bound and len(masks) < bound:
        # FreshStart needs an initial code if empty.
        if masks.size == 0:
            masks = np.array([sum(1 << i for i in range(hw))], dtype=np.uint64)
        result = iterative_set_exchange(
            v=bits, k=hw, codes=masks, min_hd=min_hd,
            max_iterations=max_iterations,
            dynamic_max_iterations=dynamic_max_iterations,
            candidate_cutoff=candidate_cutoff,
            theoretical_max=bound,
            rng=rng,
            verbose=verbose,
        )
        masks = result.masks
        iterations_used = result.iterations_used
        if result.time_first_100 is not None:
            timing["first_100_iter_s"] = result.time_first_100
        if result.time_last_improvement is not None:
            timing["last_improvement_s"] = result.time_last_improvement

    timing["total_s"] = time.perf_counter() - t_start

    # ---- Final validation ----
    ok, n_violations = validate_min_hd(masks, min_hd)
    if not ok:
        raise RuntimeError(f"Final codebook failed minHD={min_hd} check: {n_violations} violations.")

    return CodebookResult(
        bits=bits,
        hw=hw,
        min_hd=min_hd,
        masks=masks,
        johnson_bound=bound,
        iterations_used=iterations_used,
        strategy=strategy_label,
        start_method=start_method,
        pruning_n_removed=pruning_n_removed,
        pruning_n_after=pruning_n_after,
        timing=timing,
    )


def _coerce_rng(rng: int | np.random.Generator | None) -> np.random.Generator:
    if rng is None:
        return np.random.default_rng()
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)


def _build_starting_codebook(
    *, bits: int, hw: int, t: int, start: Start, rng: np.random.Generator, verbose: bool,
) -> tuple[np.ndarray, str | None, str]:
    """Return (mask vector, method string, strategy label) for the chosen start strategy."""
    if start.kind == _StartKind.fresh:
        masks = np.array([sum(1 << i for i in range(hw))], dtype=np.uint64)
        return masks, None, "FreshStart"

    if start.kind == _StartKind.csv:
        masks = read_codebook_csv(start.csv_path, sep=start.csv_sep)
        return masks, f"csv:{start.csv_path}", "CustomStartingFile"

    if start.kind == _StartKind.lajolla:
        cover = fetch_lajolla_cover(bits, hw, t)
        masks = encode_set_array(cover.blocks)
        return masks, cover.method, "StartWithCoveringDesign"

    if start.kind == _StartKind.puncture:
        if start.puncture_v is None or start.puncture_v < bits:
            raise ValueError("puncture requires source_v >= target bits.")
        cover = fetch_lajolla_cover(start.puncture_v, hw, t)
        # Drop blocks that use any bit > target v.
        keep = cover.blocks.max(axis=1) <= bits
        blocks = cover.blocks[keep]
        masks = encode_set_array(blocks)
        return masks, f"punctured from v={start.puncture_v}: {cover.method}", "PunctureSpecificCoveringStart"

    if start.kind == _StartKind.range_puncture:
        upper = start.range_upper_limit or (bits + 1)
        best_size = -1
        best_masks = np.empty(0, dtype=np.uint64)
        best_method = None
        for v_plus in range(bits, upper + 1):
            try:
                cover = fetch_lajolla_cover(v_plus, hw, t)
            except Exception as exc:
                if verbose:
                    print(f"  range puncture: skipping v={v_plus} ({exc})")
                continue
            keep = cover.blocks.max(axis=1) <= bits
            blocks = cover.blocks[keep]
            masks = encode_set_array(blocks)
            # Prune to evaluate effective size.
            ok, _ = validate_min_hd(masks, 4)
            if not ok:
                pr = prune_to_min_hd(masks, 4, rng=rng)
                masks_eval = pr.masks
            else:
                masks_eval = masks
            if verbose:
                print(f"  range puncture: v={v_plus}, after pruning size={len(masks_eval)}")
            if len(masks_eval) > best_size:
                best_size = len(masks_eval)
                best_masks = masks
                best_method = f"range puncture from v={v_plus}: {cover.method}"
        if best_size < 0:
            raise RuntimeError("range puncture: no covering design fetchable for the chosen range.")
        return best_masks, best_method, "PunctureCoveringRange"

    raise ValueError(f"Unknown start kind: {start.kind}")
