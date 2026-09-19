# =============================================================================
# HYDRA-UMC-EDITOR-STL - Real STL mutation operations: stl_ops.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# Every real edit this tool can make to a model's own STL parts -
# transform (translate/rotate/scale, real vertex math via numpy-stl, the
# same library HYDRA-UMC-SUITE's own render/mesh.py already depends on
# for the exact same file format), replace, remove, add. Nothing here
# ever calls Python's own os.remove()/Path.unlink() on a part the user
# didn't just add in this same session - "remove" moves the real file
# into the model's own `.trash/` subfolder (timestamped, never
# overwritten), matching this ecosystem's own "never permanently delete,
# move aside instead" convention. A "replace" first backs up the file it
# is about to overwrite the same way, so an edit is always reversible by
# hand even without this tool's own future undo feature.
# =============================================================================
from __future__ import annotations

import math
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

STL_TRASH_DIRNAME = ".trash"


class StlOpsError(RuntimeError):
    """A real, honest failure (bad path, malformed STL, name collision) -
    never silently ignored or papered over with a fabricated success."""


@dataclass(frozen=True)
class BoundingBox:
    min_xyz: tuple[float, float, float]
    max_xyz: tuple[float, float, float]


def _bounding_box(mesh: stl_mesh.Mesh) -> BoundingBox:
    points = mesh.points.reshape(-1, 3)
    return BoundingBox(
        min_xyz=tuple(float(v) for v in points.min(axis=0)),
        max_xyz=tuple(float(v) for v in points.max(axis=0)),
    )


def model_bounds(model_dir: Path, filenames: list[str]) -> BoundingBox | None:
    """Real, combined bounding box across every real, loadable part named
    in `filenames` (relative to `model_dir`) - `None` only when none of
    them could actually be loaded (an empty model, or every part
    genuinely unreadable). Used to frame a 3D view's own camera on the
    real model just selected, instead of a fixed distance that would
    look broken for a 400mm robot base and a 5mm screw alike."""
    mins: list[tuple[float, float, float]] = []
    maxs: list[tuple[float, float, float]] = []
    for filename in filenames:
        try:
            mesh = stl_mesh.Mesh.from_file(str(model_dir / filename))
        except Exception:
            continue
        if len(mesh.vectors) == 0:
            continue
        box = _bounding_box(mesh)
        mins.append(box.min_xyz)
        maxs.append(box.max_xyz)
    if not mins:
        return None
    mins_arr = np.array(mins)
    maxs_arr = np.array(maxs)
    return BoundingBox(
        min_xyz=tuple(float(v) for v in mins_arr.min(axis=0)),
        max_xyz=tuple(float(v) for v in maxs_arr.max(axis=0)),
    )


def is_real_stl(path: Path) -> bool:
    """True only if `path` actually parses as a real, non-empty ASCII or
    binary STL. Real gap found writing this project's own tests:
    numpy-stl's own Mesh.from_file() does NOT raise on arbitrary garbage
    bytes - its ASCII fallback path silently parses anything that isn't a
    recognized binary header as a zero-triangle mesh instead of failing,
    so a bare try/except here would have let a completely non-STL file
    through. A 0-triangle mesh is rejected explicitly for the same reason
    a 0-byte file would be - it is not a usable part either way."""
    try:
        parsed = stl_mesh.Mesh.from_file(str(path))
    except Exception:
        return False
    return len(parsed.vectors) > 0


def _unique_trash_path(model_dir: Path, filename: str) -> Path:
    trash_dir = model_dir / STL_TRASH_DIRNAME
    trash_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    safe_name = filename.replace("/", "__")
    return trash_dir / f"{stamp}_{safe_name}"


def transform_part(
    model_dir: Path,
    filename: str,
    translate_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotate_deg: tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: float = 1.0,
) -> BoundingBox:
    """Applies a real affine transform (scale, then rotate X/Y/Z in that
    order, then translate) to every vertex of `filename` and saves the
    result back in place as binary STL - the same real transform math
    every 3D tool in this ecosystem already uses (Rz(yaw)*Ry(pitch)*
    Rx(roll), see HYDRA-UMC-SUITE's own render/kinematics.py header),
    applied here directly to mesh vertices instead of a joint chain.
    Returns the real post-transform bounding box so a caller (CLI or
    QML) can show the operator what actually changed, not just "done"."""
    if scale <= 0:
        raise StlOpsError(f"scale must be a positive number, got {scale}")
    target = model_dir / filename
    if not target.is_file():
        raise StlOpsError(f"no such part: {filename}")

    mesh = stl_mesh.Mesh.from_file(str(target))
    points = mesh.points.reshape(-1, 3).astype(np.float64)

    points *= scale

    rx, ry, rz = (math.radians(a) for a in rotate_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rot_x = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    rot_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rot_z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    rotation = rot_z @ rot_y @ rot_x
    points = points @ rotation.T

    points += np.array(translate_mm, dtype=np.float64)

    mesh.points = points.reshape(-1, 9).astype(np.float32)
    mesh.update_normals()

    backup_before_write = _unique_trash_path(model_dir, filename)
    shutil.copy2(target, backup_before_write)
    mesh.save(str(target))
    return _bounding_box(mesh)


def replace_part(model_dir: Path, filename: str, source_path: Path) -> None:
    """Overwrites `filename` with `source_path`'s own real bytes, after
    validating `source_path` actually parses as an STL - the ORIGINAL
    file is backed up into `.trash/` first, never dropped."""
    if not source_path.is_file():
        raise StlOpsError(f"replacement source does not exist: {source_path}")
    if not is_real_stl(source_path):
        raise StlOpsError(f"replacement source is not a real, parseable STL file: {source_path}")
    target = model_dir / filename
    if not target.is_file():
        raise StlOpsError(f"no such part to replace: {filename}")

    shutil.copy2(target, _unique_trash_path(model_dir, filename))
    shutil.copy2(source_path, target)


def remove_part(model_dir: Path, filename: str) -> Path:
    """Moves `filename` into `.trash/` (timestamped) instead of deleting
    it - returns the real path it was moved to."""
    target = model_dir / filename
    if not target.is_file():
        raise StlOpsError(f"no such part: {filename}")
    destination = _unique_trash_path(model_dir, filename)
    shutil.move(str(target), str(destination))
    return destination


def add_part(model_dir: Path, source_path: Path, dest_filename: str | None = None) -> str:
    """Copies a real, externally-parseable STL into `model_dir` under
    `dest_filename` (or `source_path`'s own name) - refuses to silently
    overwrite an existing part (use replace_part for that). Returns the
    real filename the part was saved under."""
    if not source_path.is_file():
        raise StlOpsError(f"source does not exist: {source_path}")
    if not is_real_stl(source_path):
        raise StlOpsError(f"source is not a real, parseable STL file: {source_path}")
    filename = dest_filename or source_path.name
    target = model_dir / filename
    if target.exists():
        raise StlOpsError(f"a part named {filename!r} already exists - use replace_part instead")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target)
    return filename
