# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the language and the selection slots of EditorBridge
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The language, the ecosystem root and the library / category / model selection of the bridge, without touching the real settings file."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from hydra_umc_editor_stl import i18n, settings  # noqa: E402
from hydra_umc_editor_stl.qt_gui import EditorBridge  # noqa: E402


@pytest.fixture
def saved(monkeypatch: pytest.MonkeyPatch) -> dict[str, list]:
    """Records what the bridge saves instead of writing the settings of the person running the tests."""
    calls: dict[str, list] = {"lang": [], "root": []}
    monkeypatch.setattr(settings, "save_lang", lambda lang: calls["lang"].append(lang))
    monkeypatch.setattr(settings, "save_ecosystem_root", lambda path: calls["root"].append(path))
    return calls


def test_the_bridge_offers_the_eight_languages_and_a_version(qt_app, ecosystem_root: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    codes = {entry["code"] for entry in bridge.availableLanguages}
    assert codes == {"en", "es", "de", "fr", "it", "ja", "zh", "pt"}
    assert all(entry["label"] for entry in bridge.availableLanguages)
    assert bridge.appVersion


def test_setting_the_language_saves_it_once_and_changes_the_texts(qt_app, ecosystem_root: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    first, second = [code for code in ("de", "fr", "it") if code != bridge.language][:2]
    seen: list[str] = []
    bridge.languageChanged.connect(lambda: seen.append(bridge.language))
    bridge.setLanguage(first)
    bridge.setLanguage(first)  # the same language again changes nothing
    assert saved["lang"] == [first]
    assert seen == [first]
    assert bridge.text("window_title") == i18n.t(first, "window_title")
    bridge.setLanguage(second)
    assert bridge.text("window_title") == i18n.t(second, "window_title")
    assert saved["lang"] == [first, second]


def test_a_text_key_that_does_not_exist_gives_a_string_and_no_crash(qt_app, ecosystem_root: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert isinstance(bridge.text("this-key-does-not-exist"), str)


def test_the_ecosystem_root_is_taken_only_when_it_is_a_directory(qt_app, ecosystem_root: Path, tmp_path: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    before = bridge.ecosystemRoot
    bridge.setEcosystemRoot(str(tmp_path / "not-there"))
    assert bridge.ecosystemRoot == before
    assert saved["root"] == []
    other = tmp_path / "other-root"
    other.mkdir()
    changed: list[bool] = []
    bridge.ecosystemRootChanged.connect(lambda: changed.append(True))
    bridge.setEcosystemRoot(str(other))
    assert Path(bridge.ecosystemRoot) == other.resolve()
    assert saved["root"] == [other.resolve()]
    assert changed == [True]


def test_the_ecosystem_root_accepts_the_file_url_that_the_folder_dialog_gives(qt_app, ecosystem_root: Path, tmp_path: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    other = tmp_path / "from-dialog"
    other.mkdir()
    bridge.setEcosystemRoot(other.resolve().as_uri())
    assert Path(bridge.ecosystemRoot) == other.resolve()


def test_selecting_a_library_clears_the_category_and_the_model(qt_app, ecosystem_root: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    assert bridge.libraries == ["studio", "suite"]
    bridge.selectCategory("robots-6-dof")
    bridge.selectModel("ar3")
    assert (bridge.selectedCategory, bridge.selectedModel) == ("robots-6-dof", "ar3")
    notified: list[bool] = []
    bridge.selectionChanged.connect(lambda: notified.append(True))
    bridge.selectLibrary("studio")  # the same library: nothing happens
    assert notified == [] and bridge.selectedModel == "ar3"
    bridge.selectLibrary("suite")
    assert bridge.selectedLibrary == "suite"
    assert (bridge.selectedCategory, bridge.selectedModel) == ("", "")
    assert notified


def test_selecting_the_same_category_or_model_twice_does_not_notify_again(qt_app, ecosystem_root: Path, saved) -> None:
    bridge = EditorBridge(ecosystem_root)
    notified: list[bool] = []
    bridge.selectionChanged.connect(lambda: notified.append(True))
    bridge.selectCategory("robots-6-dof")
    after_category = len(notified)
    assert after_category >= 1
    bridge.selectCategory("robots-6-dof")
    assert len(notified) == after_category
    bridge.selectModel("ar3")
    after_model = len(notified)
    assert after_model > after_category
    bridge.selectModel("ar3")
    assert len(notified) == after_model
    assert "ar3" in bridge.models
    assert not bridge.isIndependentPartsCategory
