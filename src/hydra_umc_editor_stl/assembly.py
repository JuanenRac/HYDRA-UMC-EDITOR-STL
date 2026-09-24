# =============================================================================
# HYDRA-UMC-EDITOR-STL - Assembled (home-pose) view of a real machine: assembly.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# A robot/CNC/PnP/laser model's STL parts are each stored in their OWN
# local link frame - only that machine's forward kinematics puts them
# where they belong. This tool has no joint data of its own, and copying
# ~25 robots' worth of chains here would just create a second, drifting
# copy of data HYDRA-UMC-SUITE's own render/kinematics.py and
# render/pnp_rig.py already own (pure numpy, no Qt/GL). So this module
# READS that real data straight from the sibling HYDRA-UMC-SUITE checkout
# (same "sibling checkout under the ecosystem root" assumption
# model_catalog.py already makes) and only asks it "where does each link
# sit at its home pose?" - display only, nothing here ever writes to an
# STL. When SUITE isn't next to this checkout, or the model has no
# kinematics there, `assembled_transforms()` returns None and the viewer
# simply keeps showing the raw, unassembled parts.
# =============================================================================
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh

SUITE_DIRNAME = "HYDRA-UMC-SUITE"


@dataclass(frozen=True)
class PartPlacement:
    position: tuple[float, float, float]
    rotation_wxyz: tuple[float, float, float, float]


def _load_suite_modules(ecosystem_root: Path):
    suite_root = ecosystem_root / SUITE_DIRNAME
    if not (suite_root / "hydra_suite" / "render" / "kinematics.py").is_file():
        return None
    root_str = str(suite_root)
    if root_str not in sys.path:
        sys.path.append(root_str)
    try:
        from hydra_suite.render import kinematics, pnp_rig
    except Exception:
        return None
    return kinematics, pnp_rig


def _quaternion_wxyz(rotation: np.ndarray) -> tuple[float, float, float, float]:
    m = rotation
    trace = float(m[0, 0] + m[1, 1] + m[2, 2])
    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        return (0.25 / s, float((m[2, 1] - m[1, 2]) * s), float((m[0, 2] - m[2, 0]) * s), float((m[1, 0] - m[0, 1]) * s))
    if m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
        return (float((m[2, 1] - m[1, 2]) / s), 0.25 * s, float((m[0, 1] + m[1, 0]) / s), float((m[0, 2] + m[2, 0]) / s))
    if m[1, 1] > m[2, 2]:
        s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
        return (float((m[0, 2] - m[2, 0]) / s), float((m[0, 1] + m[1, 0]) / s), 0.25 * s, float((m[1, 2] + m[2, 1]) / s))
    s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
    return (float((m[1, 0] - m[0, 1]) / s), float((m[0, 2] + m[2, 0]) / s), float((m[1, 2] + m[2, 1]) / s), 0.25 * s)


def _mesh_is_millimeters(path: Path) -> bool:
    """Same mm-vs-m rule SUITE's own render/mesh.py and STUDIO's
    useRealScaleSTL() apply to these exact files (a span over 5 units is
    millimeters) - so the meter-based kinematics translations are scaled
    into whatever unit each STL was really authored in."""
    try:
        raw = stl_mesh.Mesh.from_file(str(path))
    except Exception:
        return False
    if len(raw.vectors) == 0:
        return False
    points = raw.vectors.reshape(-1, 3)
    return float(np.max(points.max(axis=0) - points.min(axis=0))) > 5.0


def _placement(matrix: np.ndarray, millimeters: bool) -> PartPlacement:
    scale = 1000.0 if millimeters else 1.0
    translation = (float(matrix[0, 3]) * scale, float(matrix[1, 3]) * scale, float(matrix[2, 3]) * scale)
    return PartPlacement(position=translation, rotation_wxyz=_quaternion_wxyz(matrix[:3, :3]))


def assembled_transforms(ecosystem_root: Path, category: str, model_id: str, model_dir: Path) -> dict[str, PartPlacement] | None:
    """`{part filename: PartPlacement}` for every part SUITE's own
    kinematics can place at the machine's home pose, or None when there
    is nothing to assemble (SUITE checkout missing, or an unknown
    model)."""
    modules = _load_suite_modules(ecosystem_root)
    if modules is None:
        return None
    kinematics, pnp_rig = modules
    relative_dir = f"{category}/{model_id}"

    placements: dict[str, PartPlacement] = {}

    for entry in kinematics.ROBOT_REGISTRY.values():
        if entry.mesh_dir != relative_dir:
            continue
        home = dict(entry.home_pose_deg)
        if entry.family == "ur":
            matrices = kinematics.ur_mesh_world_transforms(entry.chain, entry.mesh_offsets, home)
        elif entry.family == "quat":
            cfg = entry.quat_config
            matrices = kinematics.quat_family_mesh_world_transforms(cfg.chain, cfg.mesh_offsets, cfg.root_axis_target, cfg.base_offset, home)
        else:
            continue
        for link_name, matrix in zip(entry.link_names, matrices):
            filename = entry.mesh_files[link_name]
            part_path = model_dir / filename
            if part_path.is_file():
                placements[filename] = _placement(matrix, _mesh_is_millimeters(part_path))
        return placements or None

    if relative_dir in pnp_rig.MACHINE_MESH_DIRS.values():
        transforms = pnp_rig.pnp_world_link_transforms(0, 0, 0, 0, 0)
        for link_name in pnp_rig.PNP_LINK_NAMES:
            filename = pnp_rig.PNP_MESH_FILES[link_name]
            part_path = model_dir / filename
            if part_path.is_file():
                placements[filename] = _placement(transforms[link_name], _mesh_is_millimeters(part_path))
        for part_name, owner in pnp_rig.PNP_STATIC_PART_OWNER.items():
            filename = pnp_rig.PNP_STATIC_PART_FILES[part_name]
            part_path = model_dir / filename
            if part_path.is_file():
                placements[filename] = _placement(transforms[owner], _mesh_is_millimeters(part_path))
        return placements or None

    return None


def _rotation_matrix(wxyz: tuple[float, float, float, float]) -> np.ndarray:
    w, x, y, z = wxyz
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def assembled_bounds(model_dir: Path, placements: dict[str, PartPlacement]) -> tuple[tuple[float, float, float], tuple[float, float, float]] | None:
    """Combined world bounding box of every placed part (bbox corners
    pushed through each part's own placement) - what the camera frames on
    in the assembled view."""
    corners_all: list[np.ndarray] = []
    for filename, placement in placements.items():
        try:
            raw = stl_mesh.Mesh.from_file(str(model_dir / filename))
        except Exception:
            continue
        if len(raw.vectors) == 0:
            continue
        points = raw.vectors.reshape(-1, 3)
        lo, hi = points.min(axis=0), points.max(axis=0)
        corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        world = corners @ _rotation_matrix(placement.rotation_wxyz).T + np.array(placement.position)
        corners_all.append(world)
    if not corners_all:
        return None
    stacked = np.vstack(corners_all)
    return tuple(float(v) for v in stacked.min(axis=0)), tuple(float(v) for v in stacked.max(axis=0))
