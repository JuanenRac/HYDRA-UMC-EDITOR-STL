# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for qt_gui.py's EditorBridge
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

from hydra_umc_editor_stl.part_colors import DEFAULT_COLOR
from hydra_umc_editor_stl.qt_gui import EditorBridge


def _select_ar3_base_link(bridge: EditorBridge) -> None:
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")
    bridge.selectPart("base_link.STL")


def test_parts_carry_a_real_absolute_path_and_a_default_color(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")
    parts = {p["filename"]: p for p in bridge.parts}
    assert parts["base_link.STL"]["color"] == DEFAULT_COLOR
    assert Path(parts["base_link.STL"]["absolutePath"]).is_file()


def test_set_selected_part_color_persists_and_is_reflected_in_parts(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)

    bridge.setSelectedPartColor("#ff8800")

    parts = {p["filename"]: p for p in bridge.parts}
    assert parts["base_link.STL"]["color"] == "#ff8800"
    # The sibling part's own color must be untouched by this call.
    assert parts["link_1.STL"]["color"] == DEFAULT_COLOR


def test_set_selected_part_color_preserves_the_current_selection(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)

    bridge.setSelectedPartColor("#00ff88")

    assert bridge.selectedPart == "base_link.STL"


def test_set_selected_part_color_with_no_part_selected_reports_status_instead_of_crashing(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")

    bridge.setSelectedPartColor("#00ff88")  # no selectPart() call at all

    assert bridge.statusText  # some real, non-empty message was set, not a silent no-op


def test_copy_then_paste_adds_a_non_colliding_copy_of_the_part(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)
    assert not bridge.hasClipboard

    bridge.copySelectedPart()
    assert bridge.hasClipboard
    assert bridge.clipboardLabel == "base_link.STL"

    bridge.pasteClipboard()
    bridge.pasteClipboard()
    filenames = {p["filename"] for p in bridge.parts}
    assert {"base_link.STL", "base_link_copy.STL", "base_link_copy2.STL"} <= filenames


def test_cut_copies_then_moves_the_original_to_trash(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)

    bridge.cutSelectedPart()

    assert bridge.hasClipboard
    assert "base_link.STL" not in {p["filename"] for p in bridge.parts}
    bridge.pasteClipboard()
    assert "base_link.STL" in {p["filename"] for p in bridge.parts}


def test_paste_with_an_empty_clipboard_changes_nothing(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)
    before = {p["filename"] for p in bridge.parts}
    bridge.pasteClipboard()
    assert {p["filename"] for p in bridge.parts} == before


def test_independent_parts_categories_are_flagged_and_robots_are_not(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    assert not bridge.isIndependentPartsCategory
    for category in ("heatedbeds", "vacuum-tables", "racks"):
        bridge.selectCategory(category)
        assert bridge.isIndependentPartsCategory


def test_selected_part_center_is_the_real_center_of_that_part_only(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)
    # conftest's cube fixture spans 0..10 on every axis.
    assert bridge.selectedPartCenter == [5.0, 5.0, 5.0]
