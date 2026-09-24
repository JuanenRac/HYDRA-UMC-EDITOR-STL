# =============================================================================
# HYDRA-UMC-EDITOR-STL - Model library discovery: model_catalog.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# Real, read-only discovery of the ecosystem's own model libraries -
# HYDRA-UMC-STUDIO's own `public/models/` and HYDRA-UMC-SUITE's own
# `assets/meshes/` (see both repos' own 2026-09 reorganization into
# category folders: robots-5-dof/robots-6-dof/robots-7-dof, machine-pnp/
# machine-cnc/machine-laser, heatedbeds/racks/vacuum-tables, each with a
# per-model `metadata.json` alongside its ATTRIBUTION.txt). Assumes the
# same "sibling checkout" layout every other cross-repo tool in this
# ecosystem already assumes (HYDRA-UMC-SUITE, HYDRA-UMC-UPDATER) - both
# libraries sit under one ecosystem root directory the user points this
# tool at (settings.py's own `ecosystem_root`), not hardcoded to any one
# machine's own path.
# =============================================================================
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

#: (library id, path relative to the ecosystem root) - real, not guessed;
#: both are the exact real trees HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE ship.
LIBRARIES: tuple[tuple[str, str], ...] = (
    ("studio", "HYDRA-UMC-STUDIO/public/models"),
    ("suite", "HYDRA-UMC-SUITE/assets/meshes"),
)

#: Real mesh file extensions this tool recognizes as an editable "part" -
#: matches every real format the two libraries above actually ship
#: (.STL is the overwhelming majority; a few LumenPnP parts are .glb,
#: listed here as read-only/non-editable parts instead of hidden).
MESH_EXTENSIONS: frozenset[str] = frozenset({".stl", ".glb"})

#: Categories whose STL files are independent, mutually exclusive
#: size/variant options (e.g. 4 real heated-bed sizes) - never meant to
#: be viewed/assembled together the way a robot/CNC/PnP/laser model's own
#: real links or CAD parts are. Real gap found live: the 3D viewer used
#: to render every one of these on top of the others at the same origin
#: (one giant plate visible, the rest hidden inside/behind it) since it
#: had no way to tell "these are alternatives" apart from "these are one
#: real assembly" - both are just "a folder of STL files" to
#: model_catalog.py otherwise.
INDEPENDENT_PART_CATEGORIES: frozenset[str] = frozenset({"heatedbeds", "vacuum-tables", "racks"})


def is_independent_parts_category(category: str) -> bool:
    """True for a category whose parts should be viewed one at a time
    (the operator's own current selection only), never all overlapping."""
    return category in INDEPENDENT_PART_CATEGORIES


@dataclass(frozen=True)
class PartInfo:
    filename: str
    size_bytes: int
    editable: bool  # True for a real .stl this tool can load/transform; .glb parts are list-only.


@dataclass(frozen=True)
class ModelInfo:
    library: str
    category: str
    model_id: str
    path: Path
    parts: tuple[PartInfo, ...] = field(default_factory=tuple)
    metadata: dict | None = None


def resolve_library_root(ecosystem_root: Path, library: str) -> Path | None:
    for lib_id, relative in LIBRARIES:
        if lib_id == library:
            candidate = ecosystem_root / relative
            return candidate if candidate.is_dir() else None
    return None


def list_categories(ecosystem_root: Path, library: str) -> list[str]:
    """Every real category subfolder present for this library - not a
    fixed list, so a category added to one library later (or missing on
    a partial checkout) is reflected honestly rather than assumed."""
    root = resolve_library_root(ecosystem_root, library)
    if root is None:
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def list_models(ecosystem_root: Path, library: str, category: str) -> list[str]:
    """Every real model subfolder under `category` - for machine-pnp/
    machine-cnc/machine-laser this is the machine id (lumenpnp,
    juanenpnp, ...); for the robots-*-dof categories it's the robot's
    own folder name; for heatedbeds/racks/vacuum-tables it's the variant
    folder (currently always just "default")."""
    root = resolve_library_root(ecosystem_root, library)
    if root is None:
        return []
    category_dir = root / category
    if not category_dir.is_dir():
        return []
    return sorted(p.name for p in category_dir.iterdir() if p.is_dir())


def load_model(ecosystem_root: Path, library: str, category: str, model_id: str) -> ModelInfo | None:
    """Every real part file in this model's own folder (non-recursive at
    the top level, but LumenPnP's own `parts/` subfolder is walked too,
    since that's where its 160 individual CAD parts actually live) plus
    its own `metadata.json`/`catalog.json` if present - never invents a
    part that isn't a real file on disk."""
    root = resolve_library_root(ecosystem_root, library)
    if root is None:
        return None
    model_dir = root / category / model_id
    if not model_dir.is_dir():
        return None

    parts: list[PartInfo] = []
    for mesh_path in sorted(model_dir.rglob("*")):
        if not mesh_path.is_file() or mesh_path.suffix.lower() not in MESH_EXTENSIONS:
            continue
        parts.append(PartInfo(
            filename=str(mesh_path.relative_to(model_dir)).replace("\\", "/"),
            size_bytes=mesh_path.stat().st_size,
            editable=mesh_path.suffix.lower() == ".stl",
        ))

    metadata = None
    for metadata_name in ("metadata.json", "catalog.json"):
        metadata_path = model_dir / metadata_name
        if metadata_path.is_file():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                metadata = None
            break

    return ModelInfo(library=library, category=category, model_id=model_id, path=model_dir, parts=tuple(parts), metadata=metadata)
