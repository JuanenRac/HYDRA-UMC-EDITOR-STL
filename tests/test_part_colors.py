# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for part_colors.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

from hydra_umc_editor_stl.part_colors import load_part_colors, save_part_color


def test_load_part_colors_is_empty_for_a_model_with_no_sidecar_yet(tmp_path: Path) -> None:
    assert load_part_colors(tmp_path) == {}


def test_save_then_load_round_trips_a_real_color(tmp_path: Path) -> None:
    save_part_color(tmp_path, "link1.stl", "#ff0000")
    assert load_part_colors(tmp_path) == {"link1.stl": "#ff0000"}


def test_save_part_color_preserves_other_real_parts_own_colors(tmp_path: Path) -> None:
    save_part_color(tmp_path, "link1.stl", "#ff0000")
    save_part_color(tmp_path, "link2.stl", "#00ff00")
    assert load_part_colors(tmp_path) == {"link1.stl": "#ff0000", "link2.stl": "#00ff00"}


def test_save_part_color_with_a_falsy_color_clears_that_part_only(tmp_path: Path) -> None:
    save_part_color(tmp_path, "link1.stl", "#ff0000")
    save_part_color(tmp_path, "link2.stl", "#00ff00")
    save_part_color(tmp_path, "link1.stl", "")
    assert load_part_colors(tmp_path) == {"link2.stl": "#00ff00"}


def test_load_part_colors_tolerates_a_corrupt_sidecar_file(tmp_path: Path) -> None:
    (tmp_path / "part_colors.json").write_text("{not valid json", encoding="utf-8")
    assert load_part_colors(tmp_path) == {}


def test_load_part_colors_tolerates_a_sidecar_file_that_is_not_a_json_object(tmp_path: Path) -> None:
    (tmp_path / "part_colors.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert load_part_colors(tmp_path) == {}


def test_save_part_color_overwrites_an_existing_saved_color(tmp_path: Path) -> None:
    save_part_color(tmp_path, "link1.stl", "#ff0000")
    save_part_color(tmp_path, "link1.stl", "#0000ff")
    assert load_part_colors(tmp_path) == {"link1.stl": "#0000ff"}
