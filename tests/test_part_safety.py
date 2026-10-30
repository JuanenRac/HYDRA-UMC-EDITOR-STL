# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the safety rules of the part operations
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path

import pytest

from hydra_umc_editor_stl.catalog_push import (
    MAX_BODY_BYTES,
    CatalogPushError,
    ServerClient,
    build_assembly_urdf,
    push_warnings,
)
from hydra_umc_editor_stl.model_catalog import load_model
from hydra_umc_editor_stl.part_colors import load_part_colors, save_part_color
from hydra_umc_editor_stl.stl_ops import StlOpsError, add_part, remove_part, transform_part, unique_part_filename

from .conftest import make_cube_stl


def _library(tmp_path: Path, category: str = "robots-6-dof") -> tuple[Path, Path]:
    model_dir = tmp_path / "HYDRA-UMC-STUDIO" / "public" / "models" / category / "arm"
    model_dir.mkdir(parents=True)
    make_cube_stl(model_dir / "base.stl", size=10.0)
    return tmp_path, model_dir


def test_backup_copies_in_the_trash_are_not_parts(tmp_path: Path) -> None:
    root, model_dir = _library(tmp_path)
    transform_part(model_dir, "base.stl", translate_mm=(1.0, 0.0, 0.0))
    assert list((model_dir / ".trash").iterdir())  # the backup exists
    model = load_model(root, "studio", "robots-6-dof", "arm")
    assert [p.filename for p in model.parts] == ["base.stl"]
    assert "meshes/0_base.stl" in build_assembly_urdf(model)
    assert ".trash" not in build_assembly_urdf(model)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_transform_values_are_refused_and_the_part_is_untouched(tmp_path: Path, bad: float) -> None:
    _, model_dir = _library(tmp_path)
    before = (model_dir / "base.stl").read_bytes()
    for kwargs in ({"scale": bad}, {"translate_mm": (bad, 0.0, 0.0)}, {"rotate_deg": (0.0, bad, 0.0)}):
        with pytest.raises(StlOpsError):
            transform_part(model_dir, "base.stl", **kwargs)
    assert (model_dir / "base.stl").read_bytes() == before


def test_part_names_cannot_leave_the_model_folder(tmp_path: Path) -> None:
    _, model_dir = _library(tmp_path)
    outside = tmp_path / "outside.stl"
    make_cube_stl(outside, size=3.0)
    for name in ("../../outside.stl", str(outside)):
        with pytest.raises(StlOpsError):
            transform_part(model_dir, name)
        with pytest.raises(StlOpsError):
            remove_part(model_dir, name)
        with pytest.raises(StlOpsError):
            add_part(model_dir, outside, name)
    assert outside.exists()
    with pytest.raises(StlOpsError):
        add_part(model_dir, outside, "notes.txt")


def test_a_category_that_climbs_out_of_the_library_is_not_a_model(tmp_path: Path) -> None:
    root, _ = _library(tmp_path)
    assert load_model(root, "studio", "..", "..") is None


def test_a_corrupt_stl_is_reported_not_raised_as_a_numpy_error(tmp_path: Path) -> None:
    _, model_dir = _library(tmp_path)
    (model_dir / "broken.stl").write_bytes(b"\x00" * 84 + b"\x05\x00\x00\x00" + b"\x00" * 10)
    with pytest.raises(StlOpsError):
        transform_part(model_dir, "broken.stl")


def test_copy_name_keeps_the_subfolder(tmp_path: Path) -> None:
    _, model_dir = _library(tmp_path)
    (model_dir / "parts").mkdir()
    make_cube_stl(model_dir / "parts" / "foo.stl", size=2.0)
    assert unique_part_filename(model_dir, "parts/foo.stl") == "parts/foo_copy.stl"
    make_cube_stl(model_dir / "parts" / "foo_copy.stl", size=2.0)
    assert unique_part_filename(model_dir, "parts/foo.stl") == "parts/foo_copy2.stl"


def test_saving_a_color_leaves_no_temporary_file(tmp_path: Path) -> None:
    _, model_dir = _library(tmp_path)
    save_part_color(model_dir, "base.stl", "#112233")
    assert load_part_colors(model_dir) == {"base.stl": "#112233"}
    assert not list(model_dir.glob("*.tmp"))


def test_push_warns_about_skipped_parts_and_frame_local_categories(tmp_path: Path) -> None:
    root, model_dir = _library(tmp_path)
    (model_dir / "extra.glb").write_bytes(b"glTF")
    model = load_model(root, "studio", "robots-6-dof", "arm")
    warnings = push_warnings(model, "robots-6-dof")
    assert any("not .stl" in w for w in warnings)
    assert any("link frame" in w for w in warnings)
    assert not any("link frame" in w for w in push_warnings(model, "heatedbeds"))


def test_a_push_above_the_server_limit_is_refused_before_sending(tmp_path: Path, monkeypatch) -> None:
    root, model_dir = _library(tmp_path)
    model = load_model(root, "studio", "robots-6-dof", "arm")
    monkeypatch.setattr("hydra_umc_editor_stl.catalog_push.MAX_BODY_BYTES", 100)
    client = ServerClient("127.0.0.1", 1)
    client.token = "x"
    with pytest.raises(CatalogPushError, match="50 MB"):
        client.push_model(model, "robots-6-dof", allow_stacked=True)
    assert MAX_BODY_BYTES > 100 and json.dumps({})


def test_a_server_url_with_https_is_kept() -> None:
    assert ServerClient("https://srv", 3000).base_url == "https://srv:3000"
    assert ServerClient("https://srv:8443", 3000).base_url == "https://srv:8443"
    assert ServerClient("10.0.0.5", 3000).base_url == "http://10.0.0.5:3000"


def test_a_robot_push_is_blocked_unless_stacking_is_allowed(tmp_path: Path) -> None:
    root, _ = _library(tmp_path)
    model = load_model(root, "studio", "robots-6-dof", "arm")
    client = ServerClient("127.0.0.1", 1)
    client.token = "x"
    with pytest.raises(CatalogPushError, match="stacked"):
        client.push_model(model, "robots-6-dof")
    # Independent pieces are never blocked: this one only fails later, on the unreachable server.
    heated = load_model(root, "studio", "robots-6-dof", "arm")
    with pytest.raises(CatalogPushError) as info:
        client.push_model(heated, "heatedbeds")
    assert "stacked" not in str(info.value)
    with pytest.raises(CatalogPushError) as info:
        client.push_model(model, "robots-6-dof", allow_stacked=True)
    assert "stacked" not in str(info.value)
