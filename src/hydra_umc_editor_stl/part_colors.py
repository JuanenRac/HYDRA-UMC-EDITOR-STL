# =============================================================================
# HYDRA-UMC-EDITOR-STL - Per-part color annotations: part_colors.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# A binary STL carries no reliable per-part color of its own - the only
# real convention (a VisCAM/SolidView-style header, or a per-facet RGB555
# byte hijacking the "attribute byte count" field) is a fragile hack most
# STL consumers, including this ecosystem's own Three.js-based viewers in
# HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE, do not interpret at all - writing one
# into the mesh file itself would change nothing about how it actually
# renders anywhere real. Real color here is therefore stored as this
# tool's own sidecar `part_colors.json`, one per model folder, next to
# the parts it describes - never inside metadata.json (owned by
# STUDIO/SUITE's own catalog contract, not something this tool invents
# new fields into) and never inside the STL bytes themselves. Not just an
# EDITOR-STL-only preview: HYDRA-UMC-STUDIO's own hooks/usePartColors.ts
# and HYDRA-UMC-SUITE's own render/part_colors.py both read this exact
# same file back into their own live 3D viewers.
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path

COLORS_FILENAME = "part_colors.json"
DEFAULT_COLOR = "#9fb4c9"  # the same neutral slate this app's own theme already uses for chrome


def load_part_colors(model_dir: Path) -> dict[str, str]:
    """Real, on-disk colors for this model's own parts - `{}` (never an
    error) if the sidecar file doesn't exist yet or fails to parse, since
    "no colors saved yet" is a normal, honest starting state, not a
    failure."""
    path = model_dir / COLORS_FILENAME
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}


def save_part_color(model_dir: Path, filename: str, hex_color: str) -> None:
    """Sets (or clears, when `hex_color` is falsy) one real part's own
    saved color and writes the whole sidecar file back - small enough
    (one entry per real part in a model) that a full read-modify-write is
    simpler and safer than a partial/streaming update."""
    colors = load_part_colors(model_dir)
    if hex_color:
        colors[filename] = hex_color
    else:
        colors.pop(filename, None)
    path = model_dir / COLORS_FILENAME
    path.write_text(json.dumps(colors, indent=2, sort_keys=True), encoding="utf-8")
