# =============================================================================
# HYDRA-UMC-EDITOR-STL - Persisted user settings: settings.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
# =============================================================================
"""Real, local persistence for the small set of choices this GUI should
remember across launches - same real mechanism HYDRA-UMC-UPDATER's own
settings.py already uses (one JSON file in the user's own home
directory), adapted here to remember the ecosystem root (where
HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE are checked out) and the UI language."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path.home() / ".hydra_umc_editor_stl_settings.json"


def load_settings() -> dict[str, Any]:
    """Every real, currently-saved preference. Returns `{}` on a missing
    file, unreadable JSON, or a non-object top level - never raises."""
    try:
        raw = SETTINGS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(**updates: Any) -> None:
    """Merges `updates` into whatever is already saved and writes the
    real, combined result back - best-effort, a read-only home directory
    must never crash the GUI over a saved preference."""
    current = load_settings()
    current.update(updates)
    try:
        SETTINGS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except OSError:
        pass


def get_saved_ecosystem_root() -> Path | None:
    """The real, previously chosen ecosystem root, only when it is still
    a real, existing directory on this machine - a saved path pointing
    at a since-deleted/renamed/unmounted location must never be silently
    handed to the rest of this tool as if it were still valid."""
    raw = load_settings().get("ecosystem_root")
    if not isinstance(raw, str) or not raw:
        return None
    path = Path(raw)
    return path if path.is_dir() else None


def save_ecosystem_root(path: Path) -> None:
    save_settings(ecosystem_root=str(path))


def get_saved_lang() -> str | None:
    lang = load_settings().get("lang")
    return lang if isinstance(lang, str) and lang else None


def save_lang(lang: str) -> None:
    save_settings(lang=lang)
