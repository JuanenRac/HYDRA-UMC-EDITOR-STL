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
