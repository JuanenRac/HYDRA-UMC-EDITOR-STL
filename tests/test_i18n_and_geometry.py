# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests/test_i18n_and_geometry.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Characterization tests: the GUI translation tables and the Qt Quick 3D
STL geometry loader (the latter only when PySide6 Quick 3D is available)."""
from __future__ import annotations

import locale
import string

import numpy as np
import pytest

from hydra_umc_editor_stl import i18n

CODES = ["en", "es", "fr", "it", "de", "zh", "ja", "pt"]


def test_language_list_has_the_eight_codes_in_order() -> None:
    assert [code for code, _ in i18n.LANGUAGES] == CODES


def test_every_language_has_exactly_the_english_keys() -> None:
    english = set(i18n.TRANSLATIONS["en"])
    for code in CODES:
        assert set(i18n.TRANSLATIONS[code]) == english, code


def test_placeholders_match_the_english_ones() -> None:
    fmt = string.Formatter()

    def fields(text: str) -> set[str]:
        return {name for _, name, _, _ in fmt.parse(text) if name}

    for key, english in i18n.TRANSLATIONS["en"].items():
        for code in CODES:
            assert fields(i18n.TRANSLATIONS[code][key]) == fields(english), (code, key)


def test_no_translation_is_empty() -> None:
    for code in CODES:
        for key, text in i18n.TRANSLATIONS[code].items():
            assert text.strip(), (code, key)


def test_t_substitutes_and_falls_back() -> None:
    assert "C:/x" in i18n.t("en", "ecosystem_root_label", path="C:/x")
    assert i18n.t("xx", "window_title") == i18n.TRANSLATIONS["en"]["window_title"]
    assert i18n.t("en", "no_such_key") == "no_such_key"
    # a missing placeholder returns the raw template instead of raising
    assert i18n.t("en", "ecosystem_root_label") == i18n.TRANSLATIONS["en"]["ecosystem_root_label"]


def test_resolve_initial_lang_prefers_saved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n.settings, "get_saved_lang", lambda: "de")
    assert i18n.resolve_initial_lang() == "de"


def test_resolve_initial_lang_uses_locale_then_english(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n.settings, "get_saved_lang", lambda: "zz")
    monkeypatch.setattr(locale, "getlocale", lambda: ("pt_PT", "UTF-8"))
    assert i18n.resolve_initial_lang() == "pt"
    monkeypatch.setattr(locale, "getlocale", lambda: ("xx_XX", "UTF-8"))
    assert i18n.resolve_initial_lang() == "en"
    monkeypatch.setattr(locale, "getlocale", lambda: (None, None))
    assert i18n.resolve_initial_lang() == "en"

    def broken():
        raise ValueError("bad locale")

    monkeypatch.setattr(locale, "getlocale", broken)
    assert i18n.resolve_initial_lang() == "en"


def test_save_lang_preference_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    saved: list[str] = []
    monkeypatch.setattr(i18n.settings, "save_lang", saved.append)
    i18n.save_lang_preference("ja")
    assert saved == ["ja"]


def _write_triangle(path) -> None:
    from stl import mesh as stl_mesh

    m = stl_mesh.Mesh(np.zeros(1, dtype=stl_mesh.Mesh.dtype))
    m.vectors[0] = np.array([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float32)
    m.save(str(path))


@pytest.fixture
def geometry_module():
    pytest.importorskip("PySide6.QtQuick3D")
    from hydra_umc_editor_stl import stl_geometry

    return stl_geometry


def test_geometry_loads_a_triangle(geometry_module, tmp_path) -> None:
    path = tmp_path / "tri.stl"
    _write_triangle(path)
    geo = geometry_module.StlGeometry()
    geo.source = str(path)
    assert geo.source == str(path)
    assert geo.stride() == 24
    assert len(bytes(geo.vertexData())) == 3 * 24
    assert (geo.boundsMax().x(), geo.boundsMax().y()) == (2.0, 2.0)


def test_geometry_empty_and_missing_sources_draw_nothing(geometry_module, tmp_path) -> None:
    geo = geometry_module.StlGeometry()
    geo.source = str(tmp_path / "missing.stl")
    assert len(bytes(geo.vertexData())) == 0
    geo.source = ""
    assert len(bytes(geo.vertexData())) == 0


def test_geometry_placement_translates_vertices(geometry_module, tmp_path) -> None:
    path = tmp_path / "tri.stl"
    _write_triangle(path)
    geo = geometry_module.StlGeometry()
    geo.source = str(path)
    identity_and_shift = [1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 0, 0]
    geo.placement = identity_and_shift
    assert list(geo.placement) == [float(v) for v in identity_and_shift]
    assert geo.boundsMin().x() == 10.0
    assert geo.boundsMax().x() == 12.0
    geo.placement = []
    assert geo.boundsMin().x() == 0.0
