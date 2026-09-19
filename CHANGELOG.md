# Changelog: HYDRA-UMC-EDITOR-STL 🛠️

All notable changes to this project will be documented in this file. The
version number follows this ecosystem's "odometer" scheme: PATCH +1 on
every real build, rolling into MINOR past 9 (`0.0.9` -> `0.1.0`); MAJOR is
bumped manually only. See `bump_version.py`.

## [0.0.2] - A real About dialog

Added a real About dialog (same visual pattern HYDRA-UMC-UPDATER's own
Main.qml already established for this ecosystem's PC tools), opened via
a new header button - shows the app's own real version
(`EditorBridge.appVersion`), author/email/license, and a link to this
repo's own GitHub page. Full 7-language translations. A dedicated,
larger 3D viewer with per-part selection/color/replace/delete (the
project owner's own explicit next request) is real, substantial future
work, not attempted here.

## [0.0.1] - First real, working scaffold

- `model_catalog.py` - real, read-only discovery of both of the
  ecosystem's own model libraries (HYDRA-UMC-STUDIO's own
  `public/models/`, HYDRA-UMC-SUITE's own `assets/meshes/`), listing
  every real category/model/part folder and file actually present on
  disk, plus each model's own `metadata.json`/`catalog.json` when one
  exists.
- `stl_ops.py` - real STL mutation via `numpy-stl` (the same library
  HYDRA-UMC-SUITE's own `render/mesh.py` already depends on): transform
  (translate/rotate/scale real vertex data), replace, remove and add a
  part. Nothing is ever permanently deleted - `remove_part()`/
  `replace_part()` move the real original file into that model's own
  `.trash/` subfolder first.
- `main.py` - a stdlib+numpy-stl-only `--cli` (`categories`, `models`,
  `parts`, `transform`, `replace`, `remove`, `add`), no Qt import at all
  on that path.
- `qt_gui.py`/`qml/Main.qml` - the default windowed launch, sharing
  HYDRA-UMC-UPDATER's own real visual component set (`GameButton`/
  `GameCombo`/`SectionPanel`, dark cyan/blue/amber/red theme) rather than
  a separately designed UI, per the project owner's own request.
- Real test coverage (`tests/`) for `model_catalog.py`/`stl_ops.py`
  against real, generated STL fixtures - no GUI/hardware needed.
