# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for stl_ops.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl.stl_ops import (
    StlOpsError,
    add_part,
    is_real_stl,
    remove_part,
    replace_part,
    transform_part,
)

from .conftest import make_cube_stl


def test_is_real_stl_true_for_a_real_file(tmp_path: Path) -> None:
    cube = tmp_path / "cube.stl"
    make_cube_stl(cube, size=5.0)
    assert is_real_stl(cube) is True


def test_is_real_stl_false_for_garbage_bytes(tmp_path: Path) -> None:
    fake = tmp_path / "fake.stl"
    fake.write_bytes(b"this is not a real STL file at all, just bytes")
    assert is_real_stl(fake) is False


def test_transform_part_translate_moves_the_bounding_box(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl", size=10.0)
    bbox = transform_part(tmp_path, "part.stl", translate_mm=(5.0, 0.0, 0.0))
    assert bbox.min_xyz[0] == pytest.approx(5.0, abs=0.01)
    assert bbox.max_xyz[0] == pytest.approx(15.0, abs=0.01)
    # untouched axes stay untouched
    assert bbox.min_xyz[1] == pytest.approx(0.0, abs=0.01)
    assert bbox.max_xyz[1] == pytest.approx(10.0, abs=0.01)


def test_transform_part_scale_grows_the_bounding_box(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl", size=10.0)
    bbox = transform_part(tmp_path, "part.stl", scale=2.0)
    assert bbox.max_xyz[0] == pytest.approx(20.0, abs=0.01)
    assert bbox.max_xyz[1] == pytest.approx(20.0, abs=0.01)
    assert bbox.max_xyz[2] == pytest.approx(20.0, abs=0.01)


def test_transform_part_rejects_zero_or_negative_scale(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl")
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "part.stl", scale=0.0)
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "part.stl", scale=-1.0)


def test_transform_part_backs_up_the_original_before_writing(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl", size=10.0)
    transform_part(tmp_path, "part.stl", translate_mm=(1.0, 0.0, 0.0))
    trash_files = list((tmp_path / ".trash").glob("*part.stl"))
    assert len(trash_files) == 1
    original = stl_mesh.Mesh.from_file(str(trash_files[0]))
    assert original.points.reshape(-1, 3).min(axis=0)[0] == pytest.approx(0.0, abs=0.01)


def test_transform_part_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(StlOpsError):
        transform_part(tmp_path, "does-not-exist.stl")


def test_replace_part_overwrites_and_backs_up_original(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl", size=10.0)
    replacement = tmp_path / "replacement.stl"
    make_cube_stl(replacement, size=99.0)

    replace_part(tmp_path, "part.stl", replacement)

    replaced = stl_mesh.Mesh.from_file(str(tmp_path / "part.stl"))
    assert replaced.points.reshape(-1, 3).max() == pytest.approx(99.0, abs=0.01)
    trash_files = list((tmp_path / ".trash").glob("*part.stl"))
    assert len(trash_files) == 1


def test_replace_part_rejects_a_non_stl_source(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl")
    bad_source = tmp_path / "bad.stl"
    bad_source.write_bytes(b"not a real stl")
    with pytest.raises(StlOpsError):
        replace_part(tmp_path, "part.stl", bad_source)
    # the real target must be untouched after a rejected replacement
    assert is_real_stl(tmp_path / "part.stl")


def test_remove_part_moves_to_trash_not_deletes(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl")
    destination = remove_part(tmp_path, "part.stl")
    assert not (tmp_path / "part.stl").exists()
    assert destination.is_file()
    assert destination.parent.name == ".trash"


def test_remove_part_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(StlOpsError):
        remove_part(tmp_path, "does-not-exist.stl")


def test_add_part_copies_a_real_stl_under_its_own_name(tmp_path: Path) -> None:
    source = tmp_path / "outside" / "new_part.stl"
    make_cube_stl(source, size=3.0)
    filename = add_part(tmp_path, source)
    assert filename == "new_part.stl"
    assert is_real_stl(tmp_path / "new_part.stl")


def test_add_part_supports_a_custom_destination_filename(tmp_path: Path) -> None:
    source = tmp_path / "outside" / "new_part.stl"
    make_cube_stl(source)
    filename = add_part(tmp_path, source, dest_filename="renamed.stl")
    assert filename == "renamed.stl"
    assert (tmp_path / "renamed.stl").is_file()


def test_add_part_refuses_to_silently_overwrite_an_existing_part(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "part.stl")
    source = tmp_path / "outside" / "part.stl"
    make_cube_stl(source, size=50.0)
    with pytest.raises(StlOpsError):
        add_part(tmp_path, source, dest_filename="part.stl")
    # untouched - still the original 10mm cube, not the 50mm replacement
    original = stl_mesh.Mesh.from_file(str(tmp_path / "part.stl"))
    assert original.points.reshape(-1, 3).max() < 20.0


def test_add_part_rejects_a_non_stl_source(tmp_path: Path) -> None:
    bad_source = tmp_path / "bad.stl"
    bad_source.write_bytes(b"not a real stl")
    with pytest.raises(StlOpsError):
        add_part(tmp_path, bad_source)
