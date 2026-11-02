# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the shared golden URDF set (tests/golden/)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# The same files are checked in the URDF editor and in the physics replica. Here
# the writer of the assembly URDF has to turn a rotation into the rpy that a
# reader of those files turns back into the same rotation.
# =============================================================================
from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

from hydra_umc_editor_stl.assembly import PartPlacement
from hydra_umc_editor_stl.assembly import _quaternion_wxyz as quaternion_wxyz
from hydra_umc_editor_stl.catalog_push import build_assembly_urdf
from hydra_umc_editor_stl.model_catalog import ModelInfo, PartInfo

GOLDEN = Path(__file__).resolve().parent / "golden"
ROTATIONS = json.loads((GOLDEN / "rotations.json").read_text(encoding="utf-8"))


def _rpy_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Rz(yaw) Ry(pitch) Rx(roll), written out here so the check does not lean on the code under test."""
    cr, sr, cp, sp, cy, sy = np.cos(roll), np.sin(roll), np.cos(pitch), np.sin(pitch), np.cos(yaw), np.sin(yaw)
    return np.array(
        [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr],
        ]
    )


@pytest.mark.parametrize("entry", ROTATIONS["rotations"], ids=lambda e: "-".join(f"{v:.2f}" for v in e["rpy"]))
def test_a_placement_is_written_as_the_rpy_that_reads_back_to_the_same_rotation(tmp_path: Path, entry) -> None:
    matrix = np.array(entry["matrix"])
    part = PartInfo(filename="a.stl", size_bytes=10, editable=True)
    (tmp_path / "a.stl").write_bytes(b"fake stl bytes")
    model = ModelInfo(library="studio", category="heatedbeds", model_id="default", path=tmp_path, parts=(part,))
    placement = PartPlacement(position=(0.0, 0.0, 0.0), rotation_wxyz=quaternion_wxyz(matrix))
    origin = ET.fromstring(build_assembly_urdf(model, {"a.stl": placement})).find("joint").find("origin")
    assert origin is not None
    rpy = [float(v) for v in origin.get("rpy").split()]
    assert np.allclose(_rpy_matrix(*rpy), matrix, atol=ROTATIONS["tolerance"] * 10)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_the_golden_files_are_the_ones_listed_in_the_manifest() -> None:
    listed = dict(reversed(line.split("  ", 1)) for line in (GOLDEN / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines())
    on_disk = {p.relative_to(GOLDEN).as_posix() for p in GOLDEN.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"}
    assert set(listed) == on_disk
    for name, digest in listed.items():
        assert _digest(GOLDEN / name) == digest, name
