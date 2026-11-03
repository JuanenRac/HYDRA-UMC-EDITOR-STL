# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the GLB writer and the light copies that travel with a push
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import pytest

from hydra_umc_editor_stl.catalog_push import CatalogPushError, ServerClient
from hydra_umc_editor_stl.glb import mesh_to_glb, read_glb
from hydra_umc_editor_stl.model_catalog import ModelInfo, PartInfo

from .conftest import make_cube_stl
from .test_light_diff_sync import sphere_vectors


class _Capture(ServerClient):
    def __init__(self) -> None:
        super().__init__("127.0.0.1", 1)
        self.token = "t"; self.role = "admin"
        self.sent: dict = {}

    def _request(self, method, path, body=None, auth=False):  # type: ignore[override]
        self.sent = body or {}
        return {"slug": "m"}


def _model(tmp_path: Path) -> ModelInfo:
    from stl import mesh as stl_mesh

    sphere = stl_mesh.Mesh(np.zeros(len(sphere_vectors()), dtype=stl_mesh.Mesh.dtype))
    sphere.vectors[:] = sphere_vectors().astype(np.float32)
    sphere.save(str(tmp_path / "ball.stl"))
    return ModelInfo(library="studio", category="heatedbeds", model_id="m", path=tmp_path, parts=(PartInfo("ball.stl", (tmp_path / "ball.stl").stat().st_size, True),))


def test_a_cube_becomes_a_valid_glb_with_shared_vertices(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "c.stl")
    from stl import mesh as stl_mesh

    vectors = stl_mesh.Mesh.from_file(str(tmp_path / "c.stl")).vectors
    document, binary = read_glb(mesh_to_glb(vectors))
    positions, indices = document["accessors"]
    assert positions["count"] == 8 and indices["count"] == 36  # 12 triangles, 8 corners
    assert document["bufferViews"][1]["byteOffset"] + document["bufferViews"][1]["byteLength"] <= len(binary)
    assert len(binary) % 4 == 0


def test_a_glb_without_triangles_is_refused() -> None:
    with pytest.raises(ValueError):
        mesh_to_glb(np.zeros((0, 3, 3)))


def test_a_push_sends_no_light_copy_unless_asked(tmp_path: Path) -> None:
    client = _Capture()
    client.push_model(_model(tmp_path), "heatedbeds", confirmed=True)
    assert [m["filename"] for m in client.sent["meshFiles"]] == ["0_ball.stl"]


@pytest.mark.parametrize("fmt", ["stl", "glb"])
def test_a_push_can_send_a_lighter_copy_next_to_the_full_one(tmp_path: Path, fmt: str) -> None:
    client = _Capture()
    client.push_model(_model(tmp_path), "heatedbeds", lite_format=fmt, lite_ratio=0.2, confirmed=True)
    files = {m["filename"]: base64.b64decode(m["base64"]) for m in client.sent["meshFiles"]}
    assert set(files) == {"0_ball.stl", f"0_ball.lite.{fmt}"}
    assert len(files[f"0_ball.lite.{fmt}"]) < len(files["0_ball.stl"]) / 2
    assert 'filename="meshes/0_ball.stl"' in client.sent["urdfXml"] and ".lite" not in client.sent["urdfXml"]
    if fmt == "glb":
        read_glb(files["0_ball.lite.glb"])


def test_an_unknown_light_format_is_refused_before_anything_is_sent(tmp_path: Path) -> None:
    client = _Capture()
    with pytest.raises(CatalogPushError, match="light-copy format"):
        client.push_model(_model(tmp_path), "heatedbeds", lite_format="draco", confirmed=True)
    assert client.sent == {}
