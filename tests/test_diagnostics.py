# =============================================================================
# HYDRA-UMC-EDITOR-STL - tests for diagnostics.py (rotating log, guarded slots)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

import pytest

from hydra_umc_editor_stl import diagnostics, i18n


@pytest.fixture(autouse=True)
def _fresh_logger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Every test writes to its own file, and the handlers it attached are removed afterwards."""
    monkeypatch.setattr(diagnostics, "LOG_PATH", tmp_path / "editor.log")
    yield
    logger = logging.getLogger(diagnostics.LOGGER_NAME)
    for handler in list(logger.handlers):
        if isinstance(handler, logging.handlers.RotatingFileHandler):  # not the capture handlers of pytest
            handler.close()
            logger.removeHandler(handler)


class _Bridge:
    def __init__(self) -> None:
        self._lang = "en"
        self.status = ""

    def _set_status(self, text: str) -> None:
        self.status = text

    @diagnostics.guarded()
    def boom(self) -> str:
        raise ValueError("the part vanished")

    @diagnostics.guarded("")
    def boom_with_result(self) -> str:
        raise RuntimeError("no value for you")

    @diagnostics.guarded()
    def fine(self, a: int, b: int = 2) -> int:
        return a + b


def _flush() -> None:
    for handler in logging.getLogger(diagnostics.LOGGER_NAME).handlers:
        handler.flush()


def test_a_slot_that_works_is_untouched() -> None:
    bridge = _Bridge()
    assert bridge.fine(1, b=5) == 6
    assert bridge.status == ""
    assert _Bridge.fine.__name__ == "fine"


def test_an_unhandled_error_is_logged_with_its_traceback_and_shown_in_the_status_bar() -> None:
    bridge = _Bridge()
    assert bridge.boom() is None
    _flush()
    assert "ValueError: the part vanished" in bridge.status
    assert str(diagnostics.LOG_PATH) in bridge.status
    text = diagnostics.LOG_PATH.read_text(encoding="utf-8")
    assert "unhandled error in boom" in text
    assert "Traceback" in text and "the part vanished" in text


def test_a_slot_that_returns_a_value_gets_its_default() -> None:
    bridge = _Bridge()
    assert bridge.boom_with_result() == ""
    assert "RuntimeError" in bridge.status


def test_the_report_itself_cannot_raise() -> None:
    class Broken:
        _lang = "en"

        @diagnostics.guarded("fallback")
        def run(self) -> str:
            raise OSError("disk")

    assert Broken().run() == "fallback"  # there is no _set_status: the slot still returns its default


def test_the_log_is_rotated_and_never_grows_without_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(diagnostics, "MAX_BYTES", 2000)
    logger = diagnostics.get_logger()
    for i in range(400):
        logger.info("line %04d %s", i, "x" * 60)
    _flush()
    files = sorted(p.name for p in tmp_path.glob("editor.log*"))
    assert files == ["editor.log", "editor.log.1", "editor.log.2"]
    assert sum(p.stat().st_size for p in tmp_path.glob("editor.log*")) < 3 * 2000 + 500
    assert "line 0399" in diagnostics.LOG_PATH.read_text(encoding="utf-8")


def test_asking_for_the_logger_twice_attaches_one_handler() -> None:
    first = diagnostics.get_logger()
    second = diagnostics.get_logger()
    assert first is second
    files = [h for h in first.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(files) == 1


def test_a_log_folder_that_cannot_be_written_leaves_the_slots_working(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    blocker = tmp_path / "a-file"
    blocker.write_text("x")
    monkeypatch.setattr(diagnostics, "LOG_PATH", blocker / "log.txt")  # a folder that is a file
    bridge = _Bridge()
    assert bridge.boom() is None
    assert "ValueError" in bridge.status


def test_every_language_has_the_sentence_and_it_names_the_error_and_the_log() -> None:
    for lang in i18n.TRANSLATIONS:
        text = i18n.t(lang, "msg_unexpected_error", error="E", log="L")
        assert "E" in text and "L" in text and "{" not in text, lang
