# =============================================================================
# HYDRA-UMC-EDITOR-STL - Before and after of a part: mesh_diff.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# What a transformation did to a part, by comparing the file with the copy that `.trash/` kept before it: the numbers
# (triangles, size, centre, volume) and a picture with both versions laid over each other, seen from the top, the front and the
# side (the version before in amber, the one after in cyan, both semi-transparent). Nothing is written to the model folder.
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .stl_ops import StlOpsError, STL_TRASH_DIRNAME, _part_path, _read_mesh, list_trash

MAX_DRAWN_TRIANGLES = 3000
_PANEL = 300
_MARGIN = 16
_BEFORE = "#e0a030"
_AFTER = "#30c0e0"
#: view name -> (horizontal axis, vertical axis, flip vertical so that "up" in the picture is up in the part)
_VIEWS = {"top": (0, 1), "front": (0, 2), "side": (1, 2)}


@dataclass
class MeshDiff:
    triangles_before: int
    triangles_after: int
    size_before: tuple[float, float, float]
    size_after: tuple[float, float, float]
    center_shift: tuple[float, float, float]
    volume_before: float
    volume_after: float

    @property
    def unchanged(self) -> bool:
        return (
            self.triangles_before == self.triangles_after
            and np.allclose(self.size_before, self.size_after)
            and np.allclose(self.center_shift, 0.0)
            and abs(self.volume_before - self.volume_after) <= 1e-9 * max(1.0, abs(self.volume_before))
        )


def _finite(vectors: np.ndarray) -> np.ndarray:
    return vectors[np.isfinite(vectors).all(axis=(1, 2))].astype(np.float64)


def _signed_volume(vectors: np.ndarray) -> float:
    if len(vectors) == 0:
        return 0.0
    return float(np.einsum("ij,ij->i", vectors[:, 0], np.cross(vectors[:, 1], vectors[:, 2])).sum() / 6.0)


def _box(vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    points = vectors.reshape(-1, 3)
    if len(points) == 0:
        return np.zeros(3), np.zeros(3)
    return points.min(axis=0), points.max(axis=0)


def diff_vectors(before: np.ndarray, after: np.ndarray) -> MeshDiff:
    b, a = _finite(before), _finite(after)
    (b_lo, b_hi), (a_lo, a_hi) = _box(b), _box(a)
    shift = (a_lo + a_hi) / 2.0 - (b_lo + b_hi) / 2.0
    return MeshDiff(
        triangles_before=int(len(before)),
        triangles_after=int(len(after)),
        size_before=tuple(float(v) for v in b_hi - b_lo),
        size_after=tuple(float(v) for v in a_hi - a_lo),
        center_shift=tuple(float(v) for v in shift),
        volume_before=_signed_volume(b),
        volume_after=_signed_volume(a),
    )


def latest_trash_entry(model_dir: Path, filename: str) -> str | None:
    """The newest `.trash/` entry that holds an earlier version of `filename`, or None."""
    for item in list_trash(model_dir):
        if item["original"] == filename:
            return item["entry"]
    return None


def _versions(model_dir: Path, filename: str, entry: str | None) -> tuple[np.ndarray, np.ndarray]:
    current = _part_path(model_dir, filename)
    if not current.is_file():
        raise StlOpsError(f"no such part: {filename}")
    chosen = entry or latest_trash_entry(model_dir, filename)
    if chosen is None:
        raise StlOpsError(f"{filename} has no earlier version in {STL_TRASH_DIRNAME}/ to compare with")
    if "/" in chosen or "\\" in chosen or chosen in (".", ".."):
        raise StlOpsError(f"not a valid trash entry: {chosen!r}")
    old = model_dir / STL_TRASH_DIRNAME / chosen
    if not old.is_file():
        raise StlOpsError(f"no such trash entry: {chosen}")
    return _read_mesh(old).vectors, _read_mesh(current).vectors


def diff_with_trash(model_dir: Path, filename: str, entry: str | None = None) -> MeshDiff:
    before, after = _versions(model_dir, filename, entry)
    return diff_vectors(before, after)


def _sample(vectors: np.ndarray) -> np.ndarray:
    vectors = _finite(vectors)
    if len(vectors) > MAX_DRAWN_TRIANGLES:
        vectors = vectors[np.linspace(0, len(vectors) - 1, MAX_DRAWN_TRIANGLES).astype(np.int64)]
    return vectors


def render_diff_svg(before: np.ndarray, after: np.ndarray) -> str:
    """An SVG with three panels (top, front, side) that lays the version before (amber) and the version after (cyan) over each
    other. A part with more than MAX_DRAWN_TRIANGLES triangles is drawn from an even sample of them."""
    b, a = _sample(before), _sample(after)
    everything = np.vstack([v.reshape(-1, 3) for v in (b, a) if len(v)] or [np.zeros((1, 3))])
    low, high = everything.min(axis=0), everything.max(axis=0)
    inner = _PANEL - 2 * _MARGIN
    width = 3 * _PANEL
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{_PANEL + 24}" viewBox="0 0 {width} {_PANEL + 24}">',
        f'<rect width="{width}" height="{_PANEL + 24}" fill="#101418"/>',
    ]
    for panel, (name, (hx, vx)) in enumerate(_VIEWS.items()):
        span = max(float(high[hx] - low[hx]), float(high[vx] - low[vx]), 1e-9)
        scale = inner / span
        origin_x = panel * _PANEL + _MARGIN
        origin_y = _MARGIN + 18

        def project(points: np.ndarray) -> list[str]:
            x = origin_x + (points[:, hx] - low[hx]) * scale
            y = origin_y + inner - (points[:, vx] - low[vx]) * scale
            return [f"{px:.1f},{py:.1f}" for px, py in zip(x, y)]

        parts.append(f'<text x="{origin_x}" y="{_MARGIN + 8}" fill="#9aa4ad" font-family="sans-serif" font-size="12">{name}</text>')
        for colour, tris in ((_BEFORE, b), (_AFTER, a)):
            parts.append(f'<g fill="{colour}" fill-opacity="0.28" stroke="{colour}" stroke-opacity="0.5" stroke-width="0.3">')
            for tri in tris:
                parts.append(f'<polygon points="{" ".join(project(tri))}"/>')
            parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def render_diff_with_trash(model_dir: Path, filename: str, entry: str | None = None) -> str:
    before, after = _versions(model_dir, filename, entry)
    return render_diff_svg(before, after)
