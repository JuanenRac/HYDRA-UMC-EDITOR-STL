# =============================================================================
# HYDRA-UMC-EDITOR-STL - Real STL mesh geometry for Qt Quick 3D: stl_geometry.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# A real QQuick3DGeometry that loads an actual STL file's own triangles
# (via numpy-stl, the same library stl_ops.py already depends on) into a
# Qt Quick 3D vertex buffer - non-indexed, one flat per-facet normal
# copied onto each of its own 3 vertices, which is exactly what a binary
# STL's own data already is (no shared-vertex smoothing to reconstruct,
# and none invented here). Exposed to QML as `StlGeometry { source: "..."
# }`, used as a `View3D`'s `Model.geometry` - see Main.qml.
# =============================================================================
from __future__ import annotations

import numpy as np
from PySide6.QtCore import Property, Signal
from PySide6.QtGui import QVector3D
from PySide6.QtQuick3D import QQuick3DGeometry
from stl import mesh as stl_mesh

_FLOATS_PER_VERTEX = 6  # position.xyz + normal.xyz
_STRIDE_BYTES = _FLOATS_PER_VERTEX * 4  # float32


class StlGeometry(QQuick3DGeometry):
    sourceChanged = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source = ""

    @Property(str, notify=sourceChanged)
    def source(self) -> str:
        return self._source

    @source.setter  # type: ignore[no-redef]
    def source(self, value: str) -> None:
        if value == self._source:
            return
        self._source = value
        self.sourceChanged.emit()
        self._rebuild()

    def _rebuild(self) -> None:
        self.clear()
        if not self._source:
            self.update()
            return
        try:
            mesh = stl_mesh.Mesh.from_file(self._source)
        except Exception:
            # A genuinely unreadable/missing file shows as an empty
            # model in the 3D view (nothing drawn) rather than crashing
            # the whole app - the parts LIST (backed by real disk stats,
            # not this loader) is still the honest source of truth for
            # "does this part exist".
            self.update()
            return
        if len(mesh.vectors) == 0:
            self.update()
            return

        # mesh.vectors: (N, 3, 3) - N triangles, 3 vertices, xyz each.
        # mesh.normals: (N, 3) - one real face normal per triangle,
        # copied onto its own 3 vertices below (flat shading, matching
        # what a binary STL actually stores - never smoothed/invented).
        vertices = mesh.vectors.astype(np.float32).reshape(-1, 3)
        normals = np.repeat(mesh.normals.astype(np.float32), 3, axis=0)
        # A degenerate/zero-length normal (a real, if rare, malformed
        # facet) would otherwise light as pure black - normalized here,
        # falling back to a real "pointing up" default only for the
        # exact zero-vector case so nothing divides by zero.
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        safe_lengths = np.where(lengths > 1e-12, lengths, 1.0)
        normals = np.where(lengths > 1e-12, normals / safe_lengths, np.array([0.0, 0.0, 1.0], dtype=np.float32))

        interleaved = np.empty((vertices.shape[0], _FLOATS_PER_VERTEX), dtype=np.float32)
        interleaved[:, 0:3] = vertices
        interleaved[:, 3:6] = normals

        self.setVertexData(interleaved.tobytes())
        self.setStride(_STRIDE_BYTES)
        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Triangles)
        self.addAttribute(
            QQuick3DGeometry.Attribute.Semantic.PositionSemantic, 0,
            QQuick3DGeometry.Attribute.ComponentType.F32Type,
        )
        self.addAttribute(
            QQuick3DGeometry.Attribute.Semantic.NormalSemantic, 3 * 4,
            QQuick3DGeometry.Attribute.ComponentType.F32Type,
        )
        min_xyz = vertices.min(axis=0)
        max_xyz = vertices.max(axis=0)
        self.setBounds(QVector3D(*min_xyz.tolist()), QVector3D(*max_xyz.tolist()))
        self.update()
