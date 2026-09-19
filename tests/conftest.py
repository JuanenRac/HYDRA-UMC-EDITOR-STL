# =============================================================================
# HYDRA-UMC-EDITOR-STL - shared test fixtures: conftest.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh


def make_cube_stl(path: Path, size: float = 10.0) -> None:
    """Writes a real, valid binary STL - a unit cube scaled by `size`,
    the same 12-triangle cube every numpy-stl example ships, so tests
    exercise a real parseable file rather than hand-rolled bytes."""
    vertices = np.array([
        [0, 0, 0], [size, 0, 0], [size, size, 0], [0, size, 0],
        [0, 0, size], [size, 0, size], [size, size, size], [0, size, size],
    ])
    faces = np.array([
        [0, 3, 1], [1, 3, 2],
        [0, 4, 7], [0, 7, 3],
        [4, 5, 6], [4, 6, 7],
        [5, 1, 2], [5, 2, 6],
        [2, 3, 6], [3, 7, 6],
        [0, 1, 5], [0, 5, 4],
    ])
    cube = stl_mesh.Mesh(np.zeros(faces.shape[0], dtype=stl_mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[face[j]]
    path.parent.mkdir(parents=True, exist_ok=True)
    cube.save(str(path))


@pytest.fixture(scope="session")
def qt_app():
    """A real, single, session-scoped QGuiApplication - QQuick3DGeometry
    (stl_geometry.py) is a real Qt/QML type and cannot be instantiated
    without one. Headless: relies on QT_QPA_PLATFORM=offscreen being set
    in the environment this test suite runs in (see build-test.sh/CI),
    same as every other Qt-dependent test in this ecosystem."""
    from PySide6.QtGui import QGuiApplication
    app = QGuiApplication.instance() or QGuiApplication([])
    yield app


@pytest.fixture
def ecosystem_root(tmp_path: Path) -> Path:
    """A real, minimal ecosystem checkout layout - just enough of
    HYDRA-UMC-STUDIO's own public/models/ tree for model_catalog.py to
    discover for real, no mocking of the filesystem itself."""
    root = tmp_path / "ecosystem"
    model_dir = root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ar3"
    make_cube_stl(model_dir / "base_link.STL")
    make_cube_stl(model_dir / "link_1.STL")
    (model_dir / "ATTRIBUTION.txt").write_text("MIT - Annin Robotics\n", encoding="utf-8")
    (model_dir / "metadata.json").write_text(
        '{"schemaVersion": 1, "id": "ar3", "model": "AR3 (6-DOF)", "manufacturer": "Annin Robotics", "dof": 6, "category": "robots-6-dof"}',
        encoding="utf-8",
    )
    return root
