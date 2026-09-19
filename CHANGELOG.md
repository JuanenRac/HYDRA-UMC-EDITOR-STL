# Changelog: HYDRA-UMC-EDITOR-STL 🛠️

All notable changes to this project will be documented in this file. The
version number follows this ecosystem's "odometer" scheme: PATCH +1 on
every real build, rolling into MINOR past 9 (`0.0.9` -> `0.1.0`); MAJOR is
bumped manually only. See `bump_version.py`.

## [0.0.3] - A real 3D viewer with pick-to-select, per-part color, replace and delete

The right column used to be a stack of boxed forms (transform/replace/
remove/add) with no 3D view at all - the project owner's own explicit
request was a real, big 3D viewer with a tool panel, not more forms.

- `stl_geometry.py` (new) - a real `QQuick3DGeometry` that loads an
  actual part's own triangles straight from its STL file (via
  numpy-stl), exposed to QML as `StlGeometry { source: "..." }`. 5 new
  tests.
- Main.qml's right column is now a real Qt Quick 3D `View3D` - every
  editable part of the selected model rendered as its own `Model`,
  mouse-drag orbit + wheel zoom, camera auto-framed on the model's own
  real combined bounding box (`stl_ops.py`'s new `model_bounds()`, 4 new
  tests) so a 400mm robot base and a 5mm screw both frame correctly.
  Click a part in the 3D view (real picking via `View3D.pick()`) to
  select it - same selection the parts list already drove, now two-way.
- `part_colors.py` (new) - a real per-model `part_colors.json` sidecar
  (7 new tests) - a binary STL carries no reliable color of its own, and
  writing one into the mesh bytes wouldn't render anywhere real (this
  ecosystem's own Three.js viewers don't interpret that convention
  either), so this is an honest, real EDITOR-STL-only color annotation
  today. Selected part gets a `ColorDialog` in the new slim tool panel;
  the selected part's own material is drawn lighter in the 3D view so
  it's visible which one is picked.
- The old boxed transform/replace/add forms moved into that same slim
  tool panel instead of being dropped - still real, still functional,
  just no longer the dominant layout.
- Propagating a part's own saved color into HYDRA-UMC-STUDIO/HYDRA-UMC-
  SUITE's own live 3D viewers is real, separate, cross-repo future work
  this does not attempt - see `part_colors.py`'s own header comment.

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
