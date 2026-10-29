# Changelog

All notable changes to this project are documented here.

## [Unreleased]

- **The layout of the README is checked in the CI:** the validator runs `tools/universal_readme_check.py` and lists, as a warning, what differs from the universal layout of the README.

## [0.1.7] - A mesh check before a push and restore from `.trash/` and empty it

- **A mesh check before a push.** `mesh_check.py` reads each part and reports triangles without area, coordinates that are not numbers, a mesh that is not closed (edges that belong to one triangle or to more than two), faces that point inwards, stored normals that disagree with the winding of most faces and a size that looks like the wrong unit; `push_warnings()` lists the findings per part before anything is uploaded. Vectorised with numpy; tested on a cube in both orientations, with a missing face, with damaged triangles and in the wrong unit.
- **Restore from `.trash/` and empty it.** A new window dialog lists what is in the selected model's `.trash/` (newest first), restores an entry under its original name (a free `_copyN` name when that one is taken, so nothing is overwritten) and empties the trash after an explicit confirmation. Emptying never deletes for good: the files move to `.trash-emptied/<stamp>/`. Texts in the eight languages.
- **Bounding boxes are measured once.** `model_bounds()` and `assembled_bounds()` parsed every STL of a model again at each selection (seconds with the larger models). The box of a part is kept by path, modification time and size (at most 512 parts), so a part that is edited, replaced or transformed is read again and an unreadable one is tried again when its file changes.
- **An error inside a window slot no longer vanishes or crashes the window.** Every slot of the bridge is guarded: the traceback goes to a rotating log in the home folder (`.hydra_umc_editor_stl.log`, 256 KiB, two backups) and the status bar says what happened and where the log is, in the eight languages.
- The maturity is `scaffolding` in the manifest and the eight READMEs, as `docs/MATURITY_CRITERIA.md` already says: of its four exit criteria only the mesh validation is verified by tests today (units and dimensional limits, recorded provenance and a version check in the build test are not), so the project does not claim `functional` yet.
- Building no longer changes the version; raising it is the explicit `bump` command (`python tools/hydra_project_tool.py bump`). The build scripts only report the version they built, and CI fails if a build script runs a bump.
- The build and run scripts use the Python of the `.venv` directly instead of an activate script, and create the venv with the `py` launcher when there is one; CI fails if a script activates a venv.
- The banner follows the animated style of the ecosystem banners, with the name, the kind and the technologies of the project.
- Added `tools/hydra_project_tool.py`: the same `validate`, `test`, `version`, `status` and `bump` commands in every repository. The checks run with `HYDRA_UMC_CI=1` and fail if the version changes; only `bump` changes it.

## [0.1.6] - Damaged files and odd server answers no longer crash the editor

- **Saved files:** a settings file, a `part_colors.json` or a model `metadata.json` that is not valid UTF-8 made the editor raise instead of starting with an empty value; all three are now treated like any other damaged file.
- **Truncated STL files:** a binary STL cut short (its header promises more triangles than the file holds) was read without complaint as a smaller mesh, so transforming it saved a shorter part, and adding or replacing a part with it was accepted. Such files are now refused, and the original is left untouched.
- **Server push:** a login or push answer that is not a JSON object (a proxy or captive-portal page, `null`, a list), an error body that is not an object, or a token or slug that is not text, ended in an unhandled exception; each is now a readable push error.
- 108 new tests (194 in all, 82 % line coverage, up from 61 %): the `--cli` commands, part-name confinement and links that point outside the model, finite-value checks of transforms, backups in the trash, SUITE placements and their quaternions, STL geometry placement, and a local server answering badly.

## [0.1.5]

- Build version synchronized with `hydra-umc.project.json` and the repository-native version source.
- The licence is written as GPL-3.0-or-later in every header and in the package metadata.

## [0.1.4] - Backups are not parts, part names stay inside the model, honest push

- **Backup copies are no longer parts:** every transform, replace or remove leaves a copy in the model's `.trash/` folder, and the part list included those copies, so the viewer drew old versions on top of the real part and a push uploaded them. Hidden folders are skipped when a model is loaded.
- **Part names stay inside the model:** transform, replace, remove and add refuse absolute names, `..` segments and links that lead outside the model folder, and `add` only accepts `.stl` names; a category or model name that climbs out of the library is not a model.
- **Non-finite values are refused:** a NaN or infinite translation, rotation or scale (or a result that would overflow) is rejected before the part is touched.
- **Safer writes:** the STL, `part_colors.json` and the settings file are written to a temporary file and replaced atomically; a corrupt or truncated STL and file-system errors are reported as messages instead of leaving the operation half done.
- **Copying a part from a sub-folder** (`parts/foo.stl`) now creates `parts/foo_copy.stl` instead of a file in the model root.
- **Push is honest about what it does:** parts that are not `.stl` are reported, an upload above the server's 50 MB limit is refused before it is sent, and robots or machines (whose parts are stored in their own link frame) trigger a warning because they arrive without joints. The password can come from `HYDRA_UMC_PASSWORD` or a prompt instead of `--password`, and `--host https://...` is accepted.
- **Docs:** README (all languages), CLI reference and manifest describe the push limits and the transform order, and the push messages exist in all 8 languages (86 tests).

## [0.1.3] - Portuguese interface; the pure-logic tests no longer need Qt

- **Portuguese interface:** `pt` joins the other seven languages in `i18n.py` (83 keys with the same placeholders as English) and the language menu offers `Português`. A README_por.md joins the other seven.
- **Translation tests:** `tests/test_i18n.py` checks that every language has exactly the English keys and the same `{placeholders}`, that the language menu lists every table, and that an unknown language or key falls back safely.
- **Qt-free test run:** `test_stl_geometry.py` and `test_qt_gui.py` skip themselves when PySide6 (the optional `gui` extra) is not installed, so `pip install .[dev]` runs the whole pure-logic suite (catalog discovery, STL operations, part colors, catalog push) on a machine with no Qt. 74 tests in all.

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
