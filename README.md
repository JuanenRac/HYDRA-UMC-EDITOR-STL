<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center">🇺🇸 <b>English</b> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a></p>

### 📦 Browse and Edit the HYDRA-UMC Ecosystem's Own Real STL Model Libraries

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="numpy-stl core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="PySide6 Qt Quick desktop GUI">
</p>

> **v0.0.4.** The real CLI/GUI core described below is genuinely
> implemented and tested, including a real Qt Quick 3D viewer with
> pick-to-select, per-part color, transform, replace, remove, add and a
> real push of an edited/added model back to HYDRA-UMC-SERVER's own
> `POST /api/models/submit` catalog (the same real integration point
> HYDRA-UMC-EDITOR-URDF uses for URDF models). It does not yet propagate
> a part's own saved color into STUDIO/SUITE's own live 3D viewers - real,
> scoped future work (see ROADMAP), not silently assumed done.

**Honesty check - what actually runs today:** `model_catalog.py` (real,
read-only discovery of both model libraries), `stl_ops.py` (real STL
mutation via `numpy-stl` - transform/replace/remove/add, plus
`model_bounds()` for the 3D viewer's own camera framing),
`part_colors.py` (real per-part color sidecar), `stl_geometry.py`
(real Qt Quick 3D geometry loading) and `catalog_push.py` (real
assembly-URDF generation plus a real HTTP client for
`POST /api/models/submit`) are all tested against real, generated STL
fixtures and a real, session-scoped `QGuiApplication` where needed
(`pytest tests/`, 48 passing cases) and have been smoke-tested end to end
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

## 1. 🛠️ TECHNICAL OVERVIEW

HYDRA-UMC-EDITOR-STL is a small desktop tool - windowed GUI by default,
full CLI with `--cli` - for editing the real STL parts that make up
every robot/machine model HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE ship.
Both of those apps reorganized their own model folders in 2026-09 into
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
  no reliable color of its own, and this ecosystem's own STUDIO/SUITE
  viewers don't interpret that convention either, so this is an honest
  EDITOR-STL-only preview today, not (yet) propagated into their live
  3D viewers.
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

**Nothing is ever permanently deleted.** A remove or a replace moves the
real original file into that model's own `.trash/` subfolder first -
the same "never destroy, move aside instead" discipline this ecosystem's
own internal working conventions already follow, applied here as a real
product feature, not just an internal habit.

## 2. 🧱 ARCHITECTURE & DESIGN DECISIONS

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

## 📂 DIRECTORY STRUCTURE

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # Real, read-only discovery of both model libraries
│   ├── stl_ops.py           # Real STL mutation: transform/replace/remove/add, .trash/ backups
│   ├── catalog_push.py       # Assembly-URDF + HTTP client for POST /api/models/submit
│   ├── settings.py          # Persisted ecosystem root + language preference
│   ├── i18n.py               # Real, complete GUI translations (7 languages)
│   ├── qt_gui.py             # Qt Quick bridge over the real model_catalog.py/stl_ops.py core
│   ├── qml/Main.qml          # Themed desktop shell, shared with HYDRA-UMC-UPDATER
│   └── main.py               # Dispatch: GUI by default, --cli for categories/models/parts/transform/replace/remove/add/push
├── tests/                    # Real tests against real, generated STL fixtures
├── docs/
│   └── CLI_REFERENCE.md      # Command reference
├── images/                   # Media and app icons
├── tools/
│   ├── build_test.py         # Non-versioning build/compile check
│   └── ci_validate.py        # Manifest/CHANGELOG/docs validation used by CI
├── build.sh / build.bat      # venv + editable install (dev+gui extras) + compile-check + tests
├── run.sh / run.bat          # GUI default / CLI entry point
├── run-gui.vbs               # Windows graphical launcher with no console window
├── bump_version.py           # Ecosystem-wide odometer bump (pyproject.toml + __init__.py)
└── bump_manifest_version.py  # Syncs hydra-umc.project.json's version to the native one (--sync)
```

## ⚙️ BUILD & RUN GUIDE

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
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin --password ***
```

On Windows: `build.bat`, then `run.bat` (GUI) or `run.bat --cli ...` /
double-click `run-gui.vbs` for a console-free GUI launch.

`library` is always `studio` or `suite`; `category`/`model` are the real
folder names `categories`/`models` just printed. `--root` overrides the
ecosystem root for any `--cli` command (default: this tool's own parent
directory).

**Troubleshooting**

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

## 🚀 ROADMAP

- Propagating a part's own saved color (`part_colors.json`, see above)
  into HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE's own live 3D viewers - real,
  separate, cross-repo work.
- A packaged standalone GUI executable (PyInstaller, matching
  HYDRA-UMC-SUITE's own `build_exe.bat`/`.sh` convention).
- Undo/redo over a session's own `.trash/` history, instead of a manual
  file restore.

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
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — the physical robot-arm motherboard: CM5 host + dual-core STM32H745, orchestrating up to 8 tool arms over CAN-OTA/SPI-OTA.
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — reproducible Raspberry Pi OS product layer for the CM5: read-only agent, validated config/profiles, WiFi first-contact provisioning.
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — the shared JSON-Schema contract and safety-gate boundary every bridge validates its commands against.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — declarative adapter-manifest registry and validator for external-machine connectors; extends the SDK's own contract idea to external machines without replacing the industrial-gateway projects.

*Core Backend & Clients*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — native Android control app with biometric login and a paired Wear OS companion.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS control app (Flutter) with real-time WebSocket sync.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — native touch UI for the onboard 7" DSI touchscreen, embedded on the CM5 itself.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — desktop graphical URDF creator/editor with GitHub/local source loading and live 3D preview editing.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — coordination boundary for AGV/AMR fleets via a real VDA 5050 MQTT publisher.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — high-level CNC-cell coordinator with real GRBL status/control-byte access.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — coordination boundary for legged/humanoid droids, with a real Boston Dynamics Spot command sender.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — laser-cell safety coordinator reading 3 real key/enclosure/interlock GPIO safeguards.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — safe high-level board-flow coordinator for OpenPnP pick-and-place.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — safe coordination boundary for Moonraker/Klipper 3D printers, with real gated job commands.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — safety coordinator with a real, lazily-imported rclpy ROS 2 transport.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — coordination boundary for camera-equipped UAVs, with a real MAVLink command sender.

*URTC Tool Platform*
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware for the physical Universal Robot Tool Controller PCB, 25+ tool profiles over CAN bus.
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — desktop GUI flashing tool for URTC boards, CAN-OTA plus full-chip SWD/JTAG.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — desktop live CAN-bus diagnostic tool for URTC boards, one panel per tool profile.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — browser-based alternative to URTC-TESTER via the Web Serial API, no local install needed.

*Vision AI Node (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — integration hub for the Hailo-8 vision pipeline, with a real per-stage hardware-readiness check.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — real compiled-model registry with Hailo-architecture/checksum safe-load verification.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — real GStreamer pipeline + MediaMTX config generator with a real HailoRT integration boundary.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — real Position-Based Visual Servoing correction law, safety-gated on upstream zone state.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — real zone-breach checking and E-STOP requesting, with calibration-freshness enforcement.

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
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — real hardware-in-the-loop safety interlock routing commands between simulation and real hardware.

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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — WearOS companion app with real haptic alerts and a paired-phone voice relay.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware for a board-mounting rack with real tool-ID decoding and Smart Idle pre-heating logic.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus a real Python vision companion for a thermal/RGB inspection tool head.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — administrative desktop tool that discovers, clones and updates every repo in this ecosystem, and the origin of this project's own Qt Quick visual shell.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux desktop tool that builds a ready-to-flash CM5 image pre-loaded with the ecosystem's most current versions, with Raspberry-Pi-Imager-style first-boot Wi-Fi/user/SSH configuration.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — maintenance-incident coordinator: a low-privilege edge role collects a sanitized inventory/health snapshot, a control-plane role renders it read-only and asks an AI provider to suggest a diagnosis - never applies a patch or deploys anything.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — reproducible development host (Raspberry Pi 5 / CM5) that stores the ecosystem's source and runs bounded build/test tasks under a durable queue; a dedicated dev role, explicitly not an operational CM5.

---

## 📚 Documentation & Community

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - every real `--cli` subcommand, argument by argument.
- [`CHANGELOG.md`](CHANGELOG.md) - what actually shipped, version by version.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md).

## 👤 AUTHOR

**JuanenRac (Electro Hobby 3D)**
Email: `electrohobby3d@gmail.com`
YouTube: [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENSE

GPL-3.0 - see [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md).
