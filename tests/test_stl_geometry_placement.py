# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the assembled placement and the odd meshes
# of stl_geometry.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh

# these need the optional GUI extra (PySide6); the rest of the suite does not
pytest.importorskip("PySide6")

from hydra_umc_editor_stl.stl_geometry import StlGeometry

from .conftest import make_cube_stl


def _vertices(geometry: StlGeometry) -> np.ndarray:
    data = np.frombuffer(bytes(geometry.vertexData()), dtype=np.float32)
    return data.reshape(-1, 6)


def test_a_placement_moves_the_vertices_and_the_bounds(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=2.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    # rotate 90 degrees about z (x -> y), then move by (10, 20, 30)
    geometry.placement = [0, -1, 0, 1, 0, 0, 0, 0, 1, 10, 20, 30]
    low, high = geometry.boundsMin(), geometry.boundsMax()
    assert (low.x(), low.y(), low.z()) == pytest.approx((8.0, 20.0, 30.0))
    assert (high.x(), high.y(), high.z()) == pytest.approx((10.0, 22.0, 32.0))
    normals = _vertices(geometry)[:, 3:6]
    assert np.allclose(np.linalg.norm(normals, axis=1), 1.0, atol=1e-5)


def test_a_placement_of_the_wrong_length_is_ignored(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=2.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    geometry.placement = [1, 2, 3]
    assert geometry.boundsMax().x() == pytest.approx(2.0)
    assert geometry.placement == [1.0, 2.0, 3.0]


def test_setting_the_same_placement_twice_changes_nothing(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=2.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    changes: list[int] = []
    geometry.placementChanged.connect(lambda: changes.append(1))
    geometry.placement = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    geometry.placement = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    assert changes == [1]
    geometry.placement = []
    assert changes == [1, 1]


def test_clearing_the_source_empties_the_geometry(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=2.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    assert len(geometry.vertexData()) > 0
    geometry.source = ""
    assert geometry.vertexData() == b""


def test_files_that_are_not_meshes_draw_nothing(qt_app, tmp_path: Path) -> None:
    for name, content in (("empty.stl", b""), ("junk.stl", b"not an stl" * 20), ("header.stl", b"\x00" * 84)):
        path = tmp_path / name
        path.write_bytes(content)
        geometry = StlGeometry()
        geometry.source = str(path)
        assert geometry.vertexData() == b"", name


def test_a_facet_with_a_zero_normal_is_lit_as_pointing_up(qt_app, tmp_path: Path) -> None:
    triangle = stl_mesh.Mesh(np.zeros(1, dtype=stl_mesh.Mesh.dtype))
    triangle.vectors[0] = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    triangle.normals[0] = (0.0, 0.0, 0.0)
    path = tmp_path / "flat.stl"
    triangle.save(str(path))
    # the writer recomputes normals; write the zero normal back into the bytes
    data = bytearray(path.read_bytes())
    data[84:96] = b"\x00" * 12
    path.write_bytes(bytes(data))

    geometry = StlGeometry()
    geometry.source = str(path)
    vertices = _vertices(geometry)
    assert vertices.shape == (3, 6)
    assert np.allclose(vertices[:, 3:6], [0.0, 0.0, 1.0])
