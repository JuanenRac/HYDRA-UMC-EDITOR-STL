# =============================================================================
# HYDRA-UMC-EDITOR-STL - Push to a running server's model catalog: catalog_push.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# This tool otherwise only ever edits STUDIO's/SUITE's own bundled model
# libraries directly on local disk (model_catalog.py) - there was no way
# to hand an edited/added model to a running HYDRA-UMC-SERVER's own live
# model-submission catalog (POST /api/models/submit), the same real
# endpoint HYDRA-UMC-EDITOR-URDF's own server/client.py already uses.
# That endpoint's contract is real-robot-shaped (name/category/urdfXml/
# meshFiles) since it was built for URDF submissions - but the parts this
# tool edits are plain, un-jointed STL meshes with no kinematics at all.
# Rather than inventing a second, STL-only server endpoint, this module
# wraps the model's own editable parts in the smallest REAL URDF that
# contract already accepts: one root link plus one child link per part,
# joined by a `fixed` joint at the identity origin - honest, since every
# part's own actual position is already baked into its own STL vertices
# by transform_part(), never a synthetic pose invented here.
# =============================================================================
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

from .model_catalog import ModelInfo

REQUEST_TIMEOUT_S = 20.0


class CatalogPushError(Exception):
    """Always carries a human-readable message - shown directly by
    whichever UI (CLI or QML) called this module."""


def _upload_filename(index: int, part_filename: str) -> str:
    """The name a part's own mesh is uploaded under - index-prefixed so
    two parts with the same basename in different subfolders (LumenPnP's
    own `parts/` layout, for one real example) never collide once
    flattened into the server's own single `meshes/` folder."""
    return f"{index}_{Path(part_filename).name}"


def build_assembly_urdf(model: ModelInfo) -> str:
    """A real, minimal URDF for this model's own editable (.stl) parts -
    see this module's own header for why a rigid, un-articulated assembly
    like this is a legitimate URDF rather than a hack."""
    editable_parts = [p for p in model.parts if p.editable]
    root = ET.Element("robot")
    root.set("name", model.model_id)
    ET.SubElement(root, "link").set("name", "base_link")

    for index, part in enumerate(editable_parts):
        link_name = f"part_{index}"
        link_el = ET.SubElement(root, "link")
        link_el.set("name", link_name)
        mesh_ref = f"meshes/{_upload_filename(index, part.filename)}"
        for tag in ("visual", "collision"):
            el = ET.SubElement(link_el, tag)
            geometry_el = ET.SubElement(el, "geometry")
            ET.SubElement(geometry_el, "mesh").set("filename", mesh_ref)

        joint_el = ET.SubElement(root, "joint")
        joint_el.set("name", f"{link_name}_fixed")
        joint_el.set("type", "fixed")
        ET.SubElement(joint_el, "parent").set("link", "base_link")
        ET.SubElement(joint_el, "child").set("link", link_name)

    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


class ServerClient:
    """One instance per server the operator points this app at - mirrors
    HYDRA-UMC-EDITOR-URDF's own server/client.py StudioClient (same real
    2-endpoint contract: login, then push), kept as an independent, small
    copy here rather than a new cross-repo runtime dependency, same
    reasoning HYDRA-UMC-SDK's own doc_policy.py module documents for why
    this ecosystem prefers a vendored copy over a live import for a
    two-function contract like this one."""

    def __init__(self, host: str, port: int = 3000):
        self.base_url = f"http://{host}:{port}"
        self.token: str | None = None

    def _request(self, method: str, path: str, body: dict | None = None, auth: bool = False) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"}
        if auth:
            if not self.token:
                raise CatalogPushError("Not logged in - call login() first.")
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                payload = json.loads(e.read().decode("utf-8"))
                message = payload.get("error", f"HTTP {e.code}")
            except (ValueError, UnicodeDecodeError):
                message = f"HTTP {e.code}"
            raise CatalogPushError(f"{self.base_url}{path}: {message}") from e
        except OSError as e:
            raise CatalogPushError(f"{self.base_url}{path}: {e}") from e

    def login(self, username: str, password: str) -> None:
        """POST /api/login - only an admin-role token can actually use
        POST /api/models/submit (HYDRA-UMC-SERVER's own server.ts,
        requireAdmin), same real restriction EDITOR-URDF's own client
        already documents."""
        data = self._request("POST", "/api/login", {"username": username, "password": password})
        token = data.get("token")
        if not token:
            raise CatalogPushError("Login succeeded but the server returned no token.")
        self.token = token

    def push_model(self, model: ModelInfo, category: str, overwrite: bool = False) -> str:
        """POST /api/models/submit - builds the assembly URDF above,
        base64-encodes every editable part's own current STL bytes
        (already reflecting any transform/replace/add this tool applied),
        and submits. Returns the server-assigned slug on success; raises
        CatalogPushError with the server's own message on a real failure
        (including its 409 name-collision message when `overwrite` is
        not set)."""
        editable_parts = [p for p in model.parts if p.editable]
        if not editable_parts:
            raise CatalogPushError("This model has no editable (.stl) parts to push.")
        urdf_xml = build_assembly_urdf(model)
        mesh_files = []
        for index, part in enumerate(editable_parts):
            mesh_bytes = (model.path / part.filename).read_bytes()
            mesh_files.append({
                "filename": _upload_filename(index, part.filename),
                "base64": base64.b64encode(mesh_bytes).decode("ascii"),
            })

        body = {
            "name": model.model_id,
            "category": category,
            "urdfFilename": f"{model.model_id}.urdf",
            "urdfXml": urdf_xml,
            "meshFiles": mesh_files,
            "overwrite": overwrite,
        }
        data = self._request("POST", "/api/models/submit", body, auth=True)
        slug = data.get("slug")
        if not slug:
            raise CatalogPushError("Push succeeded but the server returned no slug.")
        return slug
