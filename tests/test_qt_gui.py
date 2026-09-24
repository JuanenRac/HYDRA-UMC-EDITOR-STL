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


def test_no_suite_checkout_means_no_assembly_and_raw_parts(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _select_ar3_base_link(bridge)
    assert not bridge.hasAssembly
    assert bridge.parts[0]["asmMatrix"] == []


def test_real_suite_kinematics_place_a_robot_and_the_toggle_reframes(qt_app) -> None:
    import pytest

    real_root = Path(__file__).resolve().parents[2]
    if not (real_root / "HYDRA-UMC-SUITE" / "hydra_suite" / "render" / "kinematics.py").is_file() \
            or not (real_root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ur5e").is_dir():
        pytest.skip("needs the sibling HYDRA-UMC-SUITE/HYDRA-UMC-STUDIO checkouts")
    bridge = EditorBridge(real_root)
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ur5e")
    assert bridge.hasAssembly and bridge.assembledView
    positions = {tuple(p["asmMatrix"][9:]) for p in bridge.parts if p["editable"]}
    assert len(positions) > 1  # links are no longer all stacked at the origin
    bridge.setAssembledView(False)
    assert not bridge.assembledView


def test_placement_matrix_is_rotation_then_translation() -> None:
    from hydra_umc_editor_stl.assembly import PartPlacement, placement_matrix

    quarter_turn_about_x = (0.7071067811865476, 0.7071067811865476, 0.0, 0.0)
    matrix = placement_matrix(PartPlacement((1.0, 2.0, 3.0), quarter_turn_about_x))
    assert matrix[9:] == [1.0, 2.0, 3.0]
    # +90 deg about X sends local +Y to world +Z and local +Z to world -Y.
    rotation = [[round(matrix[r * 3 + c], 6) for c in range(3)] for r in range(3)]
    assert rotation == [[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]]
