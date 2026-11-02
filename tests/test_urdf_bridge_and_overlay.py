# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the hand-over to the URDF editor and the comparison overlay
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# Both are off unless the saved settings switch them on (open_in_urdf_editor, diff_overlay).
# =============================================================================
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from hydra_umc_editor_stl import settings, urdf_bridge
from hydra_umc_editor_stl.model_catalog import load_model
from hydra_umc_editor_stl.stl_ops import remove_part
from hydra_umc_editor_stl.urdf_bridge import UrdfBridgeError, find_urdf_editor, handoff_enabled, open_in_urdf_editor, prepare_model_for_urdf_editor


@pytest.fixture(autouse=True)
def _own_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "settings.json")


def _model(ecosystem_root: Path):
    model = load_model(ecosystem_root, "studio", "robots-6-dof", "ar3")
    assert model is not None
    return model


def test_the_hand_over_is_off_unless_the_settings_switch_it_on() -> None:
    assert handoff_enabled() is False
    settings.save_settings(open_in_urdf_editor="yes")
    assert handoff_enabled() is False
    settings.save_settings(open_in_urdf_editor=True)
    assert handoff_enabled() is True


def test_the_model_is_written_as_a_urdf_with_its_meshes_and_the_model_folder_is_left_alone(tmp_path: Path, ecosystem_root: Path) -> None:
    model = _model(ecosystem_root)
    before = sorted(p.name for p in model.path.iterdir())
    urdf = prepare_model_for_urdf_editor(model, ecosystem_root, tmp_path / "out")
    root = ET.parse(urdf).getroot()
    meshes = [m.get("filename") for m in root.iter("mesh")]
    assert meshes and all((urdf.parent / name).is_file() for name in meshes)
    assert sorted(p.name for p in model.path.iterdir()) == before


def test_a_second_hand_over_replaces_the_first(tmp_path: Path, ecosystem_root: Path) -> None:
    model = _model(ecosystem_root)
    first = prepare_model_for_urdf_editor(model, ecosystem_root, tmp_path / "out")
    (first.parent / "stale.txt").write_text("old", encoding="utf-8")
    again = prepare_model_for_urdf_editor(model, ecosystem_root, tmp_path / "out")
    assert again == first and not (first.parent / "stale.txt").exists()


def test_an_editor_is_found_only_as_a_git_checkout_with_a_main_py(tmp_path: Path) -> None:
    root = tmp_path / "eco"
    (root / "HYDRA-UMC-EDITOR-URDF").mkdir(parents=True)
    (root / "HYDRA-UMC-EDITOR-URDF" / "main.py").write_text("", encoding="utf-8")
    assert find_urdf_editor(root) is None  # no .git: not trusted
    (root / "HYDRA-UMC-EDITOR-URDF" / ".git").mkdir()
    assert find_urdf_editor(root) == root / "HYDRA-UMC-EDITOR-URDF" / "main.py"
    assert find_urdf_editor(None) is None


def test_the_editor_is_started_on_the_file(tmp_path: Path, ecosystem_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(urdf_bridge.subprocess, "Popen", lambda cmd, cwd=None: calls.append(cmd))
    editor = ecosystem_root / "HYDRA-UMC-EDITOR-URDF"
    (editor / ".git").mkdir(parents=True)
    (editor / "main.py").write_text("", encoding="utf-8")
    settings.save_settings(urdf_handoff_dir=str(tmp_path / "work"))
    urdf = open_in_urdf_editor(_model(ecosystem_root), ecosystem_root)
    assert calls == [[calls[0][0], str(editor / "main.py"), "--open", str(urdf)]]
    assert str(urdf).startswith(str(tmp_path / "work"))


def test_without_an_editor_the_hand_over_says_so(tmp_path: Path, ecosystem_root: Path) -> None:
    settings.save_settings(urdf_handoff_dir=str(tmp_path / "work"))
    with pytest.raises(UrdfBridgeError, match="not found"):
        open_in_urdf_editor(_model(ecosystem_root), ecosystem_root)
    # the files are written anyway, so a later launch can use them
    assert any((tmp_path / "work").rglob("*.urdf"))


def test_the_overlay_exists_only_with_its_switch_and_shows_the_trash_version(qt_app, ecosystem_root: Path) -> None:
    pytest.importorskip("PySide6")
    from hydra_umc_editor_stl.qt_gui import EditorBridge

    bridge = EditorBridge(ecosystem_root)
    bridge.selectLibrary("studio")
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")
    model = _model(ecosystem_root)
    remove_part(model.path, "link_1.STL")
    entry = bridge.trashEntries()[0]["entry"]
    assert bridge.diffOverlayEnabled is False
    bridge.showTrashOverlay(entry)
    assert bridge.overlayPath == ""
    settings.save_settings(diff_overlay=True)
    assert bridge.diffOverlayEnabled is True
    bridge.showTrashOverlay("no-such-entry")
    assert bridge.overlayPath == ""
    bridge.showTrashOverlay(entry)
    assert Path(bridge.overlayPath).is_file() and Path(bridge.overlayPath).parent.name == ".trash"
    bridge.clearOverlay()
    assert bridge.overlayPath == ""
    bridge.showTrashOverlay(entry)
    bridge.selectPart("base_link.STL")
    bridge.setSelectedPartColor("#112233")  # reloading the parts drops the overlay
    assert bridge.overlayPath == ""
