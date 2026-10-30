<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Desktop editor for the STL model libraries of HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 📦 HYDRA-UMC-EDITOR-STL

<p align="center">🇺🇸 <b>English</b> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 📦 Browse and Edit the HYDRA-UMC Ecosystem's Own Real STL Model Libraries

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="Core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="Desktop">
  <img src="https://img.shields.io/badge/Tests-222%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.1.8-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-scaffolding-FFB020.svg" alt="Maturity">
</p>

---

**Honesty check - what actually runs today:** `model_catalog.py` (real,
read-only discovery of both model libraries), `stl_ops.py` (real STL
mutation via `numpy-stl` - transform/replace/remove/add, plus
`model_bounds()` for the 3D viewer's own camera framing),
`part_colors.py` (real per-part color sidecar), `stl_geometry.py`
(real Qt Quick 3D geometry loading) and `catalog_push.py` (real
assembly-URDF generation plus a real HTTP client for
`POST /api/models/submit`) are all tested against real, generated STL
fixtures and a real, session-scoped `QGuiApplication` where needed
(`pytest tests/`, 222 passing cases) and have been smoke-tested end to end
against this ecosystem's own real
`HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` checkouts (`--cli categories`/
`models`/`parts` against the real trees; `transform`/`remove` against a
throwaway copy, never the real checkout). `qt_gui.py`'s `EditorBridge`
itself is also directly tested (color slot, selection preserved across
a color change). `qml/Main.qml` loads and renders with no QML errors
(verified headlessly with `QT_QPA_PLATFORM=offscreen`, including with a
real model's parts loaded into the 3D viewer), but the QML scene graph
itself has no automated test of its own - driving a real Qt event loop
isn't attempted here, the same honesty boundary HYDRA-UMC-UPDATER's own
README already draws for its own Qt Quick shell.

---

> **Safety and security status:** this ecosystem is not a certified safety system. There is no hardware E-STOP path, no firmware-enforced limits or interlocks and no verified motion command yet; firmware images are checked with CRC-32 and an Ed25519 signature, and a release build refuses the published development keys (the tool heads and expansion boards behind the relay still run URTC bootloaders, which take a shared-key HMAC-SHA256 instead of a signature); TLS and mutual TLS are optional and off by default; no custom board has been populated or tested yet. Read the [security baseline](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) and the [threat model](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) before relying on any statement here for the safety of a person.

---

## 📋 At a glance

| | |
|---|---|
| Version | `0.1.8` |
| Maturity | Scaffolding |
| Tests | 222 (`python -m pytest tests -q`) |
| Stack | Python / PySide6 / Qt Quick / numpy-stl |
| Target | The PC of the person using it |
| On real hardware | Not applicable: nothing here runs on hardware |

**Jump to:** [Overview](#-overview) · [Architecture](#-architecture) · [Security & Safety](#-security--safety) · [Interfaces](#-interfaces) · [Configuration](#-configuration) · [Quick start](#-quick-start) · [Testing](#-testing) · [Troubleshooting](#-troubleshooting) · [Repository Structure](#-repository-structure) · [Related Projects](#-related-projects)

## 🚦 Project status

Each line is one part of this repository and the light says how far it is today. It is written from what the repository can show (tests, builds, runs), not from what is planned.

🟢 Done and verified · 🟡 Works, with known limits · 🟠 Partly done or not verified yet · 🔴 Not done or not working

| Area | State | What it means here |
|---|---|---|
| Software | 🟠 | Structure and first pieces only; most of the work is still to do |
| Tests | 🟡 | 222 automated tests, run on every change |
| Real hardware | 🟡 | Not applicable: nothing here runs on hardware |
| Documentation | 🟡 | README in eight languages, checked against the manifest on every change |

## 🎯 Overview

HYDRA-UMC-EDITOR-STL is a small desktop tool - windowed GUI by default,
full CLI with `--cli` - for editing the real STL parts that make up
every robot/machine model HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE ship.
Both of those apps reorganized their own model folders into
the same real category layout (`robots-5-dof`/`robots-6-dof`/
`robots-7-dof`, `machine-pnp`/`machine-cnc`/`machine-laser`,
`heatedbeds`/`racks`/`vacuum-tables`, each model with its own
`metadata.json` alongside its `ATTRIBUTION.txt`) - this tool reads that
exact real layout, not a separate copy or a database of its own.

A real Qt Quick 3D viewer renders every editable part of the selected
model (`stl_geometry.py`, a real `QQuick3DGeometry` loading each part's
own triangles straight from its STL file) - drag to orbit, wheel to
zoom, click a part to select it (real `View3D.pick()`, not a hit-test
guess). The camera frames itself on the model's own real combined
bounding box (`stl_ops.py`'s `model_bounds()`), so a 400mm robot base
and a 5mm screw both frame correctly.

Six real operations, each backed by real file I/O against the actual
checkout on disk:

- **Transform** - translate/rotate/scale a part's own real vertex data
  (via `numpy-stl`, the same library HYDRA-UMC-SUITE's own
  `render/mesh.py` already depends on) and save it back in place.
- **Change color** - a real per-part color annotation (`part_colors.json`,
  a sidecar this tool owns) shown in the 3D view - a binary STL carries
  no reliable color of its own, so this sidecar is the real source of
  truth. HYDRA-UMC-STUDIO's own `hooks/usePartColors.ts` and
  HYDRA-UMC-SUITE's own `render/part_colors.py` both read the exact same
  file back, so a color saved here reaches their live 3D viewers too,
  not just this tool's own preview.
- **Replace** - overwrite a part with another real STL file.
- **Remove** - take a part out of a model.
- **Add** - bring a new real STL file into a model.
- **Push to server** - submit the selected model's own current editable
  parts to a running HYDRA-UMC-SERVER's real model-submission catalog
  (`catalog_push.py`, `POST /api/models/submit` - admin login required,
  same as HYDRA-UMC-EDITOR-URDF's own equivalent feature). Since that
  endpoint's own contract is URDF-shaped, this wraps the parts in the
  smallest real URDF it accepts: one root link plus one un-jointed
  (`fixed`) child link per part, since each part's actual position is
  already baked into its own STL vertices - never a synthetic pose.
- **Floating viewer toolbar** - Select, Move (a real draggable 3-axis gizmo), Edit (rotate/scale), Color, Add, Delete, Pin (bakes the move/rotate/scale permanently), Copy, Paste and Cut, right inside the 3D view. Heated beds, vacuum tables and racks are independent size variants, so the viewer shows only the selected one instead of piling them up.
- **Assembled view** - robots, CNC, PnP and laser models open already assembled at their home pose (read from HYDRA-UMC-SUITE's own kinematics next to this checkout, display only); a toolbar button switches to the raw parts for editing.

**Limits of the push and of the transform:** only `.stl` parts are uploaded (the others are reported), the whole upload must fit the server's 50 MB request limit, and the model is only stored in the server's catalog (HYDRA-UMC-STUDIO does not read it yet). The identity pose is correct for independent pieces (heated beds, racks, vacuum tables); the parts of a robot or machine are stored in their own link frame, so they arrive stacked at the origin without joints. Prefer an `https://` host (or `HYDRA_UMC_PASSWORD` / the password prompt instead of `--password`). A transform scales first, then rotates about X, Y and Z, then translates, and the rotation is about the file's origin, not about the centre of the part.

**Nothing is ever permanently deleted.** A remove or a replace moves the
real original file into that model's own `.trash/` subfolder first -
the same "never destroy, move aside instead" discipline this ecosystem's
own internal working conventions already follow, applied here as a real
product feature, not just an internal habit.

## 🧩 Role in HYDRA-UMC

**HYDRA-UMC-EDITOR-STL** is the desktop tool that edits the real STL parts of every robot and machine model that HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE ship. It reads their two model folders as they are, shows a model in a Qt Quick 3D viewer, and transforms, recolours, replaces, removes or adds a part on disk, moving the original aside instead of deleting it. A finished model can be pushed to the model catalogue of a HYDRA-UMC-SERVER.

## 🏛️ Architecture

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-EDITOR-STL architecture" width="100%">
</p>

### ARCHITECTURE & DESIGN DECISIONS

- **Two real libraries, one discovery module.** `model_catalog.py`'s own
  `LIBRARIES` constant names both real trees this tool edits
  (`HYDRA-UMC-STUDIO/public/models/`, `HYDRA-UMC-SUITE/assets/meshes/`) -
  adding a third library later means adding one entry there, not a
  second discovery implementation.
- **`stl_ops.py` is the only place that ever mutates a file.**
  `model_catalog.py` stays strictly read-only; both `--cli` and the Qt
  Quick bridge call the exact same `transform_part()`/`replace_part()`/
  `remove_part()`/`add_part()` functions, so the GUI can never do
  anything the CLI itself couldn't.
- **A real STL, not just a filename ending in `.stl`.** `is_real_stl()`
  actually parses a candidate replacement/addition with `numpy-stl`
  before it's ever copied into a real model folder - and, a real gap
  found writing this project's own tests, also rejects a **0-triangle**
  parse result: `numpy-stl`'s own ASCII fallback path does not raise on
  arbitrary garbage bytes, it silently parses them as an empty mesh, so
  a bare try/except alone would have let a completely non-STL file
  through.
- **Qt Quick GUI by default, `--cli` for headless.** `main.py` only
  imports PySide6 on the non-`--cli` path, so `--cli categories`/
  `models`/`parts`/`transform`/`replace`/`remove`/`add` work on a
  machine with no display or Qt runtime installed at all.
- **The same real visual shell as HYDRA-UMC-UPDATER.** `qml/Main.qml`
  reuses that project's own `GameButton`/`GameCombo`/`SectionPanel`
  components and dark cyan/blue/amber/red theme verbatim, per the
  project owner's own request - a new PC tool in this ecosystem should
  feel like the same tool, not a separately designed one.
- **Ecosystem root, not a hardcoded path.** Like HYDRA-UMC-UPDATER's own
  workspace root, this project's own parent directory is the default
  (`main.py`'s `default_ecosystem_root()`), always overridable
  (`--root` on `--cli`, "Browse" in the GUI) and remembered across GUI
  launches (`settings.py`).

## 🔒 Security & Safety

| Threat | Defence | Where |
|---|---|---|
| Losing a part when it is replaced or removed | The original is moved to the `.trash/` folder of the model first and never deleted; restoring is possible, and emptying the trash needs an explicit confirmation | `stl_ops.py` |
| A file that is not an STL, or a part name that leaves the model folder | A replacement or addition is parsed first and refused when it has no triangles or is cut short; a part name must be a plain `.stl` file name inside the model folder; a transform that would give non-finite vertices changes nothing | `stl_ops.py`, `mesh_check.py` |
| The server password in the shell history or the process list | `--password` is not recommended; without it the password is read from `HYDRA_UMC_PASSWORD` or asked for without echo; an `https://` host avoids sending it in plain text | `main.py`, `catalog_push.py` |
| An upload that is too large or hangs | The whole upload must fit in 49 MiB (the server limit is 50 MB) and every request has a 20 s time limit; only `.stl` parts are sent and the others are reported | `catalog_push.py` |
| Log files that grow or hold data | One rotating log in the home folder of 256 KiB with two copies | `diagnostics.py` |

**What it never does:** edit anything outside the model folders you point it at, or delete a part for good. The push to a server was written against its documented contract and has not been tried against a real server.

Sending a robot or machine model to a catalogue is refused by default, because its parts would arrive stacked at the origin; only categories of independent parts (beds, racks) go through. The refusal says why, and the parts that are not `.stl` are reported.

## 🔌 Interfaces

| Topic or route | What it carries |
|---|---|
| `--cli categories \| models \| parts <library> [...]` | lists what is there: the categories, the models of a category, the part files of a model (`--json` for machines); the library is `studio` or `suite` |
| `--cli transform <library> <category> <model> <part> [--tx --ty --tz --rx --ry --rz --scale]` | translate, rotate and scale one part in place: it scales first, then rotates about X, Y and Z, then translates, about the origin of the file |
| `--cli replace \| remove \| add` | replace a part with another STL, move one to `.trash/`, or bring in a new STL (`--dest-filename` renames it) |
| `--cli push <library> <category> <model> --host --username` | sends the editable parts of a model to `POST /api/models/submit` of a server (administrator login; `--port` 3000 by default, `--server-category`, `--overwrite`) |
| `--root <folder>` | the ecosystem root that holds `HYDRA-UMC-STUDIO` and `HYDRA-UMC-SUITE` side by side; by default the parent folder of this tool |

`--allow-stacked-push` on `--cli push`, and the **Force** box of the push window (off by default, shown in all eight languages), let a robot or machine model go to the catalogue although its parts would arrive stacked at the origin.

## ⚙️ Configuration

There is no server and no configuration file to edit by hand: the window remembers its choices in one file and each model keeps its colours in a sidecar.

| Variable | Default | What it sets |
|---|---|---|
| `~/.hydra_umc_editor_stl_settings.json` | none | the ecosystem root and the language chosen in the window, remembered across launches |
| `part_colors.json` (in each model folder) | `#9fb4c9` | the colour of each part; a binary STL carries none, and STUDIO and SUITE read the same file |
| `HYDRA_UMC_PASSWORD` | not set | the server password for `--cli push`, so it stays out of the command line |
| `~/.hydra_umc_editor_stl.log` | 256 KiB x 3 | the rotating log of the window and the command line |

## 🚀 Quick start

Requires Python 3.10 or newer. The first line builds a virtual environment with the GUI extra and runs the checks and the tests; Windows has `build.bat` and `run.bat`.

```bash
./build.sh                                    # creates .venv, installs the package with the GUI extra, checks and tests
./run.sh                                      # the windowed editor
./run.sh --cli categories studio              # lists the categories of the STUDIO library (use suite for the SUITE one)
./run.sh --cli parts studio robots-6-dof ar3  # lists the part files of one model
```

## 🧪 Testing

222 automated tests run with `python -m pytest tests -q`. They need no hardware and nothing outside this machine.

The CI runs `HYDRA_UMC_CI=1 python tools/ci_validate.py`, which checks the manifest, the documents, the eight READMEs and the pictures.

## 🏗️ Build & Release

```bash
chmod +x build.sh   # one-time
./build.sh          # creates .venv, pip install -e ".[dev,gui]", compile-checks + tests
./run.sh                                                    # windowed GUI (default)
./run.sh --cli categories studio                            # list categories in a library
./run.sh --cli models studio robots-6-dof                   # list models in a category
./run.sh --cli parts studio robots-6-dof ar3                 # list a model's real part files
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /path/new.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /path/new.stl
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

On Windows: `build.bat`, then `run.bat` (GUI) or `run.bat --cli ...` /
double-click `run-gui.vbs` for a console-free GUI launch.

`library` is always `studio` or `suite`; `category`/`model` are the real
folder names `categories`/`models` just printed. `--root` overrides the
ecosystem root for any `--cli` command (default: this tool's own parent
directory).

## 🩺 Troubleshooting

- `categories`/`models`/`parts` prints nothing: the ecosystem root
  doesn't actually contain `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` as
  siblings - pass `--root` explicitly, or use "Browse" in the GUI.
- `transform`/`replace`/`add` fails with "not a real, parseable STL
  file": the source file genuinely isn't a valid STL (or is a
  0-triangle one) - open it in a real CAD/mesh viewer to confirm.
- A removed/replaced part didn't disappear from the GUI's own part
  list: it did move to `.trash/` on disk - the part list only shows
  real, current top-level files, and a `.trash/` subfolder is
  deliberately excluded from it.

| You see | Because | Do |
|---|---|---|
| "Push succeeded but the server returned no slug", or a login error | The server refused the account (the push needs an administrator), is not a HYDRA-UMC-SERVER, or answered something that is not a JSON object | Use an administrator account on a real HYDRA-UMC-SERVER, with its address and port |
| "the transform would produce vertices that are not finite (too large?) - nothing was changed" | The scale or the translation is so large that the numbers no longer fit in a 32-bit float | Use smaller values |
| "emptying the trash needs an explicit confirmation" | Nothing is deleted for good unless you confirm it | Restore the entry from `.trash/`, or confirm the emptying in the window |

## 📂 Repository Structure

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-EDITOR-STL" width="100%">
</p>

<details>
<summary>Text version of the tree</summary>

```text
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/   source code
│   ├── __init__.py             Package version
│   ├── model_catalog.py        Real, read-only discovery of both model libraries
│   ├── stl_ops.py              Real STL mutation: transform/replace/remove/add, .trash/ backups
│   ├── catalog_push.py         Assembly-URDF + HTTP client for POST /api/models/submit
│   ├── settings.py             Persisted ecosystem root + language preference
│   ├── i18n.py                 Real, complete GUI translations (8 languages)
│   ├── diagnostics.py          Rotating log in the home folder and the guard of the window slots
│   ├── qt_gui.py               Qt Quick bridge over the real model_catalog.py/stl_ops.py core
│   ├── qml/Main.qml            Themed desktop shell, shared with HYDRA-UMC-UPDATER
│   ├── main.py                 Dispatch: GUI by default, --cli for categories/models/parts/transform/replace/remove/add/push
│   ├── assembly.py             The assembled (home-pose) view of a machine from its STL parts
│   ├── mesh_check.py           Mesh checks before a push to the catalog
│   ├── part_colors.py          Per-part colour annotations (a binary STL carries none of its own)
│   └── stl_geometry.py         The real triangles of an STL file as Qt Quick 3D geometry
├── tests/                      Real tests against real, generated STL fixtures
├── docs/                       documents of the project
├── images/                     Media and app icons
├── tools/                      project tools and CI checks
├── .github/                    CI workflow and issue templates
├── build.sh / build.bat        venv + editable install (dev+gui extras) + compile-check + tests
├── run.sh / run.bat            GUI default / CLI entry point
├── run-gui.vbs                 Windows graphical launcher with no console window
├── bump_version.py             explicit version bump
├── bump_manifest_version.py    Syncs hydra-umc.project.json's version to the native one (--sync)
├── CHANGELOG.md                what changed in each version
├── build-test.sh               non-mutating build check
├── hydra-umc.project.json      manifest: version, maturity, family
├── pyproject.toml              package metadata
└── test.sh                     non-mutating build check
```

</details>

## 🗺️ Roadmap & Known limits

**Known limits today**

- A packaged standalone GUI executable (PyInstaller, matching
  HYDRA-UMC-SUITE's own `build_exe.bat`/`.sh` convention).
- Undo/redo over a session's own `.trash/` history, instead of a manual
  file restore.

## 🌍 Languages

This README and the documents of the repository exist in eight languages: English, Spanish, German, French, Italian, Japanese, Chinese and Portuguese (Portugal). They are written together and checked in the CI so that the eight files have the same sections and the same links.

## 🔗 Related Projects

This project is part of the HYDRA-UMC robotics ecosystem by the same author (JuanenRac / Electro Hobby 3D). Worth knowing about, since a request might actually be about one of these rather than this repository.

**Parent Project**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — owns one of the two real model libraries this editor reads and writes (`public/models/`).

**Directly Related**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — owns the second real model library this editor reads and writes (`assets/meshes/`), kept in the exact same category layout as STUDIO's own.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — sibling desktop editor for the same model catalog's own URDF/kinematics side, rather than the raw STL geometry this tool edits.
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — owns the real `POST /api/models/submit` endpoint this editor pushes finished edits to (`catalog_push.py`, "Push to server..." in the GUI or `--cli push`).

**Also Part of the Ecosystem**

*Core Hardware & Platform*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — the robot-arm motherboard design: CM5 host + dual-core STM32H745, meant to orchestrate up to 8 tool arms over CAN-OTA/SPI-OTA (firmware at an early stage; no populated board yet).
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — reproducible Raspberry Pi OS product layer for the CM5: read-only agent, validated config/profiles, WiFi first-contact provisioning.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — the shared JSON-Schema contract and software job-gate boundary every bridge validates its commands against (not a certified safety function).
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — declarative adapter-manifest registry and validator for external-machine connectors; extends the SDK's own contract idea to external machines without replacing the industrial-gateway projects.

*Core Backend & Clients*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — native Android control app with biometric login and a paired Wear OS companion.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS control app (Flutter) with real-time WebSocket sync.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — native touch UI for the onboard 7" DSI touchscreen, embedded on the CM5 itself.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — desktop graphical URDF creator/editor with GitHub/local source loading and live 3D preview editing.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — coordination boundary for AGV/AMR fleets via a VDA 5050 MQTT publisher (tested against an emulated fleet only).
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — high-level CNC-cell coordinator with GRBL status/control-byte access (tested against an emulator only).
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — coordination boundary for legged/humanoid droids, with a Boston Dynamics Spot command sender (tested against an emulator only).
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — laser-cell coordinator reading 3 key/enclosure/interlock GPIO signals (tested against a fake chip only; it cannot arm or fire a laser).
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — safe high-level board-flow coordinator for OpenPnP pick-and-place.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — safe coordination boundary for Moonraker/Klipper 3D printers, with real gated job commands.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinator with a lazily imported rclpy ROS 2 transport (not yet run against a ROS 2 installation).
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — coordination boundary for camera-equipped UAVs, with a MAVLink command sender (tested against an emulator only).

*URTC Tool Platform*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware for the physical Universal Robot Tool Controller PCB, 25+ tool profiles over CAN bus.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — desktop GUI flashing tool for URTC boards, CAN-OTA plus full-chip SWD/JTAG.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — desktop live CAN-bus diagnostic tool for URTC boards, one panel per tool profile.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — browser-based alternative to URTC-TESTER via the Web Serial API, no local install needed.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — gateway in front of the URTC CAN bus: an allowed list of identifiers, a rate limit and a session key; software tested on a computer, not yet on a real bus.

*Vision AI Node (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — integration hub for the Hailo-8 vision pipeline, with a real per-stage hardware-readiness check.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — real compiled-model registry with Hailo-architecture/checksum safe-load verification.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — real GStreamer pipeline + MediaMTX config generator with a real HailoRT integration boundary.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — Position-Based Visual Servoing correction law with authorisation gated on the zone state; no camera pose estimation yet.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — v0 zone-breach, calibration-freshness and E-STOP-request logic that takes object positions from a file; no detector feeds it and no physical E-STOP is wired to it yet.

*Cognitive AI Node (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — integration hub for the Hailo-10 cognitive pipeline (LLM/VLA/voice orchestration).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — real action-token encoding/decoding and trajectory generation for a Vision-Language-Action model.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — real voice front-end (VAD + intent parser) with a bounded, confirmation-gated Watch relay.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — real rule-based task decomposition and semantic error recovery over MCU error codes.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — real stdlib-only TF-IDF document search over this ecosystem's own Markdown docs.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — local, policy-gated AI maintenance technician for the ecosystem itself - observes, diagnoses and proposes fixes; the two highest risk levels are deliberately not implemented yet.

*Orchestration & Swarm*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — integration hub with a real gRPC/Protobuf health-report contract and mission state machine.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — real priority-based job queue with deduplication, over a real HTTP API.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — real gRPC-based fleet health watchdog with retry/backoff and identity-mismatch detection.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — real RRT-based 3D path planner with real obstacle/workspace collision validation.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — real CRDT LWW-Element-Map state sync, property-tested for multi-cell convergence.

*Digital Twin & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — real physics-simulation digital twin, consuming the URDF models HYDRA-UMC-EDITOR-URDF produces.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — consumes the same URDF models to drive its own physics simulation.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — generates training data from those same models.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — hardware-in-the-loop router with a software collision interlock between simulation and real hardware (tested without real hardware).

*Data & Analytics*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — real sqlite3-backed time-series store with a real ingest/query HTTP API.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — real FFT + statistical baseline anomaly detector with drift monitoring.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — real OEE/availability calculation over DATALAKE history, with reproducible CSV export.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — real CAN/WebSocket ingestion pipeline into DATALAKE, with sequence deduplication.

*Industrial Gateway*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — integration hub relaying to industrial protocols, with a real command allowlist/backpressure layer.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — real OPC-UA address space, verified with a real binary-protocol client session.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — real MQTT broker with optional per-client authentication and topic ACLs.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — real MTConnect `/probe` and `/current` XML endpoints with degraded-mode output.

*Complementary Tools & Ecosystem Operations*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — Smart Summaries and Anomaly Highlighting panels over DATALAKE/ANOMALY-DETECTOR, with an honest statistical fallback.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — fleet CLI with a real, stable exit-code contract, a genuine live client of HYDRA-UMC-SERVER's own API.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — WearOS companion app with haptic alert patterns and a paired-phone voice relay (not yet run on a physical watch).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware for a board-mounting rack with real tool-ID decoding and Smart Idle pre-heating logic.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus a real Python vision companion for a thermal/RGB inspection tool head.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — administrative desktop tool that discovers, clones and updates every repo in this ecosystem, and the origin of this project's own Qt Quick visual shell.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux desktop tool that builds a ready-to-flash CM5 image pre-loaded with the ecosystem's most current versions, with Raspberry-Pi-Imager-style first-boot Wi-Fi/user/SSH configuration.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — maintenance-incident coordinator: a low-privilege edge role collects a sanitized inventory/health snapshot, a control-plane role renders it read-only and asks an AI provider to suggest a diagnosis - never applies a patch or deploys anything.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — reproducible development host (Raspberry Pi 5 / CM5) that stores the ecosystem's source and runs bounded build/test tasks under a durable queue; a dedicated dev role, explicitly not an operational CM5.

## 📚 Documentation

Where to read more:

* [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - every real `--cli` subcommand, argument by argument.
* [Security baseline of the ecosystem](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Threat model of the ecosystem](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Changelog of this repository](CHANGELOG.md)
* [License of this repository](LICENSE.md)

## 🤝 Contributing & Community

* Before a pull request run `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (or `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): it must print `CI_VALIDATION=PASS`. Do not run `build.sh` or `build.bat` for this check; building is not a check.
* The eight READMEs are written from one source in HYDRA-UMC-DOCS; do not edit them by hand. Change the source and write them again with `tools/make_readmes.py`.
* Do not state in a README what has not run: say "simulated" or "not tried on hardware" where that is the truth.
* See [CONTRIBUTING.md](CONTRIBUTING.md), the [code of conduct](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) and [SUPPORT.md](SUPPORT.md).

## 👤 AUTHOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENSE

GPL-3.0-or-later - [LICENSE](LICENSE).
