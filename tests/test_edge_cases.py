# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for hostile files, hostile server answers and
# the pure helpers that had no direct test
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import json
import math
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl import settings
from hydra_umc_editor_stl.assembly import (
    PartPlacement,
    _mesh_is_millimeters,
    _quaternion_wxyz,
    _rotation_matrix,
    assembled_bounds,
    assembled_transforms,
    placement_matrix,
)
from hydra_umc_editor_stl.catalog_push import CatalogPushError, ServerClient
from hydra_umc_editor_stl.model_catalog import (
    ModelInfo,
    PartInfo,
    is_independent_parts_category,
    list_categories,
    list_models,
    load_model,
    resolve_library_root,
)
from hydra_umc_editor_stl.part_colors import load_part_colors, save_part_color
from hydra_umc_editor_stl.stl_ops import (
    StlOpsError,
    add_part,
    is_real_stl,
    model_bounds,
    remove_part,
    replace_part,
    transform_part,
    unique_part_filename,
)

from .conftest import make_cube_stl

BAD_UTF8 = b"\xff\xfe\x00\xc3\x28 not utf-8"


# --------------------------------------------------------------- saved files


@pytest.fixture
def settings_file(tmp_path: Path, monkeypatch) -> Path:
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)
    return path


def test_settings_that_are_not_utf8_load_as_empty(settings_file: Path) -> None:
    settings_file.write_bytes(BAD_UTF8)
    assert settings.load_settings() == {}
    assert settings.get_saved_lang() is None
    assert settings.get_saved_ecosystem_root() is None


@pytest.mark.parametrize("content", ["", "[]", "null", "5", '"text"', "{", "{'a': 1}"])
def test_settings_with_a_wrong_shape_load_as_empty(settings_file: Path, content: str) -> None:
    settings_file.write_text(content, encoding="utf-8")
    assert settings.load_settings() == {}


def test_saving_over_an_unreadable_settings_file_starts_again(settings_file: Path) -> None:
    settings_file.write_bytes(BAD_UTF8)
    settings.save_lang("es")
    assert settings.get_saved_lang() == "es"


def test_settings_round_trip_and_merge(settings_file: Path, tmp_path: Path) -> None:
    settings.save_lang("de")
    settings.save_ecosystem_root(tmp_path)
    assert settings.get_saved_lang() == "de"
    assert settings.get_saved_ecosystem_root() == tmp_path
    settings.save_lang("fr")
    assert settings.get_saved_ecosystem_root() == tmp_path


def test_a_saved_root_that_no_longer_exists_is_not_returned(settings_file: Path, tmp_path: Path) -> None:
    settings.save_ecosystem_root(tmp_path / "gone")
    assert settings.get_saved_ecosystem_root() is None


@pytest.mark.parametrize("value", [5, None, "", ["x"], {"a": 1}])
def test_saved_values_of_the_wrong_type_are_ignored(settings_file: Path, value) -> None:
    settings_file.write_text(json.dumps({"lang": value, "ecosystem_root": value}), encoding="utf-8")
    assert settings.get_saved_lang() is None
    assert settings.get_saved_ecosystem_root() is None


def test_saving_into_a_missing_folder_never_raises(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "no" / "such" / "folder" / "s.json")
    settings.save_lang("it")  # best effort: must not raise
    assert settings.get_saved_lang() is None


def test_part_colors_that_are_not_utf8_load_as_empty(tmp_path: Path) -> None:
    (tmp_path / "part_colors.json").write_bytes(BAD_UTF8)
    assert load_part_colors(tmp_path) == {}
    save_part_color(tmp_path, "a.stl", "#112233")
    assert load_part_colors(tmp_path) == {"a.stl": "#112233"}


def test_part_colors_ignore_entries_that_are_not_text(tmp_path: Path) -> None:
    (tmp_path / "part_colors.json").write_text(json.dumps({"a.stl": "#fff", "b.stl": 5, "c.stl": None}), encoding="utf-8")
    assert load_part_colors(tmp_path) == {"a.stl": "#fff"}


def test_model_metadata_that_is_not_utf8_is_ignored(ecosystem_root: Path) -> None:
    model_dir = ecosystem_root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ar3"
    (model_dir / "metadata.json").write_bytes(BAD_UTF8)
    model = load_model(ecosystem_root, "studio", "robots-6-dof", "ar3")
    assert model is not None
    assert model.metadata is None
    assert {part.filename for part in model.parts} == {"base_link.STL", "link_1.STL"}


# ------------------------------------------------------------------- catalog


def test_load_model_refuses_a_model_that_leads_outside_the_library(ecosystem_root: Path) -> None:
    secret = ecosystem_root / "HYDRA-UMC-STUDIO" / "public" / "secret"
    make_cube_stl(secret / "leak.stl")
    assert load_model(ecosystem_root, "studio", "..", "secret") is None
    assert load_model(ecosystem_root, "studio", "robots-6-dof/../..", "secret") is None
    assert load_model(ecosystem_root, "studio", "..", "..") is None


def test_unknown_library_has_no_root_categories_or_models(ecosystem_root: Path) -> None:
    assert resolve_library_root(ecosystem_root, "nope") is None
    assert list_categories(ecosystem_root, "nope") == []
    assert list_models(ecosystem_root, "nope", "x") == []
    assert load_model(ecosystem_root, "nope", "x", "y") is None


def test_hidden_folders_and_other_extensions_are_not_parts(ecosystem_root: Path) -> None:
    model_dir = ecosystem_root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ar3"
    make_cube_stl(model_dir / ".hidden" / "x.stl")
    make_cube_stl(model_dir / "parts" / "deep" / "y.STL")
    (model_dir / "readme.txt").write_text("x", encoding="utf-8")
    (model_dir / "model.glb").write_bytes(b"glTF")
    model = load_model(ecosystem_root, "studio", "robots-6-dof", "ar3")
    names = {part.filename: part.editable for part in model.parts}
    assert names["parts/deep/y.STL"] is True
    assert names["model.glb"] is False
    assert ".hidden/x.stl" not in names
    assert "readme.txt" not in names


def test_independent_parts_categories() -> None:
    assert is_independent_parts_category("heatedbeds")
    assert not is_independent_parts_category("robots-6-dof")


# --------------------------------------------------------------- part files


def test_part_names_that_lead_outside_the_model_are_refused(tmp_path: Path) -> None:
    model_dir = tmp_path / "model"
    make_cube_stl(model_dir / "a.stl")
    make_cube_stl(tmp_path / "outside.stl")
    source = tmp_path / "outside.stl"
    for name in ("../outside.stl", "sub/../../outside.stl", str(source.resolve())):
        with pytest.raises(StlOpsError):
            transform_part(model_dir, name, scale=2.0)
        with pytest.raises(StlOpsError):
            remove_part(model_dir, name)
        with pytest.raises(StlOpsError):
            replace_part(model_dir, name, source)
        with pytest.raises(StlOpsError):
            add_part(model_dir, source, name)
    assert is_real_stl(source)  # nothing outside was touched


def test_a_link_inside_the_model_pointing_outside_is_refused(tmp_path: Path) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    outside = tmp_path / "outside.stl"
    make_cube_stl(outside)
    link = model_dir / "link.stl"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("links cannot be created here")
    before = outside.read_bytes()
    with pytest.raises(StlOpsError):
        transform_part(model_dir, "link.stl", scale=3.0)
    assert outside.read_bytes() == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"scale": 0.0},
        {"scale": -1.0},
        {"scale": math.nan},
        {"scale": math.inf},
        {"translate_mm": (math.nan, 0.0, 0.0)},
        {"rotate_deg": (0.0, math.inf, 0.0)},
        {"scale": 1e300},
    ],
)
def test_transform_refuses_values_that_would_damage_the_part(tmp_path: Path, kwargs) -> None:
    make_cube_stl(tmp_path / "a.stl")
    before = (tmp_path / "a.stl").read_bytes()
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "a.stl", **kwargs)
    assert (tmp_path / "a.stl").read_bytes() == before
    assert not (tmp_path / ".trash").exists() or not list((tmp_path / ".trash").iterdir())


def test_transform_moves_scales_and_rotates_for_real(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    box = transform_part(tmp_path, "a.stl", translate_mm=(100.0, 0.0, 0.0), scale=2.0)
    assert box.min_xyz == pytest.approx((100.0, 0.0, 0.0), abs=1e-4)
    assert box.max_xyz == pytest.approx((120.0, 20.0, 20.0), abs=1e-4)
    rotated = transform_part(tmp_path, "a.stl", rotate_deg=(0.0, 0.0, 90.0))
    assert rotated.min_xyz[0] == pytest.approx(-20.0, abs=1e-3)
    assert rotated.max_xyz[0] == pytest.approx(0.0, abs=1e-3)


@pytest.mark.parametrize(
    "content",
    [b"", b"solid x\nendsolid x\n", b"\x00" * 10, b"not an stl at all" * 20, b"\x00" * 84],
)
def test_files_that_are_not_usable_stl_are_never_accepted(tmp_path: Path, content: bytes) -> None:
    junk = tmp_path / "junk.stl"
    junk.write_bytes(content)
    make_cube_stl(tmp_path / "model" / "a.stl")
    assert not is_real_stl(junk)
    with pytest.raises(StlOpsError):
        add_part(tmp_path / "model", junk)
    with pytest.raises(StlOpsError):
        replace_part(tmp_path / "model", "a.stl", junk)
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "junk.stl", scale=2.0)
    assert is_real_stl(tmp_path / "model" / "a.stl")


def test_a_truncated_binary_stl_is_not_transformed(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl")
    data = (tmp_path / "a.stl").read_bytes()
    (tmp_path / "cut.stl").write_bytes(data[: len(data) // 2])
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "cut.stl", scale=2.0)


def test_add_part_refuses_other_extensions_and_existing_names(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "src.stl")
    model_dir = tmp_path / "model"
    make_cube_stl(model_dir / "a.stl")
    with pytest.raises(StlOpsError, match=r"\.stl"):
        add_part(model_dir, tmp_path / "src.stl", "evil.exe")
    with pytest.raises(StlOpsError, match="already exists"):
        add_part(model_dir, tmp_path / "src.stl", "a.stl")
    assert add_part(model_dir, tmp_path / "src.stl", "sub/new.STL") == "sub/new.STL"
    assert (model_dir / "sub" / "new.STL").is_file()


def test_replace_and_remove_keep_a_backup_in_the_trash(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    make_cube_stl(tmp_path / "bigger.stl", size=50.0)
    original = (tmp_path / "a.stl").read_bytes()
    replace_part(tmp_path, "a.stl", tmp_path / "bigger.stl")
    assert (tmp_path / "a.stl").read_bytes() == (tmp_path / "bigger.stl").read_bytes()
    backups = list((tmp_path / ".trash").iterdir())
    assert [b.read_bytes() for b in backups] == [original]
    moved = remove_part(tmp_path, "a.stl")
    assert not (tmp_path / "a.stl").exists()
    assert moved.is_file()


def test_missing_parts_are_reported(tmp_path: Path) -> None:
    for call in (
        lambda: transform_part(tmp_path, "nope.stl", scale=2.0),
        lambda: remove_part(tmp_path, "nope.stl"),
    ):
        with pytest.raises(StlOpsError, match="no such part"):
            call()
    with pytest.raises(StlOpsError):
        replace_part(tmp_path, "nope.stl", tmp_path / "missing_source.stl")
    with pytest.raises(StlOpsError):
        add_part(tmp_path, tmp_path / "missing_source.stl")


def test_unique_part_filename_counts_up_and_keeps_the_folder(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "parts" / "foo.stl")
    assert unique_part_filename(tmp_path, "parts/bar.stl") == "parts/bar.stl"
    assert unique_part_filename(tmp_path, "parts/foo.stl") == "parts/foo_copy.stl"
    make_cube_stl(tmp_path / "parts" / "foo_copy.stl")
    assert unique_part_filename(tmp_path, "parts/foo.stl") == "parts/foo_copy2.stl"


def test_model_bounds_skips_unreadable_parts(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    make_cube_stl(tmp_path / "b.stl", size=4.0)
    (tmp_path / "junk.stl").write_bytes(b"junk")
    box = model_bounds(tmp_path, ["a.stl", "junk.stl", "b.stl", "missing.stl"])
    assert box is not None
    assert box.max_xyz == (10.0, 10.0, 10.0)
    assert model_bounds(tmp_path, ["junk.stl", "missing.stl"]) is None
    assert model_bounds(tmp_path, []) is None


# ----------------------------------------------------------------- assembly


def _matrix_from_axis_angle(axis: tuple[float, float, float], degrees: float) -> np.ndarray:
    x, y, z = np.array(axis) / np.linalg.norm(axis)
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    t = 1 - c
    return np.array([
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ])


@pytest.mark.parametrize(
    "axis,degrees",
    [
        ((1, 0, 0), 0),
        ((1, 0, 0), 90),
        ((0, 1, 0), 90),
        ((0, 0, 1), 90),
        ((1, 0, 0), 180),
        ((0, 1, 0), 180),
        ((0, 0, 1), 180),
        ((1, 1, 1), 120),
        ((1, 2, 3), 77),
        ((1, 2, -3), 200),
        ((-1, 2, 3), 301),
    ],
)
def test_quaternion_round_trips_through_the_rotation_matrix(axis, degrees) -> None:
    matrix = _matrix_from_axis_angle(axis, degrees)
    quaternion = _quaternion_wxyz(matrix)
    assert sum(v * v for v in quaternion) == pytest.approx(1.0, abs=1e-9)
    assert np.allclose(_rotation_matrix(quaternion), matrix, atol=1e-9)


def test_placement_matrix_is_rotation_then_translation() -> None:
    placement = PartPlacement(position=(1.0, 2.0, 3.0), rotation_wxyz=(1.0, 0.0, 0.0, 0.0))
    assert placement_matrix(placement) == [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 2, 3]


def test_meshes_over_five_units_are_millimeters(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "big.stl", size=100.0)
    make_cube_stl(tmp_path / "small.stl", size=0.5)
    (tmp_path / "junk.stl").write_bytes(b"junk")
    assert _mesh_is_millimeters(tmp_path / "big.stl")
    assert not _mesh_is_millimeters(tmp_path / "small.stl")
    assert not _mesh_is_millimeters(tmp_path / "junk.stl")
    assert not _mesh_is_millimeters(tmp_path / "missing.stl")


def test_assembled_bounds_follow_each_placement(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    make_cube_stl(tmp_path / "b.stl", size=10.0)
    (tmp_path / "junk.stl").write_bytes(b"junk")
    identity = (1.0, 0.0, 0.0, 0.0)
    placements = {
        "a.stl": PartPlacement((0.0, 0.0, 0.0), identity),
        "b.stl": PartPlacement((100.0, 0.0, 0.0), identity),
        "junk.stl": PartPlacement((9999.0, 0.0, 0.0), identity),
        "missing.stl": PartPlacement((9999.0, 0.0, 0.0), identity),
    }
    lows, highs = assembled_bounds(tmp_path, placements)
    assert lows == pytest.approx((0.0, 0.0, 0.0))
    assert highs == pytest.approx((110.0, 10.0, 10.0))
    assert assembled_bounds(tmp_path, {}) is None
    assert assembled_bounds(tmp_path, {"junk.stl": placements["junk.stl"]}) is None


def test_assembly_without_the_kinematics_checkout_gives_nothing(tmp_path: Path) -> None:
    assert assembled_transforms(tmp_path, "robots-6-dof", "ar3", tmp_path) is None


@pytest.fixture
def untouched_import_state():
    """The kinematics loader appends to sys.path and imports `hydra_suite`;
    put both back so a fake checkout cannot leak into other tests."""
    saved_path = list(sys.path)
    saved_modules = {name: m for name, m in sys.modules.items() if name.split(".")[0] == "hydra_suite"}
    for name in saved_modules:
        del sys.modules[name]
    yield
    sys.path[:] = saved_path
    for name in [n for n in sys.modules if n.split(".")[0] == "hydra_suite"]:
        del sys.modules[name]
    sys.modules.update(saved_modules)


def test_a_broken_kinematics_checkout_gives_nothing(tmp_path: Path, untouched_import_state) -> None:
    suite = tmp_path / "HYDRA-UMC-SUITE" / "hydra_suite" / "render"
    suite.mkdir(parents=True)
    (suite / "kinematics.py").write_text("raise RuntimeError('broken checkout')\n", encoding="utf-8")
    assert assembled_transforms(tmp_path, "robots-6-dof", "ar3", tmp_path) is None


# ------------------------------------------------------------ server answers


class _Handler(BaseHTTPRequestHandler):
    routes: dict[str, tuple[int, bytes]] = {}

    def log_message(self, format, *args) -> None:  # noqa: A002 - base class signature
        pass

    def _answer(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        status, body = self.routes.get(self.path, (404, b'{"error":"nope"}'))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _answer


@pytest.fixture
def fake_server():
    routes: dict[str, tuple[int, bytes]] = {}
    handler = type("Handler", (_Handler,), {"routes": routes})
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_address[1], routes
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


@pytest.mark.parametrize(
    "status,body",
    [
        (200, b"<html>captive portal</html>"),
        (200, b""),
        (200, b"[]"),
        (200, b"null"),
        (200, b'"token"'),
        (200, BAD_UTF8),
        (401, b"[]"),
        (500, b'"text"'),
        (500, b"null"),
        (502, b"<html>bad gateway</html>"),
        (500, BAD_UTF8),
    ],
)
def test_login_with_a_broken_answer_is_a_readable_error(fake_server, status: int, body: bytes) -> None:
    port, routes = fake_server
    routes["/api/login"] = (status, body)
    client = ServerClient("127.0.0.1", port)
    with pytest.raises(CatalogPushError):
        client.login("admin", "pw")
    assert client.token is None


@pytest.mark.parametrize("token", [None, "", 0, 5, ["a"], {"a": 1}, False])
def test_login_needs_a_text_token(fake_server, token) -> None:
    port, routes = fake_server
    routes["/api/login"] = (200, json.dumps({"token": token}).encode())
    client = ServerClient("127.0.0.1", port)
    with pytest.raises(CatalogPushError):
        client.login("admin", "pw")
    assert client.token is None


def test_error_message_of_the_server_is_passed_on(fake_server) -> None:
    port, routes = fake_server
    routes["/api/login"] = (401, b'{"error":"Invalid credentials"}')
    with pytest.raises(CatalogPushError, match="Invalid credentials"):
        ServerClient("127.0.0.1", port).login("admin", "bad")


def test_login_then_push_returns_the_slug(fake_server, tmp_path: Path) -> None:
    port, routes = fake_server
    routes["/api/login"] = (200, b'{"token":"abc"}')
    routes["/api/models/submit"] = (200, b'{"slug":"arm-1"}')
    make_cube_stl(tmp_path / "a.stl")
    model = ModelInfo("studio", "heatedbeds", "arm", tmp_path, (PartInfo("a.stl", 10, True),))
    client = ServerClient("127.0.0.1", port)
    client.login("admin", "pw")
    assert client.token == "abc"
    assert client.push_model(model, "heatedbeds") == "arm-1"


@pytest.mark.parametrize("answer", [b"{}", b"[]", b"null", b'{"slug":""}', b'{"slug":null}', b"<html>"])
def test_push_without_a_usable_slug_is_an_error(fake_server, tmp_path: Path, answer: bytes) -> None:
    port, routes = fake_server
    routes["/api/models/submit"] = (200, answer)
    make_cube_stl(tmp_path / "a.stl")
    model = ModelInfo("studio", "heatedbeds", "arm", tmp_path, (PartInfo("a.stl", 10, True),))
    client = ServerClient("127.0.0.1", port)
    client.token = "abc"
    with pytest.raises(CatalogPushError):
        client.push_model(model, "heatedbeds")


def test_server_addresses_are_built_the_way_the_login_screen_shows_them() -> None:
    assert ServerClient("host", 3000).base_url == "http://host:3000"
    assert ServerClient("http://host", 3000).base_url == "http://host:3000"
    assert ServerClient("https://host/", 8443).base_url == "https://host:8443"
    assert ServerClient("https://host:9000", 3000).base_url == "https://host:9000"
