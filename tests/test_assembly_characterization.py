# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests/test_assembly_characterization.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Characterization tests for the unit rules, quaternion conversion, placement
helpers and bounds of assembly.py; they pin today's behavior."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl import assembly
from hydra_umc_editor_stl.assembly import PartPlacement


def _write_box(path: Path, size: float) -> None:
    m = stl_mesh.Mesh(np.zeros(2, dtype=stl_mesh.Mesh.dtype))
    m.vectors[0] = np.array([[0, 0, 0], [size, 0, 0], [0, size, 0]], dtype=np.float32)
    m.vectors[1] = np.array([[0, 0, 0], [0, 0, size], [size, 0, 0]], dtype=np.float32)
    m.save(str(path))


@pytest.mark.parametrize(
    "metadata, expected",
    [
        ({"unit": "mm"}, "mm"),
        ({"unit": " Millimetres "}, "mm"),
        ({"units": "Meters"}, "m"),
        ({"unit": "m"}, "m"),
        ({"unit": "inch"}, None),
        ({"unit": 5}, None),
        ({}, None),
        ([], None),
        (None, None),
    ],
)
def test_unit_from_metadata(metadata, expected) -> None:
    assert assembly.unit_from_metadata(metadata) == expected


def test_model_unit_reads_metadata_then_catalog(tmp_path: Path) -> None:
    assert assembly.model_unit(tmp_path) is None
    (tmp_path / "catalog.json").write_text(json.dumps({"unit": "m"}), encoding="utf-8")
    assert assembly.model_unit(tmp_path) == "m"
    # metadata.json has priority over catalog.json
    (tmp_path / "metadata.json").write_text(json.dumps({"unit": "mm"}), encoding="utf-8")
    assert assembly.model_unit(tmp_path) == "mm"


def test_model_unit_with_broken_json_is_none(tmp_path: Path) -> None:
    (tmp_path / "metadata.json").write_text("{nope", encoding="utf-8")
    assert assembly.model_unit(tmp_path) is None


def test_mesh_unit_declared_wins_then_span_rule(tmp_path: Path) -> None:
    small, big = tmp_path / "small.stl", tmp_path / "big.stl"
    _write_box(small, 1.0)
    _write_box(big, 50.0)
    assert assembly._mesh_is_millimeters(small, "mm") is True
    assert assembly._mesh_is_millimeters(big, "m") is False
    assert assembly._mesh_is_millimeters(small) is False
    assert assembly._mesh_is_millimeters(big) is True
    assert assembly._mesh_is_millimeters(tmp_path / "missing.stl") is False


def test_quaternion_branches_roundtrip_through_rotation_matrix() -> None:
    def rot(axis: str, deg: float) -> np.ndarray:
        a = np.radians(deg)
        c, s = np.cos(a), np.sin(a)
        return {
            "x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]),
            "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
            "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]),
        }[axis]

    # identity -> trace branch; 180 degree turns exercise the three other branches
    for matrix in (np.eye(3), rot("x", 180), rot("y", 180), rot("z", 180), rot("x", 30) @ rot("z", 70)):
        quat = assembly._quaternion_wxyz(matrix)
        assert pytest.approx(1.0, abs=1e-6) == sum(v * v for v in quat)
        assert np.allclose(assembly._rotation_matrix(quat), matrix, atol=1e-6)


def test_placement_scales_translation_only_for_millimeters() -> None:
    matrix = np.eye(4)
    matrix[:3, 3] = [0.1, 0.2, 0.3]
    in_mm = assembly._placement(matrix, True)
    in_m = assembly._placement(matrix, False)
    assert in_mm.position == pytest.approx((100.0, 200.0, 300.0))
    assert in_m.position == pytest.approx((0.1, 0.2, 0.3))
    assert in_mm.rotation_wxyz == pytest.approx((1.0, 0.0, 0.0, 0.0))


def test_placement_matrix_is_row_major_rotation_then_translation() -> None:
    flat = assembly.placement_matrix(PartPlacement(position=(1.0, 2.0, 3.0), rotation_wxyz=(1.0, 0.0, 0.0, 0.0)))
    assert flat[:9] == pytest.approx([1, 0, 0, 0, 1, 0, 0, 0, 1])
    assert flat[9:] == pytest.approx([1.0, 2.0, 3.0])


def test_assembled_bounds_applies_translation_and_skips_missing(tmp_path: Path) -> None:
    _write_box(tmp_path / "a.stl", 2.0)
    placements = {
        "a.stl": PartPlacement(position=(10.0, 0.0, 0.0), rotation_wxyz=(1.0, 0.0, 0.0, 0.0)),
        "gone.stl": PartPlacement(position=(500.0, 0.0, 0.0), rotation_wxyz=(1.0, 0.0, 0.0, 0.0)),
    }
    lo, hi = assembly.assembled_bounds(tmp_path, placements)
    assert lo == pytest.approx((10.0, 0.0, 0.0))
    assert hi == pytest.approx((12.0, 2.0, 2.0))
    assert assembly.assembled_bounds(tmp_path, {}) is None


def test_assembled_transforms_without_suite_checkout_is_none(tmp_path: Path) -> None:
    assert assembly.assembled_transforms(tmp_path, "robots", "x", tmp_path) is None
    # a SUITE folder that is not a git checkout is never imported
    (tmp_path / assembly.SUITE_DIRNAME / "hydra_suite" / "render").mkdir(parents=True)
    (tmp_path / assembly.SUITE_DIRNAME / "hydra_suite" / "render" / "kinematics.py").write_text("raise SystemExit", encoding="utf-8")
    assert assembly._load_suite_modules(tmp_path) is None
    # a git checkout without the kinematics module is not imported either
    other = tmp_path / "other"
    (other / assembly.SUITE_DIRNAME / ".git").mkdir(parents=True)
    assert assembly._load_suite_modules(other) is None


def test_load_suite_modules_import_failure_restores_sys_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    # work on a copy of sys.modules so the failed fake import never leaks into other tests
    monkeypatch.setattr(sys, "modules", dict(sys.modules))

    render = tmp_path / assembly.SUITE_DIRNAME / "hydra_suite" / "render"
    render.mkdir(parents=True)
    (tmp_path / assembly.SUITE_DIRNAME / ".git").mkdir()
    (render / "kinematics.py").write_text("raise RuntimeError('boom')", encoding="utf-8")
    before = list(sys.path)
    assert assembly._load_suite_modules(tmp_path) is None
    assert sys.path == before
