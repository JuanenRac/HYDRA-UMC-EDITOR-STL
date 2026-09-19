# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for stl_geometry.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# Requires a real QGuiApplication (QQuick3DGeometry is a QML/scenegraph
# type) - conftest.py's own `qt_app` fixture provides one, headless
# (QT_QPA_PLATFORM=offscreen), the same way every other Qt-dependent test
# in this ecosystem already runs in CI with no real display attached.
# =============================================================================
from __future__ import annotations

from pathlib import Path

from hydra_umc_editor_stl.stl_geometry import StlGeometry

from .conftest import make_cube_stl


def test_empty_source_produces_no_vertex_data(qt_app) -> None:
    geometry = StlGeometry()
    assert geometry.vertexData() == b""


def test_a_real_cube_stl_produces_36_vertices_of_24_bytes_each(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=5.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    # 12 triangles * 3 vertices * (3 position floats + 3 normal floats) * 4 bytes
    assert len(geometry.vertexData()) == 12 * 3 * 6 * 4


def test_a_real_cube_stl_reports_its_own_real_bounds(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=5.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    assert (geometry.boundsMin().x(), geometry.boundsMin().y(), geometry.boundsMin().z()) == (0.0, 0.0, 0.0)
    assert (geometry.boundsMax().x(), geometry.boundsMax().y(), geometry.boundsMax().z()) == (5.0, 5.0, 5.0)


def test_a_missing_file_degrades_to_no_vertex_data_instead_of_crashing(qt_app, tmp_path: Path) -> None:
    geometry = StlGeometry()
    geometry.source = str(tmp_path / "does_not_exist.stl")
    assert geometry.vertexData() == b""


def test_setting_the_same_source_twice_is_a_real_no_op(qt_app, tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=5.0)
    geometry = StlGeometry()
    geometry.source = str(cube)
    first = geometry.vertexData()
    geometry.source = str(cube)
    assert geometry.vertexData() == first
