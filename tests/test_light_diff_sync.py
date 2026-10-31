# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for light copies, the before/after comparison and the library sync
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import math
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl import main as main_module
from hydra_umc_editor_stl.decimate import LITE_DIRNAME, decimate_to_ratio, make_light_copy
from hydra_umc_editor_stl.library_sync import BACKUP_DIRNAME, LibrarySyncError, compare_libraries, sync_libraries
from hydra_umc_editor_stl.mesh_diff import diff_vectors, diff_with_trash, latest_trash_entry, render_diff_svg, render_diff_with_trash
from hydra_umc_editor_stl.model_catalog import load_model
from hydra_umc_editor_stl.stl_ops import StlOpsError, transform_part

from .conftest import make_cube_stl


def sphere_vectors(rings: int = 40, segments: int = 60, radius: float = 10.0) -> np.ndarray:
    points = []
    for i in range(rings + 1):
        theta = math.pi * i / rings
        points.append([[radius * math.sin(theta) * math.cos(2 * math.pi * j / segments),
                        radius * math.sin(theta) * math.sin(2 * math.pi * j / segments),
                        radius * math.cos(theta)] for j in range(segments)])
    tris = []
    for i in range(rings):
        for j in range(segments):
            a, b = points[i][j], points[i][(j + 1) % segments]
            c, d = points[i + 1][j], points[i + 1][(j + 1) % segments]
            tris.append([a, c, b])
            tris.append([b, c, d])
    return np.array(tris, dtype=np.float32)


def write_stl(path: Path, vectors: np.ndarray) -> None:
    mesh = stl_mesh.Mesh(np.zeros(len(vectors), dtype=stl_mesh.Mesh.dtype))
    mesh.vectors[:] = vectors
    mesh.update_normals()
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.save(str(path))


# --- decimation ---------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("ratio", [0.1, 0.25, 0.5])
def test_decimation_gets_near_the_ratio_and_keeps_the_size(ratio: float) -> None:
    full = sphere_vectors()
    light = decimate_to_ratio(full, ratio)
    assert 0 < len(light) <= math.ceil(len(full) * ratio)
    assert len(light) >= len(full) * ratio * 0.3  # it does not collapse far below the wish
    span_full = full.reshape(-1, 3).max(axis=0) - full.reshape(-1, 3).min(axis=0)
    span_light = light.reshape(-1, 3).max(axis=0) - light.reshape(-1, 3).min(axis=0)
    assert np.all(span_light > 0.6 * span_full) and np.all(span_light <= span_full + 1e-6)
    assert np.isfinite(light).all()
    # no triangle collapsed to a line or point
    area2 = np.linalg.norm(np.cross(light[:, 1] - light[:, 0], light[:, 2] - light[:, 0]), axis=1)
    assert (area2 > 0).all()


def test_ratio_one_keeps_everything_and_bad_ratios_are_refused() -> None:
    full = sphere_vectors(8, 12)
    assert len(decimate_to_ratio(full, 1.0)) == len(full)
    assert len(decimate_to_ratio(full, 2.0)) == len(full)
    for bad in (0, -0.5, float("nan"), float("inf"), "0.5", None):
        with pytest.raises(ValueError):
            decimate_to_ratio(full, bad)  # type: ignore[arg-type]


def test_non_finite_triangles_are_dropped_and_tiny_meshes_are_kept() -> None:
    full = sphere_vectors(8, 12)
    broken = np.concatenate([full, np.full((1, 3, 3), np.nan, dtype=np.float32)])
    assert np.isfinite(decimate_to_ratio(broken, 0.5)).all()
    cube = np.array(sphere_vectors(1, 3), dtype=np.float32)[:2]
    assert len(decimate_to_ratio(cube, 0.1)) == 2


def test_the_light_copy_goes_to_lite_and_the_original_is_untouched(tmp_path: Path) -> None:
    model = tmp_path / "m"
    write_stl(model / "ball.stl", sphere_vectors())
    before = (model / "ball.stl").read_bytes()
    done = make_light_copy(model, "ball.stl", 0.2)
    assert (model / "ball.stl").read_bytes() == before
    assert done["path"] == model / LITE_DIRNAME / "ball.stl" and done["path"].is_file()
    assert done["triangles_after"] < done["triangles_before"] * 0.3 and done["bytes_after"] < done["bytes_before"]
    again = stl_mesh.Mesh.from_file(str(done["path"]))
    assert len(again.vectors) == done["triangles_after"]


def test_the_light_copy_is_not_listed_as_a_part_and_names_cannot_escape(tmp_path: Path) -> None:
    root = tmp_path / "eco"
    model = root / "HYDRA-UMC-STUDIO" / "public" / "models" / "cat" / "m"
    write_stl(model / "ball.stl", sphere_vectors(10, 12))
    make_light_copy(model, "ball.stl", 0.5)
    parts = load_model(root, "studio", "cat", "m").parts
    assert [p.filename for p in parts] == ["ball.stl"]
    with pytest.raises(StlOpsError):
        make_light_copy(model, "../ball.stl", 0.5)
    with pytest.raises(StlOpsError):
        make_light_copy(model, "missing.stl", 0.5)
    with pytest.raises(StlOpsError):
        make_light_copy(model, "ball.stl", 0)


# --- before / after ---------------------------------------------------------------------------------------------------------


def test_diff_after_a_transform_reports_the_shift_and_scale(tmp_path: Path) -> None:
    model = tmp_path / "m"
    make_cube_stl(model / "c.stl", 10.0)
    assert latest_trash_entry(model, "c.stl") is None
    with pytest.raises(StlOpsError, match="no earlier version"):
        diff_with_trash(model, "c.stl")
    transform_part(model, "c.stl", translate_mm=(5.0, 0.0, 0.0), scale=2.0)
    result = diff_with_trash(model, "c.stl")
    assert result.triangles_before == result.triangles_after == 12
    assert result.size_before == pytest.approx((10, 10, 10)) and result.size_after == pytest.approx((20, 20, 20))
    assert result.center_shift[0] == pytest.approx(10.0)  # centre 5 -> 2 * 5 + 5 = 15 ... shift in x is 10
    assert abs(result.volume_after) == pytest.approx(8 * abs(result.volume_before))
    assert not result.unchanged


def test_diff_of_identical_versions_is_unchanged_and_bad_entries_are_refused(tmp_path: Path) -> None:
    model = tmp_path / "m"
    make_cube_stl(model / "c.stl", 10.0)
    transform_part(model, "c.stl", translate_mm=(1.0, 0.0, 0.0))
    transform_part(model, "c.stl", translate_mm=(-1.0, 0.0, 0.0))
    first, second = [e["entry"] for e in __import__("hydra_umc_editor_stl.stl_ops", fromlist=["list_trash"]).list_trash(model)]
    current = (model / "c.stl").read_bytes()
    assert diff_with_trash(model, "c.stl", entry=second).unchanged or diff_with_trash(model, "c.stl", entry=first).unchanged
    for bad in ("../c.stl", "nope.stl", ".."):
        with pytest.raises(StlOpsError):
            diff_with_trash(model, "c.stl", entry=bad)
    assert (model / "c.stl").read_bytes() == current  # nothing is written by a comparison


def test_the_picture_is_valid_svg_with_both_versions_and_bounded_in_size(tmp_path: Path) -> None:
    big = sphere_vectors(80, 100)
    svg = render_diff_svg(big, big * 1.5)
    root = ET.fromstring(svg)
    polygons = root.findall(".//{http://www.w3.org/2000/svg}polygon")
    assert 0 < len(polygons) <= 3 * 2 * 3000
    assert "#e0a030" in svg and "#30c0e0" in svg
    empty = ET.fromstring(render_diff_svg(np.zeros((0, 3, 3)), np.zeros((0, 3, 3))))
    assert empty.tag.endswith("svg")
    model = tmp_path / "m"
    make_cube_stl(model / "c.stl", 10.0)
    transform_part(model, "c.stl", rotate_deg=(0.0, 0.0, 45.0))
    assert "<polygon" in render_diff_with_trash(model, "c.stl")


def test_diff_vectors_handles_empty_input() -> None:
    result = diff_vectors(np.zeros((0, 3, 3)), np.zeros((0, 3, 3)))
    assert result.triangles_before == 0 and result.volume_before == 0.0 and result.unchanged


# --- one library -----------------------------------------------------------------------------------------------------------


def _two_libraries(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "eco"
    studio = root / "HYDRA-UMC-STUDIO" / "public" / "models"
    suite = root / "HYDRA-UMC-SUITE" / "assets" / "meshes"
    make_cube_stl(studio / "robots" / "a" / "base.stl", 10.0)
    (suite / "robots" / "a").mkdir(parents=True)
    shutil.copy2(studio / "robots" / "a" / "base.stl", suite / "robots" / "a" / "base.stl")  # the header of an STL carries a time stamp
    make_cube_stl(studio / "robots" / "a" / "only_studio.stl", 5.0)
    make_cube_stl(suite / "robots" / "a" / "only_suite.stl", 6.0)
    make_cube_stl(studio / "robots" / "a" / "changed.stl", 7.0)
    make_cube_stl(suite / "robots" / "a" / "changed.stl", 8.0)
    return root, studio, suite


def test_compare_reports_each_kind_of_difference_and_ignores_hidden_folders(tmp_path: Path) -> None:
    root, studio, suite = _two_libraries(tmp_path)
    make_cube_stl(studio / "robots" / "a" / ".trash" / "old.stl", 3.0)
    diff = compare_libraries(root)
    assert diff.same == 1
    assert diff.only_in_master == ["robots/a/only_studio.stl"]
    assert diff.only_in_target == ["robots/a/only_suite.stl"]
    assert diff.different == ["robots/a/changed.stl"]
    assert not diff.in_sync


def test_sync_is_a_plan_unless_applied_and_never_deletes(tmp_path: Path) -> None:
    root, studio, suite = _two_libraries(tmp_path)
    plan = sync_libraries(root)
    assert plan["applied"] is False and plan["copied"] == ["robots/a/only_studio.stl"] and plan["replaced"] == ["robots/a/changed.stl"]
    assert not (suite / "robots" / "a" / "only_studio.stl").exists()  # nothing written
    old = (suite / "robots" / "a" / "changed.stl").read_bytes()
    done = sync_libraries(root, apply=True)
    assert done["applied"] is True
    assert compare_libraries(root).in_sync
    assert (suite / "robots" / "a" / "only_suite.stl").is_file()  # a file only in the target is left alone
    backups = list((suite / BACKUP_DIRNAME).rglob("changed.stl"))
    assert len(backups) == 1 and backups[0].read_bytes() == old  # what was replaced is kept
    assert not list(suite.rglob("*.tmp"))


def test_sync_refuses_bad_choices(tmp_path: Path) -> None:
    root, _, _ = _two_libraries(tmp_path)
    for master, target in (("studio", "studio"), ("studio", "other"), ("x", "suite")):
        with pytest.raises(LibrarySyncError):
            sync_libraries(root, master, target)
    with pytest.raises(LibrarySyncError, match="not found"):
        sync_libraries(tmp_path / "empty", "studio", "suite")


# --- the command line ----------------------------------------------------------------------------------------------------


def _cli(monkeypatch, capsys, *args: str) -> tuple[int, str, str]:
    monkeypatch.setattr(sys, "argv", ["hydra-umc-editor-stl", "--cli", *args])
    code = main_module.main()
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_cli_lite_diff_and_sync(monkeypatch, capsys, tmp_path: Path) -> None:
    root, studio, suite = _two_libraries(tmp_path)
    monkeypatch.setattr(main_module.settings, "SETTINGS_PATH", tmp_path / "settings.json")
    write_stl(studio / "robots" / "a" / "ball.stl", sphere_vectors())
    sel = ["--root", str(root), "studio", "robots", "a"]
    code, out, _ = _cli(monkeypatch, capsys, "lite", *sel, "--part", "ball.stl", "--ratio", "0.2")
    assert code == 0 and "ball.stl:" in out and (studio / "robots" / "a" / LITE_DIRNAME / "ball.stl").is_file()
    code, _, err = _cli(monkeypatch, capsys, "lite", *sel, "--part", "ball.stl", "--ratio", "0")
    assert code == 1 and "Light copy failed" in err
    main_module.settings.save_settings(lite_ratio=0.5)
    assert main_module._saved_ratio() == 0.5
    main_module.settings.save_settings(lite_ratio=7)
    assert main_module._saved_ratio() == 0.2

    code, _, err = _cli(monkeypatch, capsys, "diff", *sel, "ball.stl")
    assert code == 1 and "no earlier version" in err
    transform_part(studio / "robots" / "a", "ball.stl", scale=2.0)
    svg = tmp_path / "d.svg"
    code, out, _ = _cli(monkeypatch, capsys, "diff", *sel, "ball.stl", "--svg", str(svg))
    assert code == 0 and "triangles:" in out and ET.fromstring(svg.read_text(encoding="utf-8")).tag.endswith("svg")

    code, out, _ = _cli(monkeypatch, capsys, "sync-libraries", "--root", str(root))
    assert code == 0 and "Nothing was written" in out and not (suite / "robots" / "a" / "only_studio.stl").exists()
    code, out, _ = _cli(monkeypatch, capsys, "sync-libraries", "--root", str(root), "--apply")
    assert code == 0 and (suite / "robots" / "a" / "only_studio.stl").is_file()
    code, _, err = _cli(monkeypatch, capsys, "sync-libraries", "--root", str(root), "--master", "suite", "--target", "suite")
    assert code == 1 and "Library sync failed" in err
