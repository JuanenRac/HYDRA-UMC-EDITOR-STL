# =============================================================================
# HYDRA-UMC-EDITOR-STL - Push to a running server's model catalog: catalog_push.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
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
# joined by a `fixed` joint at the identity origin.
#
# The identity origin is the right pose for categories of independent pieces
# (heated beds, racks, vacuum tables). The STL parts of a robot or machine are
# each stored in their OWN link frame (see assembly.py), so for those the joint
# origin of every part is its home-pose placement from the kinematics of
# HYDRA-UMC-SUITE (the same placement the assembled view shows): the pushed
# robot arrives assembled, still without articulation. Only when those
# placements cannot be found (no SUITE checkout, or a model it has no
# kinematics for) would the parts arrive stacked at the origin, and then the
# push is refused unless it is forced. `push_warnings()` reports this first.
# =============================================================================
from __future__ import annotations

import base64
import http.client
import io
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import numpy as np
from stl import mesh as stl_mesh

from .assembly import PartPlacement, _mesh_is_millimeters, _rotation_matrix, assembled_transforms, unit_from_metadata
from .decimate import DEFAULT_RATIO, decimate_to_ratio
from .glb import mesh_to_glb
from .mesh_check import check_stl
from .model_catalog import ModelInfo, is_independent_parts_category
from .stl_ops import StlOpsError, _read_mesh

REQUEST_TIMEOUT_S = 20.0

# HYDRA-UMC-SERVER accepts a JSON body of at most 50 MB (express.json);
# stay a little under it.
MAX_BODY_BYTES = 49 * 1024 * 1024


class CatalogPushError(Exception):
    """Always carries a human-readable message - shown directly by
    whichever UI (CLI or QML) called this module."""


def _upload_filename(index: int, part_filename: str) -> str:
    """The name a part's own mesh is uploaded under - index-prefixed so
    two parts with the same basename in different subfolders (LumenPnP's
    own `parts/` layout, for one real example) never collide once
    flattened into the server's own single `meshes/` folder."""
    return f"{index}_{Path(part_filename).name}"


def home_placements(model: ModelInfo, ecosystem_root: Path | None) -> dict[str, PartPlacement] | None:
    """Where each part of a robot or machine sits at its home pose, or None when that is not known here."""
    if ecosystem_root is None:
        return None
    try:
        return assembled_transforms(ecosystem_root, model.category, model.model_id, model.path)
    except Exception:  # noqa: BLE001 - a kinematics module that fails is the same as having none
        return None


def _unplaced_parts(model: ModelInfo, placements: dict[str, PartPlacement] | None) -> list[str]:
    return [p.filename for p in model.parts if p.editable and (placements is None or p.filename not in placements)]


def _origin_attributes(model: ModelInfo, part_filename: str, placement: PartPlacement) -> tuple[str, str]:
    """(xyz, rpy) of a joint origin: meters and radians, as a URDF wants them."""
    scale = 0.001 if _mesh_is_millimeters(model.path / part_filename, unit_from_metadata(model.metadata)) else 1.0
    xyz = " ".join(f"{v * scale:.9g}" for v in placement.position)
    r = _rotation_matrix(placement.rotation_wxyz)
    pitch = float(np.arcsin(-np.clip(r[2, 0], -1.0, 1.0)))
    if abs(r[2, 0]) < 0.999999:
        roll, yaw = float(np.arctan2(r[2, 1], r[2, 2])), float(np.arctan2(r[1, 0], r[0, 0]))
    else:  # gimbal lock: the roll is folded into the yaw
        roll, yaw = 0.0, float(np.arctan2(-r[0, 1], r[1, 1]))
    return xyz, " ".join(f"{v:.9g}" for v in (roll, pitch, yaw))


def push_warnings(model: ModelInfo, category: str, ecosystem_root: Path | None = None) -> list[str]:
    """What a push would leave out or get wrong, so the operator can decide first."""
    warnings: list[str] = []
    skipped = [p.filename for p in model.parts if not p.editable]
    if skipped:
        warnings.append(f"{len(skipped)} part(s) are not .stl files and will not be uploaded (for example {skipped[0]}).")
    if not is_independent_parts_category(category):
        unplaced = _unplaced_parts(model, home_placements(model, ecosystem_root))
        if unplaced:
            warnings.append(
                f"Parts of a robot or machine are stored in their own link frame and the home-pose placement of "
                f"{len(unplaced)} part(s) is not known here (for example {unplaced[0]}): they would sit at the origin. "
                "Articulate the model with HYDRA-UMC-EDITOR-URDF, or check that HYDRA-UMC-SUITE is next to this checkout."
            )
    # What is wrong with the meshes themselves, part by part (a part that cannot be read is reported by the file check).
    for part in model.parts:
        if not part.editable:
            continue
        report = check_stl(model.path / part.filename)
        if report is not None:
            warnings.extend(f"{part.filename}: {problem}." for problem in report.problems)
    return warnings


def build_assembly_urdf(model: ModelInfo, placements: dict[str, PartPlacement] | None = None) -> str:
    """A real, minimal URDF for this model's own editable (.stl) parts -
    see this module's own header for why a rigid, un-articulated assembly
    like this is a legitimate URDF rather than a hack. With `placements`
    each part's joint carries its home-pose origin instead of the identity."""
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
        if placements is not None and part.filename in placements:
            xyz, rpy = _origin_attributes(model, part.filename, placements[part.filename])
            origin_el = ET.SubElement(joint_el, "origin")
            origin_el.set("xyz", xyz)
            origin_el.set("rpy", rpy)

    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


def _lite_copy(source: Path, upload_name: str, lite_format: str, ratio: float) -> tuple[str, bytes]:
    """(file name, bytes) of the light copy of one part, in memory: the originals and the model folder are not touched."""
    try:
        reduced = decimate_to_ratio(_read_mesh(source).vectors, ratio)
        if len(reduced) == 0:
            raise StlOpsError(f"{source.name} has no usable triangles")
        stem = upload_name.rsplit(".", 1)[0]
        if lite_format == "glb":
            return f"{stem}.lite.glb", mesh_to_glb(reduced, stem)
        light = stl_mesh.Mesh(np.zeros(len(reduced), dtype=stl_mesh.Mesh.dtype))
        light.vectors[:] = reduced.astype(np.float32)
        light.update_normals()
        buffer = io.BytesIO()
        light.save(f"{stem}.lite.stl", fh=buffer)
        return f"{stem}.lite.stl", buffer.getvalue()
    except (StlOpsError, ValueError) as error:
        raise CatalogPushError(f"could not make the light copy of {source.name}: {error}") from error


def push_summary(model: ModelInfo, category: str, base_url: str, overwrite: bool = False) -> list[str]:
    """The lines shown before the confirmation: what goes where, so the person confirms with the facts in front of them."""
    editable = sum(1 for p in model.parts if p.editable)
    lines = [
        f"Server: {base_url}",
        f"Model: {model.model_id} ({editable} editable part(s)) -> category '{category}'",
    ]
    if overwrite:
        lines.append("An existing submission with the same name will be REPLACED.")
    return lines


class ServerClient:
    """One instance per server the operator points this app at - mirrors
    HYDRA-UMC-EDITOR-URDF's own server/client.py StudioClient (same real
    2-endpoint contract: login, then push), kept as an independent, small
    copy here rather than a new cross-repo runtime dependency, same
    reasoning HYDRA-UMC-SDK's own doc_policy.py module documents for why
    this ecosystem prefers a vendored copy over a live import for a
    two-function contract like this one."""

    def __init__(self, host: str, port: int = 3000):
        # `host` may carry a scheme (https://server) to avoid sending the
        # password in clear text; a bare host keeps using plain http.
        if host.startswith(("http://", "https://")):
            self.base_url = host.rstrip("/") if host.count(":") > 1 else f"{host.rstrip('/')}:{port}"
        else:
            self.base_url = f"http://{host}:{port}"
        self.token: str | None = None
        # The role the server reported for this login ("admin", "operator", "viewer"...); None until a login says it.
        self.role: str | None = None
        self.last_skipped_parts = 0
        self.last_placed_parts = 0

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
                answer = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            message = f"HTTP {e.code}"
            try:
                payload = json.loads(e.read().decode("utf-8"))
                if isinstance(payload, dict) and isinstance(payload.get("error"), str):
                    message = payload["error"]
            except (ValueError, OSError, http.client.HTTPException):
                pass
            raise CatalogPushError(f"{self.base_url}{path}: {message}") from e
        except (OSError, http.client.HTTPException) as e:
            raise CatalogPushError(f"{self.base_url}{path}: {e}") from e
        except ValueError as e:  # not JSON, or not UTF-8: a proxy or captive portal page, say
            raise CatalogPushError(f"{self.base_url}{path}: the answer is not valid JSON") from e
        if not isinstance(answer, dict):
            raise CatalogPushError(f"{self.base_url}{path}: the answer is not a JSON object")
        return answer

    def login(self, username: str, password: str) -> None:
        """POST /api/login - only an admin-role token can actually use
        POST /api/models/submit (HYDRA-UMC-SERVER's own server.ts,
        requireAdmin), same real restriction EDITOR-URDF's own client
        already documents."""
        data = self._request("POST", "/api/login", {"username": username, "password": password})
        token = data.get("token")
        if not isinstance(token, str) or not token:
            raise CatalogPushError("Login succeeded but the server returned no token.")
        self.token = token
        role = data.get("role")
        self.role = role if isinstance(role, str) and role else None

    def require_admin(self) -> None:
        """Block the push with a clear reason unless the server said this login is an admin. The check is made here before
        anything is sent; the server checks the role again on its own (requireAdmin), so this is the early, readable refusal,
        not the only guard. A server that reports no role is treated as not admin (fail closed)."""
        if not self.token:
            raise CatalogPushError("Not logged in - call login() first.")
        if self.role != "admin":
            shown = self.role if self.role else "unknown"
            raise CatalogPushError(
                f"Not pushed: sending a model to the catalog needs an admin account of the server, and this login has the "
                f"role '{shown}'. Sign in with an admin account."
            )

    def push_model(
        self,
        model: ModelInfo,
        category: str,
        overwrite: bool = False,
        allow_stacked: bool = False,
        ecosystem_root: Path | None = None,
        lite_format: str | None = None,
        lite_ratio: float = DEFAULT_RATIO,
        confirmed: bool = False,
    ) -> str:
        """POST /api/models/submit - builds the assembly URDF above,
        base64-encodes every editable part's own current STL bytes
        (already reflecting any transform/replace/add this tool applied),
        and submits. Returns the server-assigned slug on success; raises
        CatalogPushError with the server's own message on a real failure
        (including its 409 name-collision message when `overwrite` is
        not set).

        With `lite_format` "stl" or "glb" (the default None sends nothing extra) a lighter copy of each part travels
        too, as `<mesh name>.lite.stl` or `.lite.glb` next to the full one, for the apps that cannot carry the full mesh;
        the URDF keeps pointing at the full mesh.

        The push changes the server's catalog, so it needs an admin login (`role` reported by the server) and an explicit
        `confirmed=True` from the person (the push window's confirmation box, `--yes` on the command line); without either it
        is refused before anything is sent. The server records the push under the account of the token this client sends;
        nothing here makes up an identity."""
        if not self.token:
            raise CatalogPushError("Not logged in - call login() first.")
        if lite_format not in (None, "stl", "glb"):
            raise CatalogPushError(f"unknown light-copy format {lite_format!r} (use stl or glb)")
        editable_parts = [p for p in model.parts if p.editable]
        if not editable_parts:
            raise CatalogPushError("This model has no editable (.stl) parts to push.")
        self.require_admin()
        if not confirmed:
            raise CatalogPushError(
                "Not pushed: the person has not confirmed the push. Confirm it in the push window or pass --yes on the command line."
            )
        placements = None
        self.last_placed_parts = 0
        if not is_independent_parts_category(category):
            placements = home_placements(model, ecosystem_root)
            self.last_placed_parts = len(editable_parts) - len(_unplaced_parts(model, placements))
            if self.last_placed_parts == 0 and not allow_stacked:
                raise CatalogPushError(
                    "Not pushed: the home-pose placement of this robot or machine is not known here, so its parts "
                    "would arrive stacked at the origin. Articulate it with HYDRA-UMC-EDITOR-URDF, check that "
                    "HYDRA-UMC-SUITE is next to this checkout, or pass allow_stacked=True (--allow-stacked-push) "
                    "to send it anyway."
                )
        urdf_xml = build_assembly_urdf(model, placements)
        self.last_skipped_parts = sum(1 for p in model.parts if not p.editable)
        mesh_files = []
        for index, part in enumerate(editable_parts):
            mesh_bytes = (model.path / part.filename).read_bytes()
            mesh_files.append({
                "filename": _upload_filename(index, part.filename),
                "base64": base64.b64encode(mesh_bytes).decode("ascii"),
            })
            if lite_format is not None:
                lite_name, lite_bytes = _lite_copy(model.path / part.filename, _upload_filename(index, part.filename), lite_format, lite_ratio)
                mesh_files.append({"filename": lite_name, "base64": base64.b64encode(lite_bytes).decode("ascii")})

        body = {
            "name": model.model_id,
            "category": category,
            "urdfFilename": f"{model.model_id}.urdf",
            "urdfXml": urdf_xml,
            "meshFiles": mesh_files,
            "overwrite": overwrite,
        }
        size = len(json.dumps(body).encode("utf-8"))
        if size > MAX_BODY_BYTES:
            raise CatalogPushError(
                f"The upload would be {size / 1024 / 1024:.0f} MB, above the server's 50 MB limit - "
                "remove parts or push fewer pieces."
            )
        data = self._request("POST", "/api/models/submit", body, auth=True)
        slug = data.get("slug")
        if not isinstance(slug, str) or not slug:
            raise CatalogPushError("Push succeeded but the server returned no slug.")
        return slug
