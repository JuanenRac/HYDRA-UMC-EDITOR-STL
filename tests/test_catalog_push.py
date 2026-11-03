# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for catalog_push.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from hydra_umc_editor_stl.catalog_push import CatalogPushError, ServerClient, build_assembly_urdf
from hydra_umc_editor_stl.model_catalog import ModelInfo, PartInfo


def _model(tmp_path: Path, parts: tuple[PartInfo, ...]) -> ModelInfo:
    for part in parts:
        (tmp_path / part.filename).write_bytes(b"fake stl bytes")
    return ModelInfo(library="studio", category="heatedbeds", model_id="default", path=tmp_path, parts=parts)


def test_build_assembly_urdf_has_one_root_link_plus_one_link_per_editable_part(tmp_path: Path) -> None:
    parts = (
        PartInfo(filename="a.stl", size_bytes=10, editable=True),
        PartInfo(filename="b.stl", size_bytes=10, editable=True),
    )
    urdf = build_assembly_urdf(_model(tmp_path, parts))
    root = ET.fromstring(urdf)
    assert [link.get("name") for link in root.findall("link")] == ["base_link", "part_0", "part_1"]
    assert len(root.findall("joint")) == 2


def test_build_assembly_urdf_skips_non_editable_parts(tmp_path: Path) -> None:
    parts = (
        PartInfo(filename="a.stl", size_bytes=10, editable=True),
        PartInfo(filename="b.glb", size_bytes=10, editable=False),
    )
    urdf = build_assembly_urdf(_model(tmp_path, parts))
    root = ET.fromstring(urdf)
    assert [link.get("name") for link in root.findall("link")] == ["base_link", "part_0"]


def test_build_assembly_urdf_every_joint_is_fixed_at_the_identity_origin(tmp_path: Path) -> None:
    parts = (PartInfo(filename="a.stl", size_bytes=10, editable=True),)
    urdf = build_assembly_urdf(_model(tmp_path, parts))
    root = ET.fromstring(urdf)
    joint = root.find("joint")
    assert joint.get("type") == "fixed"
    assert joint.find("origin") is None  # identity origin is omitted, matches writer.py's own convention
    assert joint.find("parent").get("link") == "base_link"


def test_build_assembly_urdf_mesh_filenames_are_index_prefixed_to_avoid_collisions(tmp_path: Path) -> None:
    # Same real basename in two different subfolders (LumenPnP's own
    # parts/ layout can produce this) must not collide once every mesh is
    # flattened into the server's own single meshes/ folder.
    parts = (
        PartInfo(filename="screw.stl", size_bytes=10, editable=True),
        PartInfo(filename="sub/screw.stl", size_bytes=10, editable=True),
    )
    (tmp_path / "sub").mkdir()
    urdf = build_assembly_urdf(_model(tmp_path, parts))
    root = ET.fromstring(urdf)
    mesh_filenames = [mesh.get("filename") for mesh in root.iter("mesh")]
    assert mesh_filenames == ["meshes/0_screw.stl", "meshes/0_screw.stl", "meshes/1_screw.stl", "meshes/1_screw.stl"]
    assert len(set(mesh_filenames)) == 2  # visual+collision share one real filename per part


def test_server_client_push_model_raises_without_login(tmp_path: Path) -> None:
    parts = (PartInfo(filename="a.stl", size_bytes=10, editable=True),)
    model = _model(tmp_path, parts)
    client = ServerClient("127.0.0.1", 1)
    with pytest.raises(CatalogPushError, match="Not logged in"):
        client.push_model(model, "heatedbeds")


def test_server_client_push_model_rejects_a_model_with_no_editable_parts(tmp_path: Path) -> None:
    parts = (PartInfo(filename="a.glb", size_bytes=10, editable=False),)
    model = _model(tmp_path, parts)
    client = ServerClient("127.0.0.1", 1)
    client.token = "fake-token-for-this-test-only"
    with pytest.raises(CatalogPushError, match="no editable"):
        client.push_model(model, "heatedbeds")


def test_server_client_raises_a_readable_error_for_an_unreachable_host() -> None:
    client = ServerClient("this-host-does-not-exist.invalid", 3000)
    with pytest.raises(CatalogPushError):
        client.login("admin", "wrong")


def _pushable(tmp_path: Path, role: str | None):
    from .conftest import make_cube_stl

    make_cube_stl(tmp_path / "a.stl")
    model = _model(tmp_path, (PartInfo(filename="a.stl", size_bytes=10, editable=True),))
    client = ServerClient("127.0.0.1", 1)
    client.token = "t"
    client.role = role
    return client, model


@pytest.mark.parametrize("role", ["operator", "viewer", "", None, "ADMIN"])
def test_push_is_blocked_without_the_admin_role(tmp_path: Path, role) -> None:
    client, model = _pushable(tmp_path, role)
    with pytest.raises(CatalogPushError, match="admin account"):
        client.push_model(model, "heatedbeds", confirmed=True)


def test_push_is_blocked_without_the_confirmation(tmp_path: Path) -> None:
    client, model = _pushable(tmp_path, "admin")
    with pytest.raises(CatalogPushError, match="not confirmed"):
        client.push_model(model, "heatedbeds")


def test_login_keeps_the_role_the_server_reports(monkeypatch) -> None:
    client = ServerClient("127.0.0.1", 1)
    monkeypatch.setattr(client, "_request", lambda *a, **k: {"token": "t", "role": "operator"})
    client.login("u", "p")
    assert client.role == "operator"
    monkeypatch.setattr(client, "_request", lambda *a, **k: {"token": "t"})
    client.login("u", "p")
    assert client.role is None


def test_push_summary_names_the_server_the_model_and_the_replacement(tmp_path: Path) -> None:
    from hydra_umc_editor_stl.catalog_push import push_summary

    _, model = _pushable(tmp_path, "admin")
    lines = push_summary(model, "heatedbeds", "http://h:3000", overwrite=True)
    assert "http://h:3000" in lines[0] and "heatedbeds" in lines[1] and "REPLACED" in lines[2]
