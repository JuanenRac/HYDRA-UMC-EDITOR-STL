# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the STL operations, the trash and the overlay of EditorBridge
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Transform, replace, remove, restore and empty the trash through the bridge, and the comparison overlay that is off unless the settings switch it on."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from hydra_umc_editor_stl import i18n, settings  # noqa: E402
from hydra_umc_editor_stl.qt_gui import EditorBridge  # noqa: E402
from tests.conftest import make_cube_stl  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "save_lang", lambda lang: None)
    monkeypatch.setattr(settings, "save_ecosystem_root", lambda path: None)
    monkeypatch.setattr(settings, "load_settings", lambda: {})


def _model(bridge: EditorBridge, part: str = "") -> None:
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")
    if part:
        bridge.selectPart(part)


def _said(bridge: EditorBridge, key: str, **fields: object) -> bool:
    return bridge.statusText == i18n.t(bridge.language, key, **fields)


@pytest.mark.parametrize("operation", ["transform", "replace", "remove"])
def test_an_operation_with_no_part_selected_asks_for_one_and_changes_nothing(qt_app, ecosystem_root: Path, operation: str) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    before = sorted(p["filename"] for p in bridge.parts)
    if operation == "transform":
        bridge.applyTransform(1, 0, 0, 0, 0, 0, 1)
    elif operation == "replace":
        bridge.replaceSelectedPart(str(ecosystem_root / "nothing.stl"))
    else:
        bridge.removeSelectedPart()
    assert _said(bridge, "msg_select_part_first")
    assert sorted(p["filename"] for p in bridge.parts) == before


def test_a_transform_of_the_selected_part_moves_it(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge, "base_link.STL")
    before = bridge.selectedPartCenter
    bridge.applyTransform(5, 0, 0, 0, 0, 0, 1)
    bridge.selectPart("base_link.STL")  # the parts are listed again after a transform; the piece is picked again to read it
    after = bridge.selectedPartCenter
    assert after[0] == pytest.approx(before[0] + 5, abs=1e-3)
    assert after[1] == pytest.approx(before[1], abs=1e-3)


def test_replacing_a_part_with_a_file_that_does_not_exist_reports_the_failure(qt_app, ecosystem_root: Path, tmp_path: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge, "base_link.STL")
    bridge.replaceSelectedPart(str(tmp_path / "absent.stl"))
    assert bridge.statusText
    assert not _said(bridge, "msg_replace_done")


def test_replacing_a_part_with_a_real_file_says_it_was_done(qt_app, ecosystem_root: Path, tmp_path: Path) -> None:
    source = tmp_path / "new_base.stl"
    make_cube_stl(source)
    bridge = EditorBridge(ecosystem_root)
    _model(bridge, "base_link.STL")
    part_file = next(Path(p["absolutePath"]) for p in bridge.parts if p["filename"] == "base_link.STL")
    other = next(Path(p["absolutePath"]) for p in bridge.parts if p["filename"] == "link_1.STL")
    other_before = other.read_bytes()
    bridge.replaceSelectedPart(str(source))
    assert part_file.read_bytes() == source.read_bytes()
    assert other.read_bytes() == other_before


def test_removing_a_part_puts_it_in_the_trash_and_restoring_brings_it_back(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge, "link_1.STL")
    bridge.removeSelectedPart()
    assert [p["filename"] for p in bridge.parts] == ["base_link.STL"]
    entries = bridge.trashEntries()
    assert len(entries) == 1 and entries[0]["original"] == "link_1.STL"
    bridge.restoreTrashEntry(entries[0]["entry"])
    assert sorted(p["filename"] for p in bridge.parts) == ["base_link.STL", "link_1.STL"]
    assert bridge.trashEntries() == []


def test_with_no_model_selected_the_trash_is_empty_and_a_restore_asks_for_a_model(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert bridge.trashEntries() == []
    bridge.restoreTrashEntry("whatever")
    assert _said(bridge, "msg_select_part_first")
    bridge.emptyTrash(True)  # nothing to empty, nothing to say, no crash


def test_restoring_an_entry_that_is_not_there_reports_the_failure(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge)
    bridge.restoreTrashEntry("not-an-entry")
    assert bridge.statusText
    assert not _said(bridge, "msg_restore_done", name="not-an-entry")


def test_the_trash_is_emptied_only_when_confirmed(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    _model(bridge, "link_1.STL")
    bridge.removeSelectedPart()
    bridge.emptyTrash(False)
    assert len(bridge.trashEntries()) == 1
    bridge.emptyTrash(True)
    assert bridge.trashEntries() == []
    assert _said(bridge, "msg_trash_empty_done", count=1)
    bridge.emptyTrash(True)
    assert _said(bridge, "msg_trash_is_empty")


def test_the_extras_are_off_with_empty_settings(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert bridge.diffOverlayEnabled is False
    _model(bridge, "link_1.STL")
    bridge.removeSelectedPart()
    bridge.showTrashOverlay(bridge.trashEntries()[0]["entry"])
    assert bridge.overlayPath == ""
    assert bridge.overlayPlacement == []


def test_with_the_overlay_switched_on_a_trash_version_is_laid_over_and_can_be_cleared(qt_app, ecosystem_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "load_settings", lambda: {"diff_overlay": True})
    bridge = EditorBridge(ecosystem_root)
    assert bridge.diffOverlayEnabled is True
    _model(bridge, "link_1.STL")
    bridge.removeSelectedPart()
    entry = bridge.trashEntries()[0]["entry"]
    changed: list[bool] = []
    bridge.overlayChanged.connect(lambda: changed.append(True))
    bridge.showTrashOverlay("an-entry-that-does-not-exist")
    assert bridge.overlayPath == "" and changed == []
    bridge.showTrashOverlay(entry)
    assert bridge.overlayPath.endswith(entry)
    assert _said(bridge, "msg_compare_shown")
    assert changed == [True]
    bridge.clearOverlay()
    assert bridge.overlayPath == "" and bridge.overlayPlacement == []
    assert changed == [True, True]
    bridge.clearOverlay()  # nothing to clear: no notification
    assert changed == [True, True]


def test_the_urdf_editor_button_does_nothing_while_it_is_switched_off(qt_app, ecosystem_root: Path) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert bridge.urdfEditorEnabled is False
    before = bridge.statusText
    bridge.openInUrdfEditor()
    assert bridge.statusText == before
