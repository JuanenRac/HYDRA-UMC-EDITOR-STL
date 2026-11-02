# =============================================================================
# HYDRA-UMC-EDITOR-STL - Hand a model over to the URDF editor: urdf_bridge.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# "Open this model in the URDF editor": the model's own editable parts are written, with the placement they have at the home
# pose, as a URDF in a work folder (meshes copied next to it) and the editor is started on that file (`main.py --open FILE`).
# The model folder itself is never written to. The editor is looked for as the HYDRA-UMC-EDITOR-URDF checkout next to the
# others (it must be a git checkout with a main.py) or at the `urdf_editor_path` of the saved settings. Starting a program is
# a thing to switch on: the window offers the button only when `open_in_urdf_editor` is true in the saved settings.
# =============================================================================
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from . import settings
from .catalog_push import _upload_filename, build_assembly_urdf, home_placements
from .model_catalog import ModelInfo

EDITOR_DIRNAME = "HYDRA-UMC-EDITOR-URDF"
WORK_DIRNAME = "urdf_handoff"


class UrdfBridgeError(RuntimeError):
    pass


def handoff_enabled() -> bool:
    """True only when `open_in_urdf_editor` is the boolean true in the saved settings (off by default)."""
    return settings.load_settings().get("open_in_urdf_editor") is True


def work_root() -> Path:
    """Where the handed-over models are written: `urdf_handoff_dir` of the saved settings, else a folder in the home directory."""
    value = settings.load_settings().get("urdf_handoff_dir")
    if isinstance(value, str) and value:
        return Path(value)
    return Path.home() / ".hydra_umc_editor_stl" / WORK_DIRNAME


def find_urdf_editor(ecosystem_root: Path | None) -> Path | None:
    """The main.py of the URDF editor: the saved `urdf_editor_path` when it is a real file, else the git checkout next to the others."""
    value = settings.load_settings().get("urdf_editor_path")
    if isinstance(value, str) and value:
        candidate = Path(value)
        return candidate if candidate.is_file() and candidate.name == "main.py" else None
    if ecosystem_root is None:
        return None
    folder = ecosystem_root / EDITOR_DIRNAME
    main = folder / "main.py"
    return main if (folder / ".git").exists() and main.is_file() else None


def prepare_model_for_urdf_editor(model: ModelInfo, ecosystem_root: Path | None, destination: Path | None = None) -> Path:
    """Writes `<destination>/<library>_<category>_<model>/<model>.urdf` with its `meshes/` and returns the URDF path.
    A robot or machine whose home-pose placement is not known here is written with its parts at the origin (the editor is where
    they are articulated); a folder from an earlier handover of the same model is replaced."""
    editable = [p for p in model.parts if p.editable]
    if not editable:
        raise UrdfBridgeError("this model has no editable (.stl) parts to hand over")
    base = destination if destination is not None else work_root()
    folder = base / f"{model.library}_{model.category}_{model.model_id}".replace("/", "_").replace("\\", "_")
    if folder.exists():
        shutil.rmtree(folder)
    meshes = folder / "meshes"
    meshes.mkdir(parents=True)
    for index, part in enumerate(editable):
        shutil.copy2(model.path / part.filename, meshes / _upload_filename(index, part.filename))
    urdf = folder / f"{model.model_id}.urdf"
    urdf.write_text(build_assembly_urdf(model, home_placements(model, ecosystem_root)), encoding="utf-8")
    return urdf


def launch_urdf_editor(editor_main: Path, urdf: Path) -> subprocess.Popen:
    """Starts the editor on the file, detached (its own window); this does not wait for it."""
    if not editor_main.is_file():
        raise UrdfBridgeError(f"the URDF editor was not found: {editor_main}")
    try:
        return subprocess.Popen([sys.executable, str(editor_main), "--open", str(urdf)], cwd=str(editor_main.parent))
    except OSError as error:
        raise UrdfBridgeError(str(error)) from error


def open_in_urdf_editor(model: ModelInfo, ecosystem_root: Path | None, launch: bool = True) -> Path:
    """Prepares the model and (with `launch`) starts the editor on it; returns the URDF path."""
    urdf = prepare_model_for_urdf_editor(model, ecosystem_root)
    if launch:
        editor = find_urdf_editor(ecosystem_root)
        if editor is None:
            raise UrdfBridgeError(
                f"the URDF editor was not found: put {EDITOR_DIRNAME} (a git checkout) next to the others or set urdf_editor_path in the saved settings"
            )
        launch_urdf_editor(editor, urdf)
    return urdf
