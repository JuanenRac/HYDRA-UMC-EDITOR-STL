from __future__ import annotations

from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

from hydra_umc_editor_stl.mesh_check import check_stl, check_vectors

from .conftest import make_cube_stl


def _cube(path: Path) -> stl_mesh.Mesh:
    make_cube_stl(path, size=10.0)
    return stl_mesh.Mesh.from_file(str(path))


def test_a_closed_cube_is_clean_in_one_orientation_and_inward_in_the_other(tmp_path: Path) -> None:
    mesh = _cube(tmp_path / "c.stl")
    a = check_vectors(mesh.vectors)
    b = check_vectors(mesh.vectors[:, ::-1, :])
    assert a.open_edges == 0 and b.open_edges == 0
    assert abs(abs(a.signed_volume) - 1000.0) < 1e-6
    assert a.signed_volume == -b.signed_volume
    inward = a if a.signed_volume < 0 else b
    outward = b if a.signed_volume < 0 else a
    assert outward.ok, outward.problems
    assert any("point inwards" in p for p in inward.problems)


def test_a_missing_triangle_leaves_the_mesh_open(tmp_path: Path) -> None:
    mesh = _cube(tmp_path / "c.stl")
    report = check_vectors(mesh.vectors[:-1])
    assert report.open_edges > 0
    assert any("not closed" in p for p in report.problems)


def test_degenerate_and_non_finite_triangles_are_counted(tmp_path: Path) -> None:
    mesh = _cube(tmp_path / "c.stl")
    vectors = np.concatenate([mesh.vectors, np.zeros((2, 3, 3), dtype=mesh.vectors.dtype)])
    vectors[-1, 0, 0] = np.nan
    report = check_vectors(vectors)
    assert report.degenerate == 1 and report.non_finite == 1
    assert any("degenerate" in p for p in report.problems)
    assert any("not numbers" in p for p in report.problems)


def test_a_part_in_metres_looks_like_the_wrong_unit(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "small.stl", size=0.1)
    make_cube_stl(tmp_path / "huge.stl", size=90000.0)
    assert any("unit" in p for p in check_stl(tmp_path / "small.stl").problems)
    assert any("unit" in p for p in check_stl(tmp_path / "huge.stl").problems)


def test_normals_that_disagree_with_the_winding_are_reported(tmp_path: Path) -> None:
    mesh = _cube(tmp_path / "c.stl")
    outward = mesh.vectors if check_vectors(mesh.vectors).signed_volume > 0 else mesh.vectors[:, ::-1, :]
    cross = np.cross(outward[:, 1] - outward[:, 0], outward[:, 2] - outward[:, 0])
    assert check_vectors(outward, cross).normal_mismatches == 0
    assert any("normals stored" in p for p in check_vectors(outward, -cross).problems)


def test_an_empty_or_unreadable_file(tmp_path: Path) -> None:
    assert not check_vectors(np.zeros((0, 3, 3))).ok
    (tmp_path / "bad.stl").write_bytes(b"not an stl")
    assert not check_stl(tmp_path / "bad.stl").ok
    assert check_stl(tmp_path / "missing.stl") is None
