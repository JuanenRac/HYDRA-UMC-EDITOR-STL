# Changelog: HYDRA-UMC-EDITOR-STL 🛠️

All notable changes to this project will be documented in this file. The
version number follows this ecosystem's "odometer" scheme: PATCH +1 on
every real build, rolling into MINOR past 9 (`0.0.9` -> `0.1.0`); MAJOR is
bumped manually only. See `bump_version.py`.

## [0.1.2] - The move gizmo only exists where its axes are the part's own

- The move gizmo is hidden and cannot start a drag while the assembled view is on,
  including when the move tool was already selected before switching views. In the
  assembled view a part sits in world coordinates while the transform is applied in
  the part's own coordinates, so the gizmo only works in the raw view where both agree.

## [0.1.1] - Basic Qt style

- The app now uses Qt Quick's Basic style. The native Windows style ignores
  custom control backgrounds and logged a warning for each one.

## [0.1.0] - Machines and robots open correctly assembled; right-drag pans

- **Assembled view fixed.** Rendering the real viewer showed machines upside
  down and robot links displaced: Quick 3D did not apply the placement's
  quaternion the way the source kinematics define it (and for a symmetric
  rotation such as the UR arms, conjugating it changed nothing). The
  placement is now baked into each part's vertices with a plain matrix
  product (`StlGeometry.placement`), and the model keeps an identity
  transform. Checked against renders of the CNC, PnP, UR5e and AR4.
- **Right mouse button pans.** Holding the right button and dragging moves
  the view through the 3D space; the left button still orbits, the wheel
  zooms. The pan resets when another model is loaded.

## [0.0.9] - Delete a part straight from the left-hand list

- Every row of the parts list now has a trash button. It selects the row's
  part and opens the same confirmation as the toolbar's delete; the STL is
  moved to `.trash/`, never erased permanently.

## [0.0.8] - Robots, CNC, PnP and laser now open already assembled

Those models' STL parts are each stored in their own local link frame, so
they used to open as a pile. `assembly.py` now asks the sibling
HYDRA-UMC-SUITE checkout's own kinematics (`render/kinematics.py`,
`render/pnp_rig.py` - read, never copied) where every link sits at the
machine's home pose and shows the parts there (display only; nothing is
written to any STL). A new "Assembled view" toolbar button switches back
to the raw parts, which is where Move/Pin editing happens. Also fixed the
camera/gizmo size floors, which assumed millimeter-scale parts and hid
meter-scale ones (a 0.5 m robot). With no SUITE checkout next to this
one, or an unknown model, it simply keeps showing the raw parts.

## [0.0.7] - Icon toolbar that really floats

Feedback on 0.0.6: the toolbar sat fixed in a corner and used text
buttons. It is now a compact, semi-transparent panel you drag anywhere
inside the 3D view by its grip handle (kept within the view's bounds),
and every button is an icon (bundled SVGs in `qml/icons/`) with the
translated name as a hover tooltip, so all 7 languages still read
correctly.

## [0.0.6] - Floating viewer toolbar, move gizmo, and one-at-a-time variant view

Live report from the project owner: heated beds, vacuum tables and racks
showed one giant plate with every other variant piled underneath it, and
robots looked badly assembled. Those three categories hold independent,
mutually exclusive size variants (never one assembly), while a robot/CNC/
PnP/laser model's STL parts are each stored in their own local frame -
this tool has no joint data, so assembling them is a manual job.

- Heated beds, vacuum tables and racks (`is_independent_parts_category()`)
  now show only the selected variant in the 3D view instead of every one
  overlapping at the same origin.
- New floating toolbar inside the 3D view: Select, Move, Edit
  (rotate/scale), Color, Add, Delete, Pin, Copy, Paste, Cut.
- Move shows a real draggable 3-axis gizmo on the selected part (screen-
  space axis drag, live preview only); Pin writes the accumulated move plus
  the Edit rotate/scale permanently through the existing
  `transform_part()` (original kept in `.trash/`), so a badly assembled
  robot can be fixed once by hand and stays fixed.
- Copy snapshots the part's bytes; Paste adds it under a non-colliding
  name (`<name>_copy.stl`, `_copy2`, ...), also into a different model;
  Cut is copy + move to `.trash/`.
- Honest caveat: the gizmo's appearance and drag feel could only be
  checked headlessly (loads with no QML errors), not visually - its size
  and calibration may need tuning on a real display.

## [0.0.5] - Real bug: the 3D viewer showed nothing at all

Live report from the project owner: the 3D view stayed completely
blank, even with a model's parts loaded (the parts list itself worked
fine). Root cause: the orbit camera's own `parent.parent`/
`parent.parent.parent` chains in `qml/Main.qml` were one hop short of
the `Item` that actually owns `camPitch`/`camYaw`/`camZoom` (the camera
lives inside `View3D` -> `Node`, one level deeper than the sibling
`MouseArea` those same property names were copied from) - both the
camera's own position and rotation silently evaluated against
`undefined`, producing a `NaN` transform the renderer had nothing valid
to draw. Fixed by giving that `Item` a real `id` and referencing it
directly everywhere instead of a fragile parent-chain hop count.

## [0.0.4] - Push an edited/added model to a running server's catalog

Until now this tool only ever edited STUDIO's/SUITE's own bundled model
libraries directly on local disk - there was no way to hand a model over
to a running HYDRA-UMC-SERVER's own live model-submission catalog (the
same real `POST /api/models/submit` HYDRA-UMC-EDITOR-URDF already uses
for URDF robots). That endpoint's contract is URDF-shaped, but the parts
this tool edits are plain, un-jointed STL meshes - closed the gap by
wrapping a model's own editable parts in the smallest real URDF that
contract already accepts (one root link, one child link per part joined
by a `fixed` joint at the identity origin, since each part's actual
position is already baked into its own STL vertices).

- `catalog_push.py` (new) - `build_assembly_urdf()` + `ServerClient`
  (login, then push, mirroring EDITOR-URDF's own client).
- New "Push to server..." dialog (host/port/admin login/category/
  overwrite) and `--cli push` subcommand, both routed through the same
  real `catalog_push.py`.
- Runs on a background `QThread` (this app has no asyncio event loop),
  same discipline EDITOR-URDF's own upload panel already documents.

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
