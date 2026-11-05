# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for model_catalog.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
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


def test_the_shared_library_folder_replaces_both_libraries(ecosystem_root: Path, tmp_path: Path) -> None:
    from hydra_umc_editor_stl.model_catalog import resolve_library_root, shared_library_dir

    shared = tmp_path / "common-library"
    (shared / "robots-6-dof" / "xarm6").mkdir(parents=True)
    env = {"HYDRA_UMC_LIBRARY_DIR": str(shared)}
    assert shared_library_dir(env) == shared
    assert resolve_library_root(ecosystem_root, "studio", env) == shared
    assert resolve_library_root(ecosystem_root, "suite", env) == shared
    assert list_categories(ecosystem_root, "suite") == []  # without the variable each app keeps its own folder


def test_a_wrong_shared_library_folder_falls_back_to_the_folders_of_the_apps(ecosystem_root: Path, tmp_path: Path) -> None:
    from hydra_umc_editor_stl.model_catalog import resolve_library_root, shared_library_dir

    for value in ("", "   ", str(tmp_path / "does-not-exist")):
        env = {"HYDRA_UMC_LIBRARY_DIR": value}
        assert shared_library_dir(env) is None
        assert resolve_library_root(ecosystem_root, "studio", env) == ecosystem_root / "HYDRA-UMC-STUDIO/public/models"
    assert resolve_library_root(ecosystem_root, "unknown", {"HYDRA_UMC_LIBRARY_DIR": str(tmp_path)}) is None


def test_with_one_shared_folder_the_sync_has_nothing_to_do(ecosystem_root: Path, tmp_path: Path, monkeypatch) -> None:
    from hydra_umc_editor_stl.library_sync import sync_libraries

    shared = tmp_path / "common-library"
    (shared / "cat" / "m").mkdir(parents=True)
    (shared / "cat" / "m" / "a.stl").write_bytes(b"x")
    monkeypatch.setenv("HYDRA_UMC_LIBRARY_DIR", str(shared))
    outcome = sync_libraries(ecosystem_root, apply=True)
    assert outcome["diff"].in_sync and outcome["copied"] == [] and outcome["replaced"] == []
