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
import tempfile
from pathlib import Path

from PySide6.QtCore import Property, QObject, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from . import i18n, settings
from . import __version__
from .assembly import assembled_bounds, assembled_transforms, placement_matrix
from .catalog_push import CatalogPushError, ServerClient
from .model_catalog import is_independent_parts_category, list_categories, list_models, load_model
from .part_colors import DEFAULT_COLOR, load_part_colors, save_part_color
from .stl_geometry import StlGeometry
from .stl_ops import StlOpsError, add_part, model_bounds, remove_part, replace_part, transform_part, unique_part_filename


class _PushThread(QThread):
    """Runs ServerClient.login()+push_model() off the UI thread - both are
    blocking urllib calls (this app has no asyncio event loop at all,
    unlike SUITE/EDITOR-URDF), same reasoning EDITOR-URDF's own
    ui/panels/upload_panel.py already documents for its equivalent
    _ServerCallThread."""

    finished_ok = Signal(str)  # the server-assigned slug
    finished_error = Signal(str)

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn

    def run(self) -> None:
        try:
            self.finished_ok.emit(self._fn())
        except CatalogPushError as e:
            self.finished_error.emit(str(e))
        except Exception as e:  # noqa: BLE001 - last-resort guard, same as upload_panel.py's own thread
            self.finished_error.emit(str(e))


class EditorBridge(QObject):
    ecosystemRootChanged = Signal()
    languageChanged = Signal()
    librariesChanged = Signal()
    categoriesChanged = Signal()
    modelsChanged = Signal()
    partsChanged = Signal()
    selectionChanged = Signal()
    statusChanged = Signal()
    pushStateChanged = Signal()
    clipboardChanged = Signal()

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
        self._push_busy = False
        self._push_status = ""
        self._push_thread: _PushThread | None = None
        self._clipboard_path: Path | None = None
        self._clipboard_label = ""
        self._assembled_view = True
        self._has_assembly = False
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

    @Property(bool, notify=selectionChanged)
    def isIndependentPartsCategory(self) -> bool:
        """True for heatedbeds/vacuum-tables/racks - real, independent
        size/variant options, never one real assembly - the 3D viewer
        uses this to show only the operator's own current selection
        instead of every variant piled on top of the others at the same
        origin (see model_catalog.py's own header comment)."""
        return is_independent_parts_category(self._category)

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

    @Property(bool, notify=partsChanged)
    def hasAssembly(self) -> bool:
        """True when HYDRA-UMC-SUITE's own kinematics can place this
        model's parts at the machine's home pose (see assembly.py)."""
        return self._has_assembly

    @Property(bool, notify=partsChanged)
    def assembledView(self) -> bool:
        return self._assembled_view

    @Slot(bool)
    def setAssembledView(self, value: bool) -> None:
        if value == self._assembled_view:
            return
        self._assembled_view = value
        self._refresh_parts_preserving_selection()

    @Property(str, notify=selectionChanged)
    def selectedPart(self) -> str:
        return self._selected_part

    @Slot(str)
    def selectPart(self, filename: str) -> None:
        self._selected_part = filename
        self.selectionChanged.emit()

    @Property("QVariantList", notify=selectionChanged)
    def selectedPartCenter(self) -> list[float]:
        """Real combined bounding-box center of ONLY the currently
        selected part (unlike `boundsCenter`, which frames the whole
        model) - where the move gizmo anchors itself, so it sits on the
        actual selected piece rather than the model's own overall
        center."""
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            return [0.0, 0.0, 0.0]
        box = model_bounds(model.path, [self._selected_part])
        if box is None:
            return [0.0, 0.0, 0.0]
        return [(a + b) / 2 for a, b in zip(box.min_xyz, box.max_xyz)]

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
            self._has_assembly = False
        else:
            colors = load_part_colors(model.path)
            placements = None
            if not is_independent_parts_category(self._category):
                placements = assembled_transforms(self._ecosystem_root, self._category, self._model, model.path)
            self._has_assembly = placements is not None
            show_assembled = self._has_assembly and self._assembled_view
            identity = {"asmMatrix": []}
            self._parts = [
                {
                    "filename": p.filename,
                    "sizeBytes": p.size_bytes,
                    "editable": p.editable,
                    "absolutePath": str((model.path / p.filename).resolve()) if p.editable else "",
                    "color": colors.get(p.filename, DEFAULT_COLOR),
                    **(
                        {"asmMatrix": placement_matrix(placements[p.filename])}
                        if placements is not None and p.filename in placements else identity
                    ),
                }
                for p in model.parts
            ]
            editable_filenames = [p.filename for p in model.parts if p.editable]
            box = None
            if show_assembled:
                world = assembled_bounds(model.path, placements)
                if world is not None:
                    from .stl_ops import BoundingBox
                    box = BoundingBox(min_xyz=world[0], max_xyz=world[1])
            if box is None:
                box = model_bounds(model.path, editable_filenames)
            if box is not None:
                self._bounds_center = [(a + b) / 2 for a, b in zip(box.min_xyz, box.max_xyz)]
                diagonal = sum((b - a) ** 2 for a, b in zip(box.min_xyz, box.max_xyz)) ** 0.5
                # Half the real diagonal, with only a tiny floor: parts can
                # be authored in millimeters OR meters (a 0.5 m robot is
                # radius ~0.3 here), so a floor tuned for millimeters would
                # push the camera far away from a meter-scale model.
                self._bounds_radius = max(diagonal / 2, 1e-3)
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

    # --- copy / paste / cut ----------------------------------------------
    # A real clipboard, not just a filename reference: copySelectedPart()
    # snapshots the part's own bytes into a real temp file right away, so
    # a later edit or removal of the original never corrupts a pending
    # paste - the same "independent snapshot" semantics an OS clipboard
    # already gives you for any other copy.

    @Property(bool, notify=clipboardChanged)
    def hasClipboard(self) -> bool:
        return self._clipboard_path is not None

    @Property(str, notify=clipboardChanged)
    def clipboardLabel(self) -> str:
        return self._clipboard_label

    @Slot()
    def copySelectedPart(self) -> None:
        model = self._load_selected_model()
        if model is None or not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        source = model.path / self._selected_part
        try:
            data = source.read_bytes()
        except OSError as error:
            self._set_status(i18n.t(self._lang, "msg_copy_failed", error=str(error)))
            return
        suffix = Path(self._selected_part).suffix or ".stl"
        fd, tmp_name = tempfile.mkstemp(suffix=suffix)
        tmp_path = Path(tmp_name)
        with open(fd, "wb") as handle:
            handle.write(data)
        self._clipboard_path = tmp_path
        self._clipboard_label = self._selected_part
        self.clipboardChanged.emit()
        self._set_status(i18n.t(self._lang, "msg_copy_done", name=self._selected_part))

    @Slot()
    def pasteClipboard(self) -> None:
        model = self._load_selected_model()
        if model is None:
            self._set_status(i18n.t(self._lang, "msg_select_model_first"))
            return
        if self._clipboard_path is None or not self._clipboard_path.is_file():
            self._set_status(i18n.t(self._lang, "msg_clipboard_empty"))
            return
        dest_name = unique_part_filename(model.path, self._clipboard_label or self._clipboard_path.name)
        try:
            filename = add_part(model.path, self._clipboard_path, dest_name)
        except StlOpsError as error:
            self._set_status(i18n.t(self._lang, "msg_add_failed", error=str(error)))
            return
        self._set_status(i18n.t(self._lang, "msg_paste_done", name=filename))
        self._refresh_parts()

    @Slot()
    def cutSelectedPart(self) -> None:
        if not self._selected_part:
            self._set_status(i18n.t(self._lang, "msg_select_part_first"))
            return
        cut_name = self._selected_part
        self.copySelectedPart()
        if self._clipboard_path is not None and self._clipboard_label == cut_name:
            self.removeSelectedPart()

    # --- push to a running server's own model-submission catalog --------

    @Property(bool, notify=pushStateChanged)
    def pushBusy(self) -> bool:
        return self._push_busy

    @Property(str, notify=pushStateChanged)
    def pushStatus(self) -> str:
        return self._push_status

    @Slot(str, int, str, str, str, bool)
    def pushToServer(self, host: str, port: int, username: str, password: str, category: str, overwrite: bool) -> None:
        model = self._load_selected_model()
        if model is None:
            self._push_status = i18n.t(self._lang, "msg_select_model_first")
            self.pushStateChanged.emit()
            return
        if self._push_busy:
            return  # a push is already in flight - same one-at-a-time guard every other mutation here gets for free by being synchronous

        def do_push() -> str:
            client = ServerClient(host, port)
            client.login(username, password)
            return client.push_model(model, category or self._category, overwrite)

        self._push_busy = True
        self._push_status = ""
        self.pushStateChanged.emit()
        thread = _PushThread(do_push, self)
        self._push_thread = thread
        thread.finished_ok.connect(self._on_push_ok)
        thread.finished_error.connect(self._on_push_error)
        thread.finished.connect(self._on_push_thread_done)
        thread.start()

    def _on_push_ok(self, slug: str) -> None:
        self._push_busy = False
        self._push_status = i18n.t(self._lang, "msg_push_done", slug=slug)
        self.pushStateChanged.emit()

    def _on_push_error(self, message: str) -> None:
        self._push_busy = False
        self._push_status = i18n.t(self._lang, "msg_push_failed", error=message)
        self.pushStateChanged.emit()

    def _on_push_thread_done(self) -> None:
        # Same real "only drop the reference once QThread.finished confirms
        # run() has actually returned" discipline EDITOR-URDF's own
        # upload_panel.py documents for its equivalent threads.
        if self._push_thread is not None:
            self._push_thread.deleteLater()
            self._push_thread = None


def launch_qt_gui(ecosystem_root: Path) -> int:
    # The Windows native style ignores custom backgrounds; Basic honours them.
    QQuickStyle.setStyle("Basic")
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
