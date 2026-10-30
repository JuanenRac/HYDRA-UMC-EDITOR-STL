# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the safety rules of the part operations
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
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


def test_a_robot_with_known_home_placements_is_pushed_assembled_not_stacked(tmp_path: Path, monkeypatch) -> None:
    from hydra_umc_editor_stl import catalog_push
    from hydra_umc_editor_stl.assembly import PartPlacement

    root, model_dir = _library(tmp_path)
    model = load_model(root, "studio", "robots-6-dof", "arm")
    # 10 mm cube: a placement of 250 mm along x, turned a quarter of a turn about z
    quarter_z = (0.7071067811865476, 0.0, 0.0, 0.7071067811865476)
    monkeypatch.setattr(catalog_push, "assembled_transforms", lambda *a, **k: {"base.stl": PartPlacement((0.25, 0.0, 0.5), quarter_z)})
    placements = catalog_push.home_placements(model, root)
    urdf = build_assembly_urdf(model, placements)
    origin = ET.fromstring(urdf).find("joint/origin")
    assert origin is not None
    xyz = [float(v) for v in origin.get("xyz").split()]
    rpy = [float(v) for v in origin.get("rpy").split()]
    # the cube spans 10 units (not more than 5 mm-units rule: 10 > 5 so it is millimeters): 0.25 mm -> 0.00025 m
    assert xyz == pytest.approx([0.00025, 0.0, 0.0005])
    assert rpy == pytest.approx([0.0, 0.0, 1.5707963], abs=1e-6)
    # no refusal any more: the push gets as far as the (unreachable) server
    client = ServerClient("127.0.0.1", 1)
    client.token = "x"
    with pytest.raises(CatalogPushError) as info:
        client.push_model(model, "robots-6-dof", ecosystem_root=root)
    assert "stacked" not in str(info.value)
    assert client.last_placed_parts == 1
    assert not any("link frame" in w for w in catalog_push.push_warnings(model, "robots-6-dof", root))


def test_parts_without_a_known_placement_are_reported_and_a_model_with_none_is_still_refused(tmp_path: Path, monkeypatch) -> None:
    from hydra_umc_editor_stl import catalog_push
    from hydra_umc_editor_stl.assembly import PartPlacement

    root, model_dir = _library(tmp_path)
    make_cube_stl(model_dir / "arm2.stl", size=10.0)
    model = load_model(root, "studio", "robots-6-dof", "arm")
    monkeypatch.setattr(catalog_push, "assembled_transforms", lambda *a, **k: {"base.stl": PartPlacement((0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0))})
    warnings = catalog_push.push_warnings(model, "robots-6-dof", root)
    assert any("1 part(s)" in w and "arm2.stl" in w for w in warnings)
    monkeypatch.setattr(catalog_push, "assembled_transforms", lambda *a, **k: None)
    client = ServerClient("127.0.0.1", 1)
    client.token = "x"
    with pytest.raises(CatalogPushError, match="stacked"):
        client.push_model(model, "robots-6-dof", ecosystem_root=root)


def test_a_failing_kinematics_module_counts_as_no_placement(tmp_path: Path, monkeypatch) -> None:
    from hydra_umc_editor_stl import catalog_push

    root, _ = _library(tmp_path)
    model = load_model(root, "studio", "robots-6-dof", "arm")

    def boom(*a, **k):
        raise RuntimeError("kinematics broke")

    monkeypatch.setattr(catalog_push, "assembled_transforms", boom)
    assert catalog_push.home_placements(model, root) is None
    assert catalog_push.home_placements(model, None) is None


def test_the_real_suite_places_a_ur5e_with_distinct_origins_in_the_pushed_urdf() -> None:
    from hydra_umc_editor_stl import catalog_push

    real_root = Path(__file__).resolve().parents[2]
    if not (real_root / "HYDRA-UMC-SUITE" / "hydra_suite" / "render" / "kinematics.py").is_file() \
            or not (real_root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ur5e").is_dir():
        pytest.skip("needs the sibling HYDRA-UMC-SUITE/HYDRA-UMC-STUDIO checkouts")
    model = load_model(real_root, "studio", "robots-6-dof", "ur5e")
    placements = catalog_push.home_placements(model, real_root)
    assert placements
    root = ET.fromstring(build_assembly_urdf(model, placements))
    origins = {o.get("xyz") for o in root.findall("joint/origin")}
    assert len(origins) > 1
