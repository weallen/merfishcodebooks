"""CSV I/O matching the R reference's output conventions.

The R reference writes:
  - `{prefix}Binary.csv` : space-separated 0/1 matrix, no header.
  - `{prefix}Set.csv`    : space-separated 1-indexed bit positions, no header.
  - `meta_{prefix}.txt`  : key-value listing of generation metadata.

We preserve those formats so this package is a drop-in replacement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from .bitmask import binary_to_masks, decode_set_array, masks_to_binary


def read_codebook_csv(path: str | Path, sep: str = " ") -> np.ndarray:
    """Read a codebook CSV (binary or set-form) and return uint64 bitmasks.

    The format is auto-detected: if every cell is 0 or 1, treat as binary; otherwise
    treat as set-form (1-indexed bit positions).
    """
    path = Path(path)
    raw = np.loadtxt(path, dtype=np.int64, delimiter=None if sep.isspace() else sep)
    if raw.ndim == 1:
        raw = raw.reshape(1, -1)
    if raw.size == 0:
        return np.empty(0, dtype=np.uint64)

    if raw.max() <= 1 and raw.min() >= 0:
        return binary_to_masks(raw.astype(np.uint8))
    # Set form: rows are 1-indexed bit positions. Encode each row.
    from .bitmask import encode_set_array
    return encode_set_array(raw)


def write_binary_csv(path: str | Path, masks: np.ndarray, v: int, sep: str = " ") -> None:
    """Write codes as an N×v 0/1 matrix (R's `Binary.csv` format)."""
    binary = masks_to_binary(np.asarray(masks, dtype=np.uint64), v)
    np.savetxt(path, binary, fmt="%d", delimiter=sep)


def write_set_csv(path: str | Path, masks: np.ndarray, k: int, sep: str = " ") -> None:
    """Write codes as an N×k matrix of 1-indexed bit positions (R's `Set.csv` format)."""
    sets = decode_set_array(np.asarray(masks, dtype=np.uint64), k)
    np.savetxt(path, sets, fmt="%d", delimiter=sep)


def write_metadata(path: str | Path, metadata: Mapping[str, object]) -> None:
    """Write a key-value text file mirroring the R `sink(metafilename); print(metadata)` output.

    Keys are written verbatim, values are stringified. Two-column aligned for readability.
    """
    items = [(str(k), str(v)) for k, v in metadata.items()]
    width = max(len(k) for k, _ in items) if items else 0
    lines = [f"{k:<{width}}  {v}" for k, v in items]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
