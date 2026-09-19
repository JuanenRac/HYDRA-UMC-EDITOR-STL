# Contributing to HYDRA-UMC-EDITOR-STL 🦾

We welcome contributions to the STL model editor of the HYDRA-UMC
platform.

## Technology Stack

- **Language**: Python 3.10+.
- **Mesh I/O**: `numpy-stl` - the same real STL read/write library
  HYDRA-UMC-SUITE's own `render/mesh.py` already depends on for the
  exact same file format. Do not introduce a second, competing STL
  parser/writer.
- **GUI**: PySide6/Qt Quick, optional (`pip install -e ".[gui]"`) -
  `--cli` and the whole `model_catalog.py`/`stl_ops.py` core stay
  importable and usable with zero Qt dependency, so a headless machine
  can still browse/edit the model libraries.

## Guidelines

1. **`model_catalog.py` is read-only discovery, `stl_ops.py` is the only
   place that mutates a file on disk.** Don't add a second path that
   writes an STL/metadata file outside `stl_ops.py`'s own functions.
2. **Never permanently delete a real file.** `remove_part()`/
   `replace_part()` move the original into that model's own `.trash/`
   subfolder instead of calling `unlink()`/overwriting without a backup.
   Any new destructive operation must follow the same pattern.
3. **`qt_gui.py` calls the exact same functions `--cli` calls** -
   `model_catalog.load_model()`, `stl_ops.transform_part()`/
   `replace_part()`/`remove_part()`/`add_part()`. Do not duplicate any
   of that logic directly in `qt_gui.py` or in QML.
4. **The two real model libraries this tool edits**
   (`model_catalog.LIBRARIES`) are HYDRA-UMC-STUDIO's own
   `public/models/` and HYDRA-UMC-SUITE's own `assets/meshes/` - keep
   both in sync if either repo's own category layout changes (see that
   constant's own header comment).
5. **The Qt Quick shell reuses HYDRA-UMC-UPDATER's own visual component
   set** (`GameButton`/`GameCombo`/`SectionPanel`, the dark cyan/blue/
   amber/red theme) - a new panel should match that style, not introduce
   a new one.
