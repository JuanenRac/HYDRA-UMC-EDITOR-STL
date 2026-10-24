# =============================================================================
# HYDRA-UMC-EDITOR-STL - Mesh checks before a push: mesh_check.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# What is wrong with a mesh that would be uploaded to the catalog as it is: triangles without area, coordinates that are
# not numbers, edges that belong to one triangle or to more than two (the mesh is not closed), a winding that points the
# faces inwards, normals stored in the file that disagree with the winding, and a size that looks like the wrong unit.
# The checks are vectorised (numpy) and only read the file.
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

#: A triangle whose area is below this (in the squared unit of the file) has no area.
DEGENERATE_AREA = 1e-12
#: The largest side of a part outside this range (in the unit of the file) looks like the wrong unit (metres or micrometres).
SIZE_RANGE = (0.5, 5000.0)
#: Vertices equal up to this many decimals are the same vertex when edges are matched.
WELD_DECIMALS = 6


@dataclass
class MeshReport:
    triangles: int = 0
    non_finite: int = 0
    degenerate: int = 0
    open_edges: int = 0
    non_manifold_edges: int = 0
    signed_volume: float = 0.0
    normal_mismatches: int = 0
    largest_side: float = 0.0
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def check_vectors(vectors: np.ndarray, normals: np.ndarray | None = None) -> MeshReport:
    """The report of a mesh given as an (N, 3, 3) array of triangles and, optionally, the (N, 3) normals the file stores."""
    report = MeshReport(triangles=int(len(vectors)))
    if report.triangles == 0:
        report.problems.append("the mesh has no triangles")
        return report
    finite = np.isfinite(vectors).all(axis=(1, 2))
    report.non_finite = int((~finite).sum())
    good = vectors[finite].astype(np.float64)
    if report.non_finite:
        report.problems.append(f"{report.non_finite} triangle(s) have coordinates that are not numbers")
    if len(good) == 0:
        return report
    cross = np.cross(good[:, 1] - good[:, 0], good[:, 2] - good[:, 0])
    area2 = np.linalg.norm(cross, axis=1)
    live = area2 / 2.0 >= DEGENERATE_AREA
    report.degenerate = int((~live).sum())
    if report.degenerate:
        report.problems.append(f"{report.degenerate} degenerate triangle(s) (no area)")

    # Every edge of a closed mesh belongs to exactly two triangles.
    flat = np.round(good, WELD_DECIMALS).reshape(-1, 3)
    _, inverse = np.unique(flat, axis=0, return_inverse=True)
    ids = inverse.reshape(-1, 3)[live]
    if len(ids):
        edges = np.concatenate([ids[:, [0, 1]], ids[:, [1, 2]], ids[:, [2, 0]]])
        _, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
        report.open_edges = int((counts == 1).sum())
        report.non_manifold_edges = int((counts > 2).sum())
        if report.open_edges:
            report.problems.append(f"the mesh is not closed ({report.open_edges} edge(s) belong to one triangle)")
        if report.non_manifold_edges:
            report.problems.append(f"{report.non_manifold_edges} edge(s) belong to more than two triangles")
        if report.open_edges == 0 and report.non_manifold_edges == 0:
            g = good[live]
            report.signed_volume = float(np.einsum("ij,ij->i", g[:, 0], np.cross(g[:, 1], g[:, 2])).sum() / 6.0)
            if report.signed_volume < 0:
                report.problems.append("the faces point inwards (negative volume)")

    if normals is not None and len(normals) == len(vectors):
        stored = normals[finite].astype(np.float64)
        stored_len = np.linalg.norm(stored, axis=1)
        usable = (area2 > 0) & (stored_len > 0)
        if usable.any():
            dots = np.einsum("ij,ij->i", cross[usable] / area2[usable, None], stored[usable] / stored_len[usable, None])
            report.normal_mismatches = int((dots < 0).sum())
            if report.normal_mismatches > 0.5 * usable.sum():
                report.problems.append("the normals stored in the file disagree with the winding of most faces")

    extent = good.reshape(-1, 3).max(axis=0) - good.reshape(-1, 3).min(axis=0)
    report.largest_side = float(extent.max())
    if report.largest_side < SIZE_RANGE[0] or report.largest_side > SIZE_RANGE[1]:
        report.problems.append(f"the largest side is {report.largest_side:g}: the unit may be wrong (expected millimetres)")
    return report


def check_stl(path: Path) -> MeshReport | None:
    """The report of an STL file, or None when it cannot be read (the file check of the editor says that)."""
    try:
        mesh = stl_mesh.Mesh.from_file(str(path))
    except Exception:
        return None
    return check_vectors(mesh.vectors, mesh.normals)
