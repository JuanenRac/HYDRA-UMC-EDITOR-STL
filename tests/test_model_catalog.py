# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for model_catalog.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
from __future__ import annotations

from pathlib import Path

from hydra_umc_editor_stl.model_catalog import list_categories, list_models, load_model


def test_list_categories_finds_the_real_category(ecosystem_root: Path) -> None:
    assert list_categories(ecosystem_root, "studio") == ["robots-6-dof"]


def test_list_categories_empty_for_a_missing_library(ecosystem_root: Path) -> None:
    assert list_categories(ecosystem_root, "suite") == []


def test_list_models_finds_the_real_model(ecosystem_root: Path) -> None:
    assert list_models(ecosystem_root, "studio", "robots-6-dof") == ["ar3"]


def test_list_models_empty_for_a_missing_category(ecosystem_root: Path) -> None:
    assert list_models(ecosystem_root, "studio", "no-such-category") == []


def test_load_model_lists_real_parts_and_metadata(ecosystem_root: Path) -> None:
    model = load_model(ecosystem_root, "studio", "robots-6-dof", "ar3")
    assert model is not None
    filenames = sorted(p.filename for p in model.parts)
    assert filenames == ["base_link.STL", "link_1.STL"]
    assert all(p.editable for p in model.parts)
    assert all(p.size_bytes > 0 for p in model.parts)
    assert model.metadata is not None
    assert model.metadata["model"] == "AR3 (6-DOF)"
    assert model.metadata["dof"] == 6


def test_load_model_none_for_a_missing_model(ecosystem_root: Path) -> None:
    assert load_model(ecosystem_root, "studio", "robots-6-dof", "no-such-model") is None
