# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for i18n.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# Every language has exactly the keys English has and the same {placeholders}:
# a missing key shows English (or the bare key) in the window, and a changed
# placeholder breaks the message at run time.
# =============================================================================
from __future__ import annotations

import re

import pytest

from hydra_umc_editor_stl import i18n

PLACEHOLDER = re.compile(r"\{[a-z_]+\}")
OTHER_LANGUAGES = [code for code, _ in i18n.LANGUAGES if code != "en"]


def test_the_language_menu_lists_every_translation_table() -> None:
    assert {code for code, _ in i18n.LANGUAGES} == set(i18n.TRANSLATIONS)


def test_portuguese_is_offered() -> None:
    assert "pt" in {code for code, _ in i18n.LANGUAGES}


@pytest.mark.parametrize("lang", OTHER_LANGUAGES)
def test_a_language_has_exactly_the_english_keys(lang: str) -> None:
    english = set(i18n.TRANSLATIONS["en"])
    assert set(i18n.TRANSLATIONS[lang]) == english


@pytest.mark.parametrize("lang", OTHER_LANGUAGES)
def test_a_language_keeps_the_english_placeholders(lang: str) -> None:
    for key, english in i18n.TRANSLATIONS["en"].items():
        assert sorted(PLACEHOLDER.findall(i18n.TRANSLATIONS[lang][key])) == sorted(PLACEHOLDER.findall(english)), (lang, key)


def test_an_unknown_language_falls_back_to_english_and_an_unknown_key_to_itself() -> None:
    assert i18n.t("xx", "status_ready") == "Ready."
    assert i18n.t("pt", "no_such_key") == "no_such_key"


def test_portuguese_formats_its_placeholders() -> None:
    assert i18n.t("pt", "status_model_loaded", count=3, model="ar3") == "3 peça(s) carregada(s) para ar3."
