# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for stl_ops.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl.stl_ops import (
    StlOpsError,
    add_part,
    model_bounds,
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


def test_model_bounds_unions_every_real_part_given(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=5.0)  # (0,0,0) - (5,5,5)
    b = stl_mesh.Mesh.from_file(str(tmp_path / "a.stl"))
    b.translate([10.0, 0.0, 0.0])
    b.save(str(tmp_path / "b.stl"))  # (10,0,0) - (15,5,5)
    box = model_bounds(tmp_path, ["a.stl", "b.stl"])
    assert box is not None
    assert box.min_xyz == (0.0, 0.0, 0.0)
    assert box.max_xyz == (15.0, 5.0, 5.0)


def test_model_bounds_skips_an_unreadable_part_instead_of_raising(tmp_path: Path) -> None:
    make_cube_stl(tmp_path / "a.stl", size=5.0)
    box = model_bounds(tmp_path, ["a.stl", "missing.stl"])
    assert box is not None
    assert box.min_xyz == (0.0, 0.0, 0.0)
    assert box.max_xyz == (5.0, 5.0, 5.0)


def test_model_bounds_returns_none_when_nothing_could_be_loaded(tmp_path: Path) -> None:
    assert model_bounds(tmp_path, ["missing.stl"]) is None


def test_model_bounds_returns_none_for_an_empty_part_list(tmp_path: Path) -> None:
    assert model_bounds(tmp_path, []) is None


# ---- the cache of bounding boxes (a part is measured once until it changes) ------------------------------------

def _count_reads(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    reads: list[str] = []
    original = stl_mesh.Mesh.from_file

    def counting(path, *args, **kwargs):
        reads.append(str(path))
        return original(path, *args, **kwargs)

    monkeypatch.setattr(stl_mesh.Mesh, "from_file", staticmethod(counting))
    return reads


def test_a_part_is_measured_once_however_many_times_the_model_is_selected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hydra_umc_editor_stl.stl_ops import clear_box_cache, part_box

    clear_box_cache()
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    make_cube_stl(tmp_path / "b.stl", size=20.0)
    reads = _count_reads(monkeypatch)
    first = model_bounds(tmp_path, ["a.stl", "b.stl"])
    second = model_bounds(tmp_path, ["a.stl", "b.stl"])
    third = model_bounds(tmp_path, ["b.stl"])
    assert first == second
    assert third is not None and third.max_xyz == (20.0, 20.0, 20.0)
    assert len(reads) == 2, "each part was parsed once"
    assert part_box(tmp_path / "a.stl") == part_box(tmp_path / "a.stl")
    assert len(reads) == 2


def test_a_part_that_changes_is_measured_again(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hydra_umc_editor_stl.stl_ops import clear_box_cache

    clear_box_cache()
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    reads = _count_reads(monkeypatch)
    before = model_bounds(tmp_path, ["a.stl"])
    assert before is not None and before.max_xyz == (10.0, 10.0, 10.0)
    make_cube_stl(tmp_path / "a.stl", size=30.0)  # another size on disk
    after = model_bounds(tmp_path, ["a.stl"])
    assert after is not None and after.max_xyz == (30.0, 30.0, 30.0)
    assert len(reads) == 2


def test_an_edit_made_by_this_tool_is_seen_by_the_next_measure(tmp_path: Path) -> None:
    from hydra_umc_editor_stl.stl_ops import clear_box_cache

    clear_box_cache()
    make_cube_stl(tmp_path / "a.stl", size=10.0)
    assert model_bounds(tmp_path, ["a.stl"]).min_xyz == (0.0, 0.0, 0.0)  # type: ignore[union-attr]
    transform_part(tmp_path, "a.stl", translate_mm=(5.0, 0.0, 0.0))
    assert model_bounds(tmp_path, ["a.stl"]).min_xyz == (5.0, 0.0, 0.0)  # type: ignore[union-attr]


def test_an_unreadable_part_is_skipped_and_tried_again_when_it_changes(tmp_path: Path) -> None:
    from hydra_umc_editor_stl.stl_ops import clear_box_cache

    clear_box_cache()
    (tmp_path / "bad.stl").write_bytes(b"not an stl")
    make_cube_stl(tmp_path / "ok.stl", size=4.0)
    assert model_bounds(tmp_path, ["bad.stl", "missing.stl"]) is None
    box = model_bounds(tmp_path, ["bad.stl", "ok.stl"])
    assert box is not None and box.max_xyz == (4.0, 4.0, 4.0)
    make_cube_stl(tmp_path / "bad.stl", size=9.0)  # the damaged part was replaced by a good one
    fixed = model_bounds(tmp_path, ["bad.stl", "ok.stl"])
    assert fixed is not None and fixed.max_xyz == (9.0, 9.0, 9.0)


def test_the_cache_does_not_grow_without_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hydra_umc_editor_stl import stl_ops

    stl_ops.clear_box_cache()
    monkeypatch.setattr(stl_ops, "_BOX_CACHE_LIMIT", 3)
    for i in range(8):
        make_cube_stl(tmp_path / f"p{i}.stl", size=float(i + 1))
        assert stl_ops.part_box(tmp_path / f"p{i}.stl").max_xyz == (float(i + 1),) * 3  # type: ignore[union-attr]
    assert len(stl_ops._box_cache) == 3, "the oldest answers were dropped"
    # a dropped answer is simply measured again
    assert stl_ops.part_box(tmp_path / "p0.stl").max_xyz == (1.0, 1.0, 1.0)  # type: ignore[union-attr]


def test_trash_list_restore_and_empty(tmp_path: Path) -> None:
    from hydra_umc_editor_stl.stl_ops import empty_trash, list_trash, restore_from_trash

    make_cube_stl(tmp_path / "a.stl", size=5.0)
    remove_part(tmp_path, "a.stl")
    assert not (tmp_path / "a.stl").exists()
    entries = list_trash(tmp_path)
    assert [e["original"] for e in entries] == ["a.stl"]
    # the name is taken again meanwhile: restoring never overwrites it
    make_cube_stl(tmp_path / "a.stl", size=7.0)
    restored = restore_from_trash(tmp_path, entries[0]["entry"])
    assert restored == "a_copy.stl" and (tmp_path / restored).is_file()
    assert list_trash(tmp_path) == []
    with pytest.raises(StlOpsError):
        restore_from_trash(tmp_path, "../x")
    remove_part(tmp_path, "a.stl")
    with pytest.raises(StlOpsError):
        empty_trash(tmp_path, confirmed=False)
    assert empty_trash(tmp_path, confirmed=True) == 1
    assert list_trash(tmp_path) == []
    assert len(list((tmp_path / ".trash-emptied").rglob("*a.stl"))) == 1
