# =============================================================================
# HYDRA-UMC-EDITOR-STL - One model library for both apps: library_sync.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# The two apps carry the same models in two folders (see model_catalog.LIBRARIES). Instead of editing both by hand, one of
# them is the master and the other is brought in line with it. The comparison goes by content (size, then SHA-256). By default
# nothing is written (a plan is returned); with `apply=True` the files that are missing or different in the target are copied
# from the master, and a file that is replaced is first kept in `.sync-backup/<stamp>/` of the target. Nothing is ever deleted:
# files that exist only in the target are reported and left alone. Hidden folders (`.trash`, `.lite`, ...) are not compared.
# =============================================================================
from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .model_catalog import LIBRARIES, resolve_library_root

BACKUP_DIRNAME = ".sync-backup"


class LibrarySyncError(RuntimeError):
    pass


@dataclass
class LibraryDiff:
    same: int = 0
    only_in_master: list[str] = field(default_factory=list)
    only_in_target: list[str] = field(default_factory=list)
    different: list[str] = field(default_factory=list)

    @property
    def in_sync(self) -> bool:
        return not (self.only_in_master or self.different)


def _files(root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        found[relative.as_posix()] = path
    return found


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            sha.update(block)
    return sha.hexdigest()


def _roots(ecosystem_root: Path, master: str, target: str) -> tuple[Path, Path]:
    names = {name for name, _ in LIBRARIES}
    if master not in names or target not in names or master == target:
        raise LibrarySyncError(f"master and target must be two different libraries of {sorted(names)}, got {master!r} and {target!r}")
    master_root = resolve_library_root(ecosystem_root, master)
    target_root = resolve_library_root(ecosystem_root, target)
    if master_root is None:
        raise LibrarySyncError(f"the {master} library was not found under {ecosystem_root}")
    if target_root is None:
        raise LibrarySyncError(f"the {target} library was not found under {ecosystem_root}")
    return master_root, target_root


def compare_libraries(ecosystem_root: Path, master: str = "studio", target: str = "suite") -> LibraryDiff:
    master_root, target_root = _roots(ecosystem_root, master, target)
    a, b = _files(master_root), _files(target_root)
    diff = LibraryDiff()
    for name, path in a.items():
        other = b.get(name)
        if other is None:
            diff.only_in_master.append(name)
        elif path.stat().st_size != other.stat().st_size or _digest(path) != _digest(other):
            diff.different.append(name)
        else:
            diff.same += 1
    diff.only_in_target = [name for name in b if name not in a]
    return diff


def sync_libraries(ecosystem_root: Path, master: str = "studio", target: str = "suite", apply: bool = False) -> dict:
    """Brings the target in line with the master. Returns `{"diff": LibraryDiff, "copied": [...], "replaced": [...], "applied": bool}`.
    Without `apply` it only returns the plan (what would be copied and replaced)."""
    master_root, target_root = _roots(ecosystem_root, master, target)
    diff = compare_libraries(ecosystem_root, master, target)
    result = {"diff": diff, "copied": list(diff.only_in_master), "replaced": list(diff.different), "applied": False}
    if not apply:
        return result
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    try:
        for name in diff.different:
            destination = target_root / name
            backup = target_root / BACKUP_DIRNAME / stamp / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
        for name in [*diff.only_in_master, *diff.different]:
            destination = target_root / name
            if not destination.resolve().is_relative_to(target_root.resolve()):
                raise LibrarySyncError(f"{name!r} leads outside the target library")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(destination.name + ".tmp")
            shutil.copy2(master_root / name, temporary)
            temporary.replace(destination)
    except OSError as error:
        raise LibrarySyncError(f"could not bring the {target} library in line: {error}") from error
    result["applied"] = True
    return result
