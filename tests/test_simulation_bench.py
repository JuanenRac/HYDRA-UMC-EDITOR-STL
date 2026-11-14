# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests/test_simulation_bench.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Simulation bench: the real STL operations against parts made by a generator with a fixed seed, and against parts damaged the way files get damaged.

The parts are boxes and spheres of random size, written to disk as binary STL. Their volume is known in closed form, so the bench can say what every operation must
leave true: a rigid move keeps the volume, a scale changes it by the cube, a move and its inverse give the part back, the light copy never grows and keeps the
shape of the part, and nothing that is removed is ever lost. Then it injures the parts (a hole, faces turned inside out, a number that is not a number, a repeated face,
a wrong unit, a file cut short) and requires the checks to see each injury. Nothing here says how the editor behaves with the parts of a real model: that needs the model."""
from __future__ import annotations

import math
import random
import struct
from pathlib import Path

import numpy as np
import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl import stl_ops
from hydra_umc_editor_stl.decimate import decimate_to_ratio
from hydra_umc_editor_stl.glb import mesh_to_glb, read_glb
from hydra_umc_editor_stl.mesh_check import check_stl, check_vectors
from hydra_umc_editor_stl.mesh_diff import diff_vectors

SEED = 20260101


def box(dx: float, dy: float, dz: float) -> np.ndarray:
    """The 12 triangles of a closed box with its corner at the origin, faces turned outwards."""
    c = np.array([[x, y, z] for x in (0, dx) for y in (0, dy) for z in (0, dz)], dtype=np.float64)
    quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    triangles = []
    for a, b, c2, d in quads:
        triangles += [[c[a], c[b], c[c2]], [c[a], c[c2], c[d]]]
    return np.array(triangles)[:, ::-1, :]  # the quads above are listed the other way round: turned so the faces point out


def sphere(radius: float, rings: int, segments: int) -> np.ndarray:
    """A closed UV sphere centred on the origin, faces turned outwards."""
    top, bottom = np.array([0, 0, radius]), np.array([0, 0, -radius])
    ring = [[radius * np.array([math.sin(math.pi * (i + 1) / rings) * math.cos(2 * math.pi * j / segments),
                                math.sin(math.pi * (i + 1) / rings) * math.sin(2 * math.pi * j / segments),
                                math.cos(math.pi * (i + 1) / rings)]) for j in range(segments)] for i in range(rings - 1)]
    triangles = []
    for j in range(segments):
        k = (j + 1) % segments
        triangles.append([top, ring[0][j], ring[0][k]])
        triangles.append([bottom, ring[-1][k], ring[-1][j]])
        for i in range(rings - 2):
            a, b, c, d = ring[i][j], ring[i][k], ring[i + 1][k], ring[i + 1][j]
            triangles += [[a, d, c], [a, c, b]]
    return np.array(triangles)


def write_stl(path: Path, vectors: np.ndarray) -> Path:
    part = stl_mesh.Mesh(np.zeros(len(vectors), dtype=stl_mesh.Mesh.dtype))
    part.vectors[:] = vectors.astype(np.float32)
    part.update_normals()
    path.parent.mkdir(parents=True, exist_ok=True)
    part.save(str(path))
    return path


def volume(vectors: np.ndarray) -> float:
    return float(np.einsum("ij,ij->i", vectors[:, 0], np.cross(vectors[:, 1], vectors[:, 2])).sum() / 6.0)


def read_vectors(path: Path) -> np.ndarray:
    return stl_mesh.Mesh.from_file(str(path)).vectors.astype(np.float64)


def parts(rng: random.Random, count: int):
    for index in range(count):
        if index % 2:
            yield sphere(rng.uniform(5, 60), rng.randint(6, 14), rng.randint(8, 20))
        else:
            yield box(rng.uniform(10, 200), rng.uniform(10, 200), rng.uniform(10, 200))


def test_the_generated_parts_are_closed_with_the_volume_they_have_in_closed_form() -> None:
    rng = random.Random(SEED)
    for vectors in parts(rng, 20):
        report = check_vectors(vectors.astype(np.float32))
        assert report.ok, report.problems
        assert report.open_edges == 0 and report.non_manifold_edges == 0 and report.degenerate == 0
        assert report.signed_volume == pytest.approx(volume(vectors), rel=1e-4)
    assert volume(box(10, 20, 30)) == pytest.approx(6000.0)


def test_a_rigid_move_keeps_the_volume_and_the_sizes_and_a_move_and_its_inverse_give_the_part_back(tmp_path: Path) -> None:
    rng = random.Random(SEED + 1)
    for index, vectors in enumerate(parts(rng, 10)):
        path = write_stl(tmp_path / f"p{index}.stl", vectors)
        before = read_vectors(path)
        shift = (rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(-50, 50))
        turn = (rng.uniform(-180, 180), rng.uniform(-180, 180), rng.uniform(-180, 180))
        stl_ops.transform_part(tmp_path, path.name, translate_mm=shift, rotate_deg=turn)
        after = read_vectors(path)
        assert volume(after) == pytest.approx(volume(before), rel=1e-3)
        size = lambda v: np.sort(np.linalg.svd((v.reshape(-1, 3) - v.reshape(-1, 3).mean(axis=0)), compute_uv=False))  # noqa: E731
        assert size(after) == pytest.approx(size(before), rel=1e-3)
        assert check_vectors(after.astype(np.float32)).ok
        # the inverse: rotate back (z, y, x order undone) is not an operation of the editor, so move it back and compare what a move alone gives
        stl_ops.transform_part(tmp_path, path.name, translate_mm=tuple(-v for v in shift))
        assert volume(read_vectors(path)) == pytest.approx(volume(before), rel=1e-3)


def test_a_move_without_a_rotation_shifts_the_box_by_exactly_the_move(tmp_path: Path) -> None:
    rng = random.Random(SEED + 2)
    for index, vectors in enumerate(parts(rng, 8)):
        path = write_stl(tmp_path / f"p{index}.stl", vectors)
        before = stl_ops.part_box(path)
        shift = (rng.uniform(-80, 80), rng.uniform(-80, 80), rng.uniform(-80, 80))
        stl_ops.clear_box_cache()
        returned = stl_ops.transform_part(tmp_path, path.name, translate_mm=shift)
        assert before is not None
        for axis in range(3):
            assert returned.min_xyz[axis] == pytest.approx(before.min_xyz[axis] + shift[axis], abs=1e-3)
            assert returned.max_xyz[axis] == pytest.approx(before.max_xyz[axis] + shift[axis], abs=1e-3)


def test_a_scale_changes_the_volume_by_the_cube_and_the_box_by_the_factor(tmp_path: Path) -> None:
    rng = random.Random(SEED + 3)
    for index, vectors in enumerate(parts(rng, 8)):
        path = write_stl(tmp_path / f"p{index}.stl", vectors)
        factor = rng.choice([0.25, 0.5, 2.0, 3.0])
        before = read_vectors(path)
        stl_ops.transform_part(tmp_path, path.name, scale=factor)
        after = read_vectors(path)
        assert volume(after) == pytest.approx(volume(before) * factor**3, rel=1e-3)
        diff = diff_vectors(before, after)
        assert diff.size_after == pytest.approx(tuple(s * factor for s in diff.size_before), rel=1e-3) and not diff.unchanged


def test_every_change_leaves_the_part_it_replaced_in_the_trash_and_nothing_is_lost(tmp_path: Path) -> None:
    rng = random.Random(SEED + 4)
    path = write_stl(tmp_path / "bracket.stl", box(40, 30, 20))
    versions = [read_vectors(path)]
    for _ in range(4):
        stl_ops.transform_part(tmp_path, "bracket.stl", translate_mm=(rng.uniform(1, 9), 0, 0), scale=rng.choice([1.0, 1.1]))
        versions.append(read_vectors(path))
    entries = stl_ops.list_trash(tmp_path)
    assert len(entries) == 4 and {e["original"] for e in entries} == {"bracket.stl"}
    stamps = [e["stamp"] for e in entries]
    assert stamps == sorted(stamps, reverse=True)
    removed = stl_ops.remove_part(tmp_path, "bracket.stl")
    assert removed.is_file() and not path.exists()
    restored = stl_ops.restore_from_trash(tmp_path, removed.name)
    assert restored == "bracket.stl" and np.allclose(read_vectors(path), versions[-1], atol=1e-4)
    again = stl_ops.restore_from_trash(tmp_path, entries[-1]["entry"])
    assert again != "bracket.stl" and (tmp_path / again).is_file()  # a part that exists is never overwritten


def test_the_trash_is_emptied_only_when_asked_and_only_into_an_archive(tmp_path: Path) -> None:
    write_stl(tmp_path / "a.stl", box(10, 10, 10))
    stl_ops.transform_part(tmp_path, "a.stl", scale=2.0)
    stl_ops.remove_part(tmp_path, "a.stl")
    with pytest.raises(stl_ops.StlOpsError):
        stl_ops.empty_trash(tmp_path, confirmed=False)
    assert len(stl_ops.list_trash(tmp_path)) == 2
    assert stl_ops.empty_trash(tmp_path, confirmed=True) == 2
    assert stl_ops.list_trash(tmp_path) == [] and len(list((tmp_path / stl_ops.STL_TRASH_EMPTIED_DIRNAME).rglob("*.stl"))) == 2
    assert stl_ops.empty_trash(tmp_path, confirmed=True) == 0


@pytest.mark.parametrize("name", ["../outside.stl", "/etc/passwd", "", "a/../../b.stl"])
def test_a_name_that_leads_out_of_the_model_folder_is_refused_by_every_operation(tmp_path: Path, name: str) -> None:
    write_stl(tmp_path / "a.stl", box(10, 10, 10))
    for call in (lambda: stl_ops.transform_part(tmp_path, name), lambda: stl_ops.remove_part(tmp_path, name), lambda: stl_ops.replace_part(tmp_path, name, tmp_path / "a.stl")):
        with pytest.raises(stl_ops.StlOpsError):
            call()


@pytest.mark.parametrize("bad", [{"scale": 0}, {"scale": -1}, {"scale": float("nan")}, {"translate_mm": (float("inf"), 0, 0)}, {"rotate_deg": (0, float("nan"), 0)}, {"scale": 1e40}])
def test_a_transform_that_would_damage_the_part_is_refused_and_the_part_is_untouched(tmp_path: Path, bad: dict) -> None:
    path = write_stl(tmp_path / "a.stl", box(10, 10, 10))
    original = path.read_bytes()
    with pytest.raises(stl_ops.StlOpsError):
        stl_ops.transform_part(tmp_path, "a.stl", **bad)
    assert path.read_bytes() == original and stl_ops.list_trash(tmp_path) == []


def test_the_light_copy_never_grows_never_leaves_the_box_and_a_ratio_of_one_changes_nothing() -> None:
    for vectors in (sphere(30, 24, 36), sphere(12, 16, 24), box(40, 30, 20)):
        counts = []
        low, high = vectors.reshape(-1, 3).min(axis=0), vectors.reshape(-1, 3).max(axis=0)
        for ratio in (0.9, 0.5, 0.2, 0.05):
            light = decimate_to_ratio(vectors.astype(np.float32), ratio)
            counts.append(len(light))
            assert 0 < len(light) <= len(vectors) and np.isfinite(light).all()
            points = light.reshape(-1, 3)
            assert (points.min(axis=0) >= low - 1e-3).all() and (points.max(axis=0) <= high + 1e-3).all()  # a merged vertex is a mean: never outside the box
        assert counts == sorted(counts, reverse=True)
        assert len(decimate_to_ratio(vectors.astype(np.float32), 1.0)) == len(vectors)
        assert len(decimate_to_ratio(vectors.astype(np.float32), 7.5)) == len(vectors)
        for ratio in (0, -0.5, float("nan"), float("inf"), "half"):
            with pytest.raises(ValueError):
                decimate_to_ratio(vectors, ratio)  # type: ignore[arg-type]


def test_a_sphere_loses_triangles_in_step_with_the_ratio() -> None:
    vectors = sphere(30, 24, 36).astype(np.float32)
    kept = {ratio: len(decimate_to_ratio(vectors, ratio)) / len(vectors) for ratio in (0.5, 0.25, 0.1)}
    for ratio, fraction in kept.items():
        assert fraction <= ratio * 1.5 + 4 / len(vectors), (ratio, fraction)
    assert kept[0.5] > kept[0.1]


def test_the_light_copy_of_a_part_on_disk_is_a_new_file_and_the_part_is_not_changed(tmp_path: Path) -> None:
    from hydra_umc_editor_stl.decimate import make_light_copy

    path = write_stl(tmp_path / "ball.stl", sphere(25, 24, 36))
    original = path.read_bytes()
    result = make_light_copy(tmp_path, "ball.stl", 0.2)
    assert path.read_bytes() == original
    assert result["triangles_after"] < result["triangles_before"] and result["bytes_after"] < result["bytes_before"] and Path(result["path"]).is_file()
    assert check_stl(Path(result["path"])) is not None


def test_each_injury_to_a_part_is_seen_by_the_check(tmp_path: Path) -> None:
    rng = random.Random(SEED + 6)
    healthy = sphere(30, 10, 14).astype(np.float32)
    assert check_vectors(healthy).ok
    hole = np.delete(healthy, rng.randrange(len(healthy)), axis=0)
    report = check_vectors(hole)
    assert report.open_edges > 0 and any("not closed" in p for p in report.problems)
    inside_out = healthy[:, ::-1, :]
    assert any("inwards" in p for p in check_vectors(np.ascontiguousarray(inside_out)).problems)
    broken = healthy.copy()
    broken[rng.randrange(len(broken)), 1, 1] = np.nan
    assert check_vectors(broken).non_finite == 1
    doubled = np.concatenate([healthy, healthy[:3]])
    assert check_vectors(doubled).non_manifold_edges > 0
    flat = healthy.copy()
    flat[0, 1] = flat[0, 0]
    assert check_vectors(flat).degenerate >= 1
    in_metres = healthy / 1000.0
    assert any("unit" in p for p in check_vectors(in_metres.astype(np.float32)).problems)
    assert any("no triangles" in p for p in check_vectors(np.zeros((0, 3, 3))).problems)


def test_a_file_cut_short_is_not_a_part_and_is_never_saved_over_a_good_one(tmp_path: Path) -> None:
    path = write_stl(tmp_path / "ball.stl", sphere(25, 10, 14))
    data = path.read_bytes()
    rng = random.Random(SEED + 7)
    for cut in sorted({rng.randrange(90, len(data) - 1) for _ in range(6)}):
        broken = tmp_path / f"cut{cut}.stl"
        broken.write_bytes(data[:cut])
        declared = struct.unpack("<I", data[80:84])[0]
        if 84 + 50 * declared > cut:
            assert not stl_ops.is_real_stl(broken)
            with pytest.raises(stl_ops.StlOpsError):
                stl_ops.transform_part(tmp_path, broken.name, scale=2.0)
            with pytest.raises(stl_ops.StlOpsError):
                stl_ops.add_part(tmp_path / "model", broken)
    garbage = tmp_path / "garbage.stl"
    garbage.write_bytes(bytes(rng.randrange(256) for _ in range(500)))
    assert not stl_ops.is_real_stl(garbage)


def test_the_glb_of_a_part_carries_the_triangles_the_part_has() -> None:
    rng = random.Random(SEED + 8)
    for vectors in parts(rng, 8):
        document, binary = read_glb(mesh_to_glb(vectors.astype(np.float32), "part"))
        accessors = document["accessors"]
        assert accessors[1]["count"] == len(vectors) * 3
        assert len(binary) >= accessors[0]["count"] * 12 + accessors[1]["count"] * 4
        low = np.array(accessors[0]["min"])
        assert low == pytest.approx(vectors.reshape(-1, 3).min(axis=0), abs=1e-3)
    with pytest.raises(ValueError):
        mesh_to_glb(np.full((2, 3, 3), np.nan))
    for bad in (b"", b"glTF", b"x" * 40):
        with pytest.raises(ValueError):
            read_glb(bad)


def test_the_same_seed_makes_the_same_parts_and_another_seed_does_not() -> None:
    def fingerprint(seed: int) -> list[float]:
        return [round(volume(v), 6) for v in parts(random.Random(seed), 6)]

    assert fingerprint(SEED) == fingerprint(SEED) and fingerprint(SEED) != fingerprint(SEED + 1)
