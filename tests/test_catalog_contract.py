# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests/test_catalog_contract.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What this editor sends to the model catalog of the server, against the contract it shares with HYDRA-UMC-EDITOR-URDF
(`tests/catalog_submit.json`, a byte copy of `conformance/fixtures/v1/catalog-submit.json` of HYDRA-UMC-SDK)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from hydra_umc_editor_stl.catalog_push import CatalogPushError, ServerClient
from hydra_umc_editor_stl.model_catalog import ModelInfo, PartInfo

CONTRACT_FILE = Path(__file__).parent / "catalog_submit.json"
# The same number in the other editor: the contract changes in the SDK first, then in both copies.
CONTRACT_SHA256 = "86442c8b44d37b068d73f728602938d0700e5d5e702f6d1ced5711b4f2507cb1"
CONTRACT = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))


def _recording(client) -> list[tuple[str, str, dict | None, bool]]:
    """Replaces the HTTP call of the client: it answers with the examples of the contract and keeps what was asked."""
    asked: list[tuple[str, str, dict | None, bool]] = []
    answers = {spec["path"]: spec["response"] for spec in (CONTRACT["login"], CONTRACT["submit"])}

    def request(method: str, path: str, body: dict | None = None, auth: bool = False) -> dict:
        asked.append((method, path, body, auth))
        return answers.get(path, CONTRACT["download"]["response"])

    client._request = request
    return asked


def _same_shape(sent: dict, required: dict, optional: dict) -> None:
    assert set(required) <= set(sent) <= set(required) | set(optional), sorted(sent)
    for key, value in sent.items():
        assert type(value) is type({**required, **optional}[key]), key


def test_the_contract_is_the_agreed_copy() -> None:
    assert hashlib.sha256(CONTRACT_FILE.read_bytes()).hexdigest() == CONTRACT_SHA256


def test_login_and_submit_send_what_the_contract_says(tmp_path: Path) -> None:
    (tmp_path / "base.stl").write_bytes(b"solid base")
    model = ModelInfo(library="studio", category="robots", model_id="arm", path=tmp_path, parts=(PartInfo(filename="base.stl", size_bytes=10, editable=True),))
    client = ServerClient("127.0.0.1")
    asked = _recording(client)
    login, submit = CONTRACT["login"], CONTRACT["submit"]
    client.login(login["request"]["username"], login["request"]["password"])
    assert client.push_model(model, "robots", allow_stacked=True, confirmed=True) == submit["response"]["slug"]
    (method, path, body, auth), (method2, path2, body2, auth2) = asked
    assert (method, path, auth) == (login["method"], login["path"], False)
    assert body == login["request"]
    assert (method2, path2, auth2) == (submit["method"], submit["path"], True)
    assert body2 is not None
    _same_shape(body2, submit["required"], submit["optional"])
    assert all(set(entry) == {"filename", "base64"} for entry in body2["meshFiles"])
    assert "attribution" not in body2, "a model with no ATTRIBUTION.txt sends none"


def test_the_attribution_of_the_model_folder_or_of_the_command_is_sent(tmp_path: Path) -> None:
    (tmp_path / "base.stl").write_bytes(b"solid base")
    (tmp_path / "ATTRIBUTION.txt").write_bytes("\ufeffmeshes by their authors, CC-BY\r\n".encode("utf-8"))
    model = ModelInfo(library="studio", category="robots", model_id="arm", path=tmp_path, parts=(PartInfo(filename="base.stl", size_bytes=10, editable=True),))
    client = ServerClient("127.0.0.1")
    asked = _recording(client)
    client.login("admin", "x")
    client.push_model(model, "robots", allow_stacked=True, confirmed=True)
    body = asked[-1][2]
    assert body["attribution"] == "meshes by their authors, CC-BY"
    _same_shape(body, CONTRACT["submit"]["required"], CONTRACT["submit"]["optional"])
    client.push_model(model, "robots", allow_stacked=True, confirmed=True, attribution="another credit")
    assert asked[-1][2]["attribution"] == "another credit"


def test_an_attribution_the_server_would_refuse_is_not_sent(tmp_path: Path) -> None:
    (tmp_path / "base.stl").write_bytes(b"solid base")
    model = ModelInfo(library="studio", category="robots", model_id="arm", path=tmp_path, parts=(PartInfo(filename="base.stl", size_bytes=10, editable=True),))
    client = ServerClient("127.0.0.1")
    asked = _recording(client)
    client.login("admin", "x")
    for setup in (lambda: None, lambda: (tmp_path / "ATTRIBUTION.txt").write_bytes(b"\xff\xfe\x00")):
        setup()
        try:
            client.push_model(model, "robots", allow_stacked=True, confirmed=True, attribution=None if (tmp_path / "ATTRIBUTION.txt").exists() else "x" * 8001)
        except CatalogPushError:
            pass
        else:
            raise AssertionError("expected a refusal")
    assert [entry[1] for entry in asked] == ["/api/login"]
