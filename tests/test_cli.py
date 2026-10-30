# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for the --cli command line (main.py)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from hydra_umc_editor_stl import main as main_module

from .conftest import make_cube_stl

LIB = ("studio", "robots-6-dof", "ar3")


def run_cli(monkeypatch, capsys, root: Path, *args: str) -> tuple[int, str, str]:
    monkeypatch.setattr(sys, "argv", ["hydra-umc-editor-stl", "--cli", *args])
    code = main_module.main()
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def selector(root: Path) -> list[str]:
    return ["--root", str(root), *LIB]


def test_categories_models_and_parts_list_the_real_tree(monkeypatch, capsys, ecosystem_root: Path) -> None:
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "categories", "--root", str(ecosystem_root), "studio")
    assert code == 0 and out.split() == ["robots-6-dof"]
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "models", "--root", str(ecosystem_root), "studio", "robots-6-dof", "--json")
    assert code == 0 and json.loads(out) == ["ar3"]
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "parts", *selector(ecosystem_root), "--json")
    assert code == 0
    assert {p["filename"] for p in json.loads(out)} == {"base_link.STL", "link_1.STL"}
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "parts", *selector(ecosystem_root))
    assert code == 0 and "base_link.STL\t684 bytes" in out


def test_an_unknown_model_is_an_error_for_every_command(monkeypatch, capsys, ecosystem_root: Path) -> None:
    missing = ["--root", str(ecosystem_root), "studio", "robots-6-dof", "nope"]
    source = str(ecosystem_root / "x.stl")
    for command in (
        ["parts", *missing],
        ["transform", *missing, "a.stl", "--scale", "2"],
        ["replace", *missing, "a.stl", source],
        ["remove", *missing, "a.stl"],
        ["add", *missing, source],
        ["push", *missing, "--host", "127.0.0.1", "--username", "u", "--password", "p"],
    ):
        code, out, err = run_cli(monkeypatch, capsys, ecosystem_root, *command)
        assert code == 1, command
        assert "No such model" in err, command


def test_transform_changes_the_part_and_reports_the_new_bounds(monkeypatch, capsys, ecosystem_root: Path) -> None:
    code, out, _ = run_cli(
        monkeypatch, capsys, ecosystem_root, "transform", *selector(ecosystem_root), "base_link.STL", "--tx", "100", "--scale", "2"
    )
    assert code == 0
    assert "new bounds" in out


@pytest.mark.parametrize("scale", ["0", "-2", "nan", "inf"])
def test_transform_with_a_bad_scale_fails_and_keeps_the_file(monkeypatch, capsys, ecosystem_root: Path, scale: str) -> None:
    part = ecosystem_root / "HYDRA-UMC-STUDIO" / "public" / "models" / "robots-6-dof" / "ar3" / "base_link.STL"
    before = part.read_bytes()
    code, _, err = run_cli(monkeypatch, capsys, ecosystem_root, "transform", *selector(ecosystem_root), "base_link.STL", "--scale", scale)
    assert code == 1 and "Transform failed" in err
    assert part.read_bytes() == before


def test_a_part_name_that_leaves_the_model_is_refused(monkeypatch, capsys, ecosystem_root: Path) -> None:
    code, _, err = run_cli(monkeypatch, capsys, ecosystem_root, "remove", *selector(ecosystem_root), "../../../../outside.stl")
    assert code == 1 and "Remove failed" in err


def test_add_replace_and_remove_through_the_cli(monkeypatch, capsys, ecosystem_root: Path, tmp_path: Path) -> None:
    extra = tmp_path / "extra.stl"
    make_cube_stl(extra, size=3.0)
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "add", *selector(ecosystem_root), str(extra), "--dest-filename", "new.stl")
    assert code == 0 and "Added as new.stl" in out
    code, _, err = run_cli(monkeypatch, capsys, ecosystem_root, "add", *selector(ecosystem_root), str(extra), "--dest-filename", "new.stl")
    assert code == 1 and "already exists" in err
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "replace", *selector(ecosystem_root), "new.stl", str(extra))
    assert code == 0 and "Replaced new.stl" in out
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root, "remove", *selector(ecosystem_root), "new.stl")
    assert code == 0 and ".trash" in out
    junk = tmp_path / "junk.stl"
    junk.write_bytes(b"junk")
    code, _, err = run_cli(monkeypatch, capsys, ecosystem_root, "add", *selector(ecosystem_root), str(junk))
    assert code == 1 and "Add failed" in err


def test_push_prints_the_warnings_and_reports_an_unreachable_server(monkeypatch, capsys, ecosystem_root: Path) -> None:
    code, _, err = run_cli(
        monkeypatch, capsys, ecosystem_root, "push", *selector(ecosystem_root),
        "--host", "127.0.0.1", "--port", "1", "--username", "admin", "--password", "pw",
    )
    assert code == 1
    assert "Warning:" in err and "Push failed" in err


def test_push_reads_the_password_from_the_environment(monkeypatch, capsys, ecosystem_root: Path) -> None:
    monkeypatch.setenv("HYDRA_UMC_PASSWORD", "from-env")
    seen: list[str] = []

    class FakeClient:
        def __init__(self, host, port) -> None:
            pass

        def login(self, username: str, password: str) -> None:
            seen.append(password)

        def push_model(self, model, category, overwrite, allow_stacked=False) -> str:
            return "slug-1"

    monkeypatch.setattr(main_module, "ServerClient", FakeClient)
    code, out, _ = run_cli(
        monkeypatch, capsys, ecosystem_root, "push", *selector(ecosystem_root), "--host", "h", "--username", "admin"
    )
    assert code == 0 and "Pushed as slug-1" in out
    assert seen == ["from-env"]


def test_no_subcommand_prints_the_help(monkeypatch, capsys, ecosystem_root: Path) -> None:
    code, out, _ = run_cli(monkeypatch, capsys, ecosystem_root)
    assert code == 0 and "usage:" in out


def test_version_flag(monkeypatch, capsys, ecosystem_root: Path) -> None:
    with pytest.raises(SystemExit) as stop:
        run_cli(monkeypatch, capsys, ecosystem_root, "--version")
    assert stop.value.code == 0
    assert "hydra-umc-editor-stl" in capsys.readouterr().out


def test_the_saved_root_wins_over_the_parent_directory(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(main_module.settings, "get_saved_ecosystem_root", lambda: tmp_path)
    assert main_module.resolve_ecosystem_root() == tmp_path
    monkeypatch.setattr(main_module.settings, "get_saved_ecosystem_root", lambda: None)
    assert main_module.resolve_ecosystem_root() == main_module.default_ecosystem_root()
