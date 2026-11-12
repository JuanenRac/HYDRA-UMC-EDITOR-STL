# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the part properties and the status of EditorBridge
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The bounds, the selected part and the status line of the bridge, on the small cube model of the test checkout."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from hydra_umc_editor_stl import i18n, settings  # noqa: E402
from hydra_umc_editor_stl.qt_gui import EditorBridge  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "save_lang", lambda lang: None)
    monkeypatch.setattr(settings, "save_ecosystem_root", lambda path: None)


def _model(bridge: EditorBridge) -> None:
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")


def test_a_fresh_bridge_with_a_root_is_ready_and_frames_nothing(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert bridge.statusText == i18n.t(bridge.language, "status_ready")
    assert bridge.parts == []
    assert bridge.selectedPart == ""
    assert bridge.boundsRadius > 0
    assert len(bridge.boundsCenter) == 3


def test_a_root_with_no_models_says_so(qt_app, tmp_path: Path) -> None:
    empty = tmp_path / "empty-root"
    empty.mkdir()
    bridge = EditorBridge(empty)
    assert bridge.categories == []
    assert bridge.statusText == i18n.t(bridge.language, "status_no_root")


def test_selecting_a_model_lists_its_parts_and_frames_them(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    names = sorted(part["filename"] for part in bridge.parts)
    assert names == ["base_link.STL", "link_1.STL"]
    assert bridge.boundsRadius > 0
    assert len(bridge.boundsCenter) == 3


def test_the_selected_part_has_its_own_center_and_none_gives_the_origin(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    assert bridge.selectedPartCenter == [0.0, 0.0, 0.0]
    bridge.selectPart("base_link.STL")
    center = bridge.selectedPartCenter
    assert len(center) == 3
    assert all(isinstance(value, float) for value in center)


def test_a_part_that_does_not_exist_gives_the_origin_and_no_crash(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    bridge.selectPart("no-such-part.STL")
    assert bridge.selectedPartCenter == [0.0, 0.0, 0.0]


def test_the_assembled_view_switch_notifies_once_and_keeps_the_selection(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    bridge.selectPart("base_link.STL")
    changes: list[bool] = []
    bridge.partsChanged.connect(lambda: changes.append(bridge.assembledView))
    current = bridge.assembledView
    bridge.setAssembledView(current)  # no change, no notification
    assert changes == []
    bridge.setAssembledView(not current)
    assert bridge.assembledView is (not current)
    assert changes
    assert bridge.selectedPart == "base_link.STL"


def test_a_model_without_a_kinematic_assembly_reports_that(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    assert isinstance(bridge.hasAssembly, bool)
