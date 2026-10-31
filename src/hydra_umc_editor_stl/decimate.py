# =============================================================================
# HYDRA-UMC-EDITOR-STL - Light copies of a part: decimate.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# A lighter version of a part for the apps that cannot carry the full mesh: the vertices are merged cell by cell on a grid
# (vertex clustering), the triangles that collapse are dropped, and the grid is searched so that the result has about the
# wanted share of the triangles. The original file is never touched: the light copy goes to `.lite/<part>` in the model
# folder (a hidden folder, so it is not listed as a part). Vertex clustering keeps the outline and the size of the part but
# does not promise a closed mesh, so the copy is for looking at, not for printing.
# =============================================================================
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

from .stl_ops import StlOpsError, _part_path, _read_mesh, _save_mesh_atomically

LITE_DIRNAME = ".lite"
DEFAULT_RATIO = 0.2
MIN_TRIANGLES = 4
_SEARCH_STEPS = 14
_MAX_CELLS = 8192


def cluster_decimate(vectors: np.ndarray, cells: int) -> np.ndarray:
    """The triangles ((M, 3, 3)) left after merging the vertices that fall in the same cell of a grid with `cells` cells along the
    longest side of the part. The merged vertex is the mean of the vertices of its cell."""
    cells = max(1, int(cells))
    points = vectors.reshape(-1, 3).astype(np.float64)
    low = points.min(axis=0)
    side = float((points.max(axis=0) - low).max())
    if side <= 0.0:
        return vectors[:0].astype(np.float64)
    index = np.floor((points - low) / (side / cells)).astype(np.int64)
    dims = index.max(axis=0) + 1
    key = (index[:, 0] * dims[1] + index[:, 1]) * dims[2] + index[:, 2]
    _, inverse = np.unique(key, return_inverse=True)
    inverse = inverse.reshape(-1)
    counts = np.bincount(inverse).astype(np.float64)
    merged = np.stack([np.bincount(inverse, weights=points[:, axis]) / counts for axis in range(3)], axis=1)
    corners = inverse.reshape(-1, 3)
    alive = (corners[:, 0] != corners[:, 1]) & (corners[:, 1] != corners[:, 2]) & (corners[:, 0] != corners[:, 2])
    return merged[corners[alive]]


def decimate_to_ratio(vectors: np.ndarray, ratio: float) -> np.ndarray:
    """A copy of the triangles reduced to about `ratio` of their number (never more than the original, never fewer than a few).
    A `ratio` of 1 or more returns the triangles unchanged; a ratio that is not a number in (0, 1] is refused."""
    if not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or ratio <= 0:
        raise ValueError(f"the ratio must be a number above 0 and up to 1, got {ratio!r}")
    finite = vectors[np.isfinite(vectors).all(axis=(1, 2))]
    if ratio >= 1.0 or len(finite) <= MIN_TRIANGLES:
        return finite.astype(np.float64)
    target = max(MIN_TRIANGLES, int(math.ceil(len(finite) * ratio)))
    low, high = 1, _MAX_CELLS
    best = cluster_decimate(finite, low)
    for _ in range(_SEARCH_STEPS):  # the triangle count grows with the number of cells: look for the finest grid within the target
        middle = (low + high) // 2
        if middle == low:
            break
        candidate = cluster_decimate(finite, middle)
        if len(candidate) <= target:
            best, low = candidate, middle
        else:
            high = middle
    if len(best) == 0:  # a grid that coarse can collapse the whole part: the smallest grid that keeps something
        for cells in range(2, _MAX_CELLS):
            best = cluster_decimate(finite, cells)
            if len(best):
                break
    return best


def make_light_copy(model_dir: Path, filename: str, ratio: float = DEFAULT_RATIO) -> dict:
    """Writes the light copy of one part to `.lite/<filename>` and returns what was done:
    `{"part", "path", "triangles_before", "triangles_after", "bytes_before", "bytes_after"}`. The part itself is not changed."""
    source = _part_path(model_dir, filename)
    if not source.is_file():
        raise StlOpsError(f"no such part: {filename}")
    mesh = _read_mesh(source)
    try:
        reduced = decimate_to_ratio(mesh.vectors, ratio)
    except ValueError as error:
        raise StlOpsError(str(error)) from error
    if len(reduced) == 0:
        raise StlOpsError(f"{filename} has no usable triangles")
    light = stl_mesh.Mesh(np.zeros(len(reduced), dtype=stl_mesh.Mesh.dtype))
    light.vectors[:] = reduced.astype(np.float32)
    light.update_normals()
    target = model_dir / LITE_DIRNAME / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    _save_mesh_atomically(light, target)
    return {
        "part": filename,
        "path": target,
        "triangles_before": int(len(mesh.vectors)),
        "triangles_after": int(len(reduced)),
        "bytes_before": source.stat().st_size,
        "bytes_after": target.stat().st_size,
    }
