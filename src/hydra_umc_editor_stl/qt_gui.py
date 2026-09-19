# =============================================================================
# HYDRA-UMC-EDITOR-STL - Qt Quick / QML GUI bridge: qt_gui.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0 - see LICENSE
#
# The visual QML shell over model_catalog.py/stl_ops.py - QML calls this
# bridge, the bridge calls the exact same real discovery/mutation
# functions `--cli` uses, so the GUI can never show/do anything the CLI
# itself couldn't. Same real "no separate GUI-only logic" discipline
# HYDRA-UMC-UPDATER's own qt_gui.py already documents. Every operation
# here is synchronous, local-disk file I/O (no network, no long-running
# subprocess), so unlike UPDATER's own bridge this needs no background
# worker thread - a transform/replace/remove/add call returns before QML
# even notices a delay.
# =============================================================================
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from . import i18n, settings
from . import __version__
from .model_catalog import list_categories, list_models, load_model
from .part_colors import DEFAULT_COLOR, load_part_colors, save_part_color
from .stl_geometry import StlGeometry
from .stl_ops import StlOpsError, add_part, model_bounds, remove_part, replace_part, transform_part


class EditorBridge(QObject):
    ecosystemRootChanged = Signal()
    languageChanged = Signal()
    librariesChanged = Signal()
    categoriesChanged = Signal()
    modelsChanged = Signal()
    partsChanged = Signal()
    selectionChanged = Signal()
    statusChanged = Signal()

    def __init__(self, ecosystem_root: Path) -> None:
        super().__init__()
        self._ecosystem_root = ecosystem_root
        self._lang = i18n.resolve_initial_lang()
        self._library = "studio"
        self._category = ""
        self._model = ""
        self._categories: list[str] = []
        self._models: list[str] = []
        self._parts: list[dict] = []
        self._selected_part = ""
        self._status = ""
        self._bounds_center = [0.0, 0.0, 0.0]
        self._bounds_radius = 100.0  # a real, honest default before any real model is loaded
        self._refresh_categories()

    # --- i18n ---------------------------------------------------------

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._lang

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        if lang == self._lang:
            return
        self._lang = lang
        i18n.save_lang_preference(lang)
        self.languageChanged.emit()

    @Slot(str, result=str)
    def text(self, key: str) -> str:
        return i18n.t(self._lang, key)

    @Property("QVariantList", constant=True)
    def availableLanguages(self) -> list[dict]:
        return [{"code": code, "label": label} for code, label in i18n.LANGUAGES]

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return __version__

    # --- ecosystem root / library / category / model selection --------

    @Property(str, notify=ecosystemRootChanged)
    def ecosystemRoot(self) -> str:
        return str(self._ecosystem_root)

    @Slot(str)
    def setEcosystemRoot(self, path: str) -> None:
        # QML FolderDialog hands back a file:// URL string - QUrl strips
        # the scheme back to a real local path cleanly on every platform
        # this ecosystem's own tools actually ship on (Windows/Linux).
        real_path = Path(QUrl(path).toLocalFile() or path).resolve()
        if not real_path.is_dir():
            return
        self._ecosystem_root = real_path
        settings.save_ecosystem_root(real_path)
        self.ecosystemRootChanged.emit()
        self._refresh_categories()

    @Property("QStringList", constant=True)
    def libraries(self) -> list[str]:
        return ["studio", "suite"]

    @Property(str, notify=selectionChanged)
    def selectedLibrary(self) -> str:
        return self._library

    @Slot(str)
    def selectLibrary(self, library: str) -> None:
        if library == self._library:
            return
        self._library = library
        self._category = ""
        self._model = ""
        self.selectionChanged.emit()
        self._refresh_categories()

    @Property("QStringList", notify=categoriesChanged)
    def categories(self) -> list[str]:
        return self._categories

    @Property(str, notify=selectionChanged)
    def selectedCategory(self) -> str:
        return self._category

    @Slot(str)
    def selectCategory(self, category: str) -> None:
        if category == self._category:
            return
        self._category = category
        self._model = ""
        self.selectionChanged.emit()
        self._refresh_models()

    @Property("QStringList", notify=modelsChanged)
    def models(self) -> list[str]:
        return self._models

    @Property(str, notify=selectionChanged)
    def selectedModel(self) -> str:
        return self._model

    @Slot(str)
    def selectModel(self, model: str) -> None:
        if model == self._model:
            return
        self._model = model
        self.selectionChanged.emit()
        self._refresh_parts()

    @Property("QVariantList", notify=partsChanged)
    def parts(self) -> list[dict]:
        return self._parts

    @Property("QVariantList", notify=partsChanged)
    def boundsCenter(self) -> list[float]:
        return self._bounds_center

    @Property(float, notify=partsChanged)
    def boundsRadius(self) -> float:
        return self._bounds_radius

    @Property(str, notify=selectionChanged)
    def selectedPart(self) -> str:
        return self._selected_part

    @Slot(str)
    def selectPart(self, filename: str) -> None:
        self._selected_part = filename
        self.selectionChanged.emit()

    @Property(str, notify=statusChanged)
    def statusText(self) -> str:
        return self._status

    def _set_status(self, text: str) -> None:
        self._status = text
        self.statusChanged.emit()

    def _refresh_categories(self) -> None:
        self._categories = list_categories(self._ecosystem_root, self._library)
        self.categoriesChanged.emit()
        self._models = []
        self.modelsChanged.emit()
        self._parts = []
        self.partsChanged.emit()
        if not self._categories:
            self._set_status(i18n.t(self._lang, "status_no_root"))
        else:
            self._set_status(i18n.t(self._lang, "status_ready"))

    def _refresh_models(self) -> None:
        self._models = list_models(self._ecosystem_root, self._library, self._category) if self._category else []
        self.modelsChanged.emit()
        self._parts = []
        self.partsChanged.emit()

    def _refresh_parts(self) -> None:
        model = self._load_selected_model()
        if model is None:
            self._parts = []
        else:
            colors = load_part_colors(model.path)
            self._parts = [
                {
                    "filename": p.filename,
                    "sizeBytes": p.size_bytes,
                    "editable": p.editable,
                    "absolutePath": str((model.path / p.filename).resolve()) if p.editable else "",
                    "color": colors.get(p.filename, DEFAULT_COLOR),
                }
                for p in model.parts
            ]
            editable_filenames = [p.filename for p in model.parts if p.editable]
            box = model_bounds(model.path, editable_filenames)
            if box is not None:
                self._bounds_center = [(a + b) / 2 for a, b in zip(box.min_xyz, box.max_xyz)]
                diagonal = sum((b - a) ** 2 for a, b in zip(box.min_xyz, box.max_xyz)) ** 0.5
                # Half the real diagonal, floored so a single tiny part
                # (a screw) doesn't put the camera closer than a sane
                # near-clip distance.
                self._bounds_radius = max(diagonal / 2, 5.0)
        self.partsChanged.emit()
        self._selected_part = ""
        self.selectionChanged.emit()
        if model is not None:
            self._set_status(i18n.t(self._lang, "status_model_loaded", count=len(model.parts), model=self._model))

    def _load_selected_model(self):
        if not self._category or not self._model:
            return None
        return load_model(self._ecosystem_root, self._library, self._category, self._model)

    # --- real STL operations --------------------------------------------

    @Slot(float, float, float, float, float, float, float)
    def applyTransform(self, tx: float, ty: float, tz: float, rx: float, ry: float, rz: float, scale: float) -> None:
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        try:
            bbox = transform_part(model.path, self._selected_part, (tx, ty, tz), (rx, ry, rz), scale)
        except StlOpsError as error:
            self._set_status(i18n.t(self._lang, "msg_transform_failed", error=str(error)))
            return
        self._set_status(i18n.t(
            self._lang, "msg_transform_applied",
            min=", ".join(f"{v:.1f}" for v in bbox.min_xyz),
            max=", ".join(f"{v:.1f}" for v in bbox.max_xyz),
        ))
        self._refresh_parts()

    @Slot(str)
    def replaceSelectedPart(self, source_path: str) -> None:
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        real_source = Path(QUrl(source_path).toLocalFile() or source_path)
        try:
            replace_part(model.path, self._selected_part, real_source)
        except StlOpsError as error:
            self._set_status(i18n.t(self._lang, "msg_replace_failed", error=str(error)))
            return
        self._set_status(i18n.t(self._lang, "msg_replace_done"))
        self._refresh_parts()

    @Slot()
    def removeSelectedPart(self) -> None:
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        try:
            remove_part(model.path, self._selected_part)
        except StlOpsError as error:
            self._set_status(i18n.t(self._lang, "msg_remove_failed", error=str(error)))
            return
        self._set_status(i18n.t(self._lang, "msg_remove_done", name=self._selected_part))
        self._refresh_parts()

    @Slot(str)
    def setSelectedPartColor(self, hex_color: str) -> None:
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        save_part_color(model.path, self._selected_part, hex_color)
        self._refresh_parts_preserving_selection()

    def _refresh_parts_preserving_selection(self) -> None:
        # Real gap that _refresh_parts() itself must never fix: a color
        # change should update this part's own row (list + 3D view) but
        # never drop the operator's own current selection the way every
        # OTHER mutation here does (they all move/rename/remove the file
        # itself, so dropping selection is the honest outcome there -
        # setting a color changes none of that).
        selected = self._selected_part
        self._refresh_parts()
        self._selected_part = selected
        self.selectionChanged.emit()

    @Slot(str, str)
    def addPart(self, source_path: str, dest_filename: str) -> None:
        model = self._load_selected_model()
        if model is None:
            self._set_status(i18n.t(self._lang, "msg_select_model_first"))
            return
        real_source = Path(QUrl(source_path).toLocalFile() or source_path)
        try:
            filename = add_part(model.path, real_source, dest_filename or None)
        except StlOpsError as error:
            self._set_status(i18n.t(self._lang, "msg_add_failed", error=str(error)))
            return
        self._set_status(i18n.t(self._lang, "msg_add_done", name=filename))
        self._refresh_parts()


def launch_qt_gui(ecosystem_root: Path) -> int:
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    app.setApplicationName("HYDRA-UMC-EDITOR-STL")
    app.setApplicationDisplayName("HYDRA-UMC Editor STL")
    project_root = Path(__file__).resolve().parents[2]
    icon = project_root / "images" / "HYDRA_UMC_ICON.ico"
    if not icon.is_file():
        icon = project_root / "images" / "HYDRA_UMC_ICON.svg"
    app.setWindowIcon(QIcon(str(icon)))
    qmlRegisterType(StlGeometry, "HydraUmcEditorStl", 1, 0, "StlGeometry")
    engine = QQmlApplicationEngine()
    bridge = EditorBridge(ecosystem_root)
    engine.rootContext().setContextProperty("backend", bridge)
    qml_path = Path(__file__).with_name("qml") / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()
