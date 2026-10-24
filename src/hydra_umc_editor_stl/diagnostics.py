# =============================================================================
# HYDRA-UMC-EDITOR-STL - Rotating log and guarded slots: diagnostics.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What goes wrong inside a slot of the window must neither crash the window nor vanish: it is written, with its
traceback, to a small rotating log in the home folder, and the person sees a sentence in the status bar that names
the log. The log never holds more than `MAX_BYTES * (BACKUPS + 1)` bytes."""
from __future__ import annotations

import functools
import logging
import logging.handlers
from pathlib import Path
from typing import Any, Callable

LOG_PATH = Path.home() / ".hydra_umc_editor_stl.log"
MAX_BYTES = 256 * 1024
BACKUPS = 2
LOGGER_NAME = "hydra_umc_editor_stl"


def get_logger(path: Path | None = None) -> logging.Logger:
    """The logger of this tool, with its rotating file handler attached once. A folder that cannot be written
    leaves the logger without a file (the guarded slots still report to the status bar)."""
    logger = logging.getLogger(LOGGER_NAME)
    target = path or LOG_PATH
    if any(getattr(handler, "_hydra_log_path", None) == str(target) for handler in logger.handlers):
        return logger
    try:
        handler = logging.handlers.RotatingFileHandler(target, maxBytes=MAX_BYTES, backupCount=BACKUPS, encoding="utf-8", delay=True)
    except OSError:
        return logger
    handler._hydra_log_path = str(target)  # type: ignore[attr-defined]
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def guarded(default: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Wraps a slot of the bridge: any exception it did not handle is logged with its traceback and shown in the
    status bar (`msg_unexpected_error`), and the slot returns `default`. The bridge must have `_set_status` and `_lang`."""

    def decorate(method: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return method(self, *args, **kwargs)
            except Exception as error:  # noqa: BLE001 - last-resort guard of a UI slot
                get_logger().exception("unhandled error in %s", method.__name__)
                try:
                    from . import i18n

                    self._set_status(i18n.t(self._lang, "msg_unexpected_error", error=f"{type(error).__name__}: {error}", log=str(LOG_PATH)))
                except Exception:  # noqa: BLE001 - reporting must not raise either
                    pass
                return default

        return wrapper

    return decorate
