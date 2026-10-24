# =============================================================================
# HYDRA-UMC-EDITOR-STL - Real STL mutation operations: stl_ops.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
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
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

STL_TRASH_DIRNAME = ".trash"
STL_SUFFIXES = (".stl",)


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


_BOX_CACHE_LIMIT = 512
_box_cache: dict[tuple[str, int, int], BoundingBox | None] = {}


def part_box(path: Path) -> BoundingBox | None:
    """The bounding box of the raw vertices of one STL part, or `None` when it cannot be read or holds no
    triangle. Reading a part parses the whole file, and the same parts are measured again at every selection of
    a model, so the answer is kept by (path, modification time, size): a part that is edited, replaced or
    transformed has another modification time or size and is read again. A part that cannot be read is
    remembered the same way (it is tried again as soon as the file changes)."""
    try:
        stat = path.stat()
    except OSError:
        return None
    key = (str(path), stat.st_mtime_ns, stat.st_size)
    if key in _box_cache:
        return _box_cache[key]
    try:
        mesh = stl_mesh.Mesh.from_file(str(path))
        box = _bounding_box(mesh) if len(mesh.vectors) > 0 else None
    except Exception:
        box = None
    if len(_box_cache) >= _BOX_CACHE_LIMIT:
        _box_cache.pop(next(iter(_box_cache)))
    _box_cache[key] = box
    return box


def clear_box_cache() -> None:
    """Forgets every measured box (used by the checks)."""
    _box_cache.clear()


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
        box = part_box(model_dir / filename)
        if box is None:
            continue
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


def _is_truncated_binary(path: Path) -> bool:
    """True for a binary STL whose header promises more triangles than the file
    holds. numpy-stl reads such a file without complaint and returns only the
    triangles that are there, so saving it again would turn a damaged download
    into a shorter, "valid" part. An ASCII STL is not judged by this rule."""
    try:
        with path.open("rb") as handle:
            head = handle.read(2048)
        size = path.stat().st_size
    except OSError:
        return False
    if head.startswith(b"solid") and b"facet" in head:
        return False
    if len(head) < 84:
        return False
    declared = int.from_bytes(head[80:84], "little")
    return 84 + 50 * declared > size


def is_real_stl(path: Path) -> bool:
    """True only if `path` actually parses as a real, non-empty ASCII or
    binary STL. Real gap found writing this project's own tests:
    numpy-stl's own Mesh.from_file() does NOT raise on arbitrary garbage
    bytes - its ASCII fallback path silently parses anything that isn't a
    recognized binary header as a zero-triangle mesh instead of failing,
    so a bare try/except here would have let a completely non-STL file
    through. A 0-triangle mesh is rejected explicitly for the same reason
    a 0-byte file would be - it is not a usable part either way."""
    if _is_truncated_binary(path):
        return False
    try:
        parsed = stl_mesh.Mesh.from_file(str(path))
    except Exception:
        return False
    return len(parsed.vectors) > 0


def _part_path(model_dir: Path, filename: str) -> Path:
    """`model_dir / filename`, refused when it would lead outside `model_dir`
    (an absolute name, `..` segments or a link pointing elsewhere)."""
    if not filename or Path(filename).is_absolute():
        raise StlOpsError(f"not a valid part name: {filename!r}")
    candidate = model_dir / filename
    if not candidate.resolve().is_relative_to(model_dir.resolve()):
        raise StlOpsError(f"part name {filename!r} leads outside the model folder")
    return candidate


def _read_mesh(path: Path) -> stl_mesh.Mesh:
    if _is_truncated_binary(path):
        raise StlOpsError(f"{path.name} is cut short: its header promises more triangles than the file holds")
    try:
        mesh = stl_mesh.Mesh.from_file(str(path))
    except Exception as error:  # numpy-stl raises ValueError/AssertionError/struct.error on a corrupt file
        raise StlOpsError(f"{path.name} is not a readable STL file: {error}") from error
    if len(mesh.vectors) == 0:
        raise StlOpsError(f"{path.name} has no triangles (empty or truncated STL)")
    return mesh


def _save_mesh_atomically(mesh: stl_mesh.Mesh, target: Path) -> None:
    """Writes next to the target and replaces it in one step, so a crash mid-write cannot truncate the part."""
    temporary = target.with_name(target.name + ".tmp")
    try:
        mesh.save(str(temporary))
        os.replace(temporary, target)
    except OSError as error:
        raise StlOpsError(f"could not write {target.name}: {error}") from error
    finally:
        if temporary.exists():
            temporary.unlink()


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
    if not all(math.isfinite(v) for v in (*translate_mm, *rotate_deg, scale)):
        raise StlOpsError("translation, rotation and scale must be finite numbers")
    if scale <= 0:
        raise StlOpsError(f"scale must be a positive number, got {scale}")
    target = _part_path(model_dir, filename)
    if not target.is_file():
        raise StlOpsError(f"no such part: {filename}")

    mesh = _read_mesh(target)
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

    transformed = points.astype(np.float32)
    if not np.isfinite(transformed).all():
        raise StlOpsError("the transform would produce vertices that are not finite (too large?) - nothing was changed")
    mesh.points = transformed.reshape(-1, 9)
    mesh.update_normals()

    backup_before_write = _unique_trash_path(model_dir, filename)
    try:
        shutil.copy2(target, backup_before_write)
    except OSError as error:
        raise StlOpsError(f"could not back up {filename}: {error}") from error
    _save_mesh_atomically(mesh, target)
    return _bounding_box(mesh)


def replace_part(model_dir: Path, filename: str, source_path: Path) -> None:
    """Overwrites `filename` with `source_path`'s own real bytes, after
    validating `source_path` actually parses as an STL - the ORIGINAL
    file is backed up into `.trash/` first, never dropped."""
    if not source_path.is_file():
        raise StlOpsError(f"replacement source does not exist: {source_path}")
    if not is_real_stl(source_path):
        raise StlOpsError(f"replacement source is not a real, parseable STL file: {source_path}")
    target = _part_path(model_dir, filename)
    if not target.is_file():
        raise StlOpsError(f"no such part to replace: {filename}")

    try:
        shutil.copy2(target, _unique_trash_path(model_dir, filename))
        shutil.copy2(source_path, target)
    except OSError as error:
        raise StlOpsError(f"could not replace {filename}: {error}") from error


def remove_part(model_dir: Path, filename: str) -> Path:
    """Moves `filename` into `.trash/` (timestamped) instead of deleting
    it - returns the real path it was moved to."""
    target = _part_path(model_dir, filename)
    if not target.is_file():
        raise StlOpsError(f"no such part: {filename}")
    destination = _unique_trash_path(model_dir, filename)
    try:
        shutil.move(str(target), str(destination))
    except OSError as error:
        raise StlOpsError(f"could not move {filename} to the trash: {error}") from error
    return destination


def unique_part_filename(model_dir: Path, filename: str) -> str:
    """A real filename inside `model_dir` that doesn't collide with an
    existing part - `filename` itself if it's already free, else
    `<stem>_copy<N><suffix>` for the first free `N`. Used by copy/paste so
    pasting the same clipboard part twice (or into the model it was
    copied from) never hits `add_part`'s own "already exists" refusal."""
    if not (model_dir / filename).exists():
        return filename
    original = Path(filename)
    stem, suffix = original.stem, original.suffix
    # keep the sub-folder (e.g. parts/foo.stl -> parts/foo_copy.stl)
    candidate = original.with_name(f"{stem}_copy{suffix}").as_posix()
    n = 2
    while (model_dir / candidate).exists():
        candidate = original.with_name(f"{stem}_copy{n}{suffix}").as_posix()
        n += 1
    return candidate


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
    if Path(filename).suffix.lower() not in STL_SUFFIXES:
        raise StlOpsError(f"a part must be a .stl file, got {filename!r}")
    target = _part_path(model_dir, filename)
    if target.exists():
        raise StlOpsError(f"a part named {filename!r} already exists - use replace_part instead")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
    except OSError as error:
        raise StlOpsError(f"could not add {filename}: {error}") from error
    return filename


STL_TRASH_EMPTIED_DIRNAME = ".trash-emptied"


def list_trash(model_dir: Path) -> list[dict]:
    """The files in this model's `.trash/`, newest first: `{"entry": <name in .trash/>, "original": <name it had>, "stamp": <UTC stamp>}`.
    Entries that do not follow the `<stamp>_<name>` pattern are listed with an empty stamp so nothing in the folder is hidden."""
    trash_dir = model_dir / STL_TRASH_DIRNAME
    if not trash_dir.is_dir():
        return []
    entries = []
    for item in trash_dir.iterdir():
        if not item.is_file():
            continue
        stamp, sep, rest = item.name.partition("_")
        if sep and stamp.endswith("Z") and stamp[:8].isdigit():
            entries.append({"entry": item.name, "original": rest.replace("__", "/"), "stamp": stamp})
        else:
            entries.append({"entry": item.name, "original": item.name, "stamp": ""})
    entries.sort(key=lambda e: (e["stamp"], e["entry"]), reverse=True)
    return entries


def restore_from_trash(model_dir: Path, entry: str) -> str:
    """Moves a `.trash/` entry back into the model under its original name (a free `_copyN` name when that one is taken - an existing
    part is never overwritten). Returns the name it was restored as."""
    if not entry or "/" in entry or "\\" in entry or entry in (".", ".."):
        raise StlOpsError(f"not a valid trash entry: {entry!r}")
    source = model_dir / STL_TRASH_DIRNAME / entry
    if not source.is_file():
        raise StlOpsError(f"no such trash entry: {entry}")
    listing = {e["entry"]: e for e in list_trash(model_dir)}
    original = listing[entry]["original"]
    _part_path(model_dir, original)  # refuses a name that would lead outside the model folder
    restored = unique_part_filename(model_dir, original)
    target = model_dir / restored
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
    except OSError as error:
        raise StlOpsError(f"could not restore {entry}: {error}") from error
    return restored


def empty_trash(model_dir: Path, confirmed: bool) -> int:
    """Clears `.trash/` after an explicit confirmation, without deleting anything for good: the files move to `.trash-emptied/<stamp>/`
    (out of the restore list, still on disk). Returns how many files were moved."""
    if not confirmed:
        raise StlOpsError("emptying the trash needs an explicit confirmation")
    entries = list_trash(model_dir)
    if not entries:
        return 0
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    archive = model_dir / STL_TRASH_EMPTIED_DIRNAME / stamp
    try:
        archive.mkdir(parents=True)
        for item in entries:
            shutil.move(str(model_dir / STL_TRASH_DIRNAME / item["entry"]), str(archive / item["entry"]))
    except OSError as error:
        raise StlOpsError(f"could not empty the trash: {error}") from error
    return len(entries)
