<!--
=============================================================================
HYDRA-UMC-EDITOR-STL - CLI reference
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
=============================================================================
-->

# CLI Reference

Every `--cli` subcommand below calls the exact same real
`model_catalog.py`/`stl_ops.py` functions the Qt Quick GUI uses - no
separate GUI-only logic exists. None of these import Qt, so all of them
work on a headless machine with no display.

`library` is always `studio` (HYDRA-UMC-STUDIO's own `public/models/`)
or `suite` (HYDRA-UMC-SUITE's own `assets/meshes/`). `category`/`model`
must be real folder names - use `categories`/`models` to discover them.

## `categories <library>`

Lists every real category folder present for that library.

```bash
hydra-umc-editor-stl --cli categories studio
hydra-umc-editor-stl --cli categories studio --json
```

## `models <library> <category>`

Lists every real model folder under that category.

```bash
hydra-umc-editor-stl --cli models studio robots-6-dof
```

## `parts <library> <category> <model>`

Lists every real part file in that model, its size, and whether it's
editable (a real `.stl`; a `.glb` part like LumenPnP's own merged mesh
is listed but marked read-only).

```bash
hydra-umc-editor-stl --cli parts studio machine-pnp lumenpnp
```

## `transform <library> <category> <model> <part> [options]`

Translates/rotates/scales `part`'s own real vertex data and saves it
back in place. The original is backed up into that model's own
`.trash/` subfolder first.

| Option | Meaning | Default |
| --- | --- | --- |
| `--tx`/`--ty`/`--tz` | Translation, millimeters | `0` |
| `--rx`/`--ry`/`--rz` | Rotation, degrees (applied X, then Y, then Z, after scale) | `0` |
| `--scale` | Uniform scale factor, must be positive | `1` |

```bash
hydra-umc-editor-stl --cli transform studio robots-6-dof ar3 base_link.STL --tz 10 --rz 90
```

## `replace <library> <category> <model> <part> <source>`

Overwrites `part` with `source`'s own real bytes, after validating
`source` actually parses as a non-empty STL. The original `part` is
backed up into `.trash/` first.

```bash
hydra-umc-editor-stl --cli replace studio robots-6-dof ar3 base_link.STL /path/to/new_base.stl
```

## `remove <library> <category> <model> <part>`

Moves `part` into that model's own `.trash/` subfolder - never deletes
it.

```bash
hydra-umc-editor-stl --cli remove studio robots-6-dof ar3 base_link.STL
```

## `add <library> <category> <model> <source> [--dest-filename NAME]`

Copies a real, externally-parseable STL into that model's own folder.
Refuses to overwrite an existing part with the same name - use
`replace` for that instead.

```bash
hydra-umc-editor-stl --cli add studio robots-6-dof ar3 /path/to/extra_bracket.stl
```

## `push <library> <category> <model> --host HOST --username USER [--password PASS] [options]`

Submits `model`'s own current editable (`.stl`) parts to a running
HYDRA-UMC-SERVER's real model-submission catalog (`POST
/api/models/submit`) - the same real integration point
HYDRA-UMC-EDITOR-URDF already uses for URDF models. Requires an
admin-role account (that endpoint's own `requireAdmin`). Since the
endpoint's own contract is URDF-shaped, this wraps the parts in the
smallest real URDF it accepts: one root link plus one un-jointed
(`fixed`) child link per part - each part's actual position is already
baked into its own STL vertices, never a synthetic pose invented here. That holds for independent pieces (heated beds, racks, vacuum tables) only: the parts of a robot or machine are stored in their own link frame, so each joint origin is the part's home-pose position from the kinematics of the `HYDRA-UMC-SUITE` checkout next to this one (the placement of the assembled view; the joints stay `fixed`). If that placement is not known for the model the parts would arrive stacked at the origin: a warning is printed and the push is refused unless it is forced. Only `.stl` parts are uploaded, the rest is reported, and an upload above the server's 50 MB limit is refused before it is sent.

| Option | Meaning | Default |
| --- | --- | --- |
| `--host` | HYDRA-UMC-SERVER host/IP, or a full `https://host` URL to avoid sending the password in clear text (required) | - |
| `--port` | Server port | `3000` |
| `--username` | Admin account username (required) | - |
| `--password` | Not recommended: it is visible in the process list and the shell history. Leave it out to be prompted, or set `HYDRA_UMC_PASSWORD` | prompt |
| `--server-category` | Category to file this under server-side | same as `<category>` |
| `--overwrite` | Replace an existing submission with the same name/category | off |
| `--allow-stacked-push` | Send a robot or machine although the home-pose placement of its parts is not known here and they arrive stacked at the origin (refused by default only in that case; independent pieces such as heated beds are never refused; the **Force** box of the push window does the same) | off |

```bash
hydra-umc-editor-stl --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

## Global options

- `--root PATH` - ecosystem root to scan (default: this tool's own
  parent directory - the standard "every project as a sibling
  directory" layout every other cross-repo tool in this ecosystem
  already assumes).
- `--json` (on `categories`/`models`/`parts`) - machine-readable JSON
  instead of one entry per line.
- `--version` - print this tool's own version and exit.

## `open-in-urdf-editor <library> <category> <model> [--launch]`

Writes the model as a URDF in a work folder (`urdf_handoff_dir` of the saved settings, else `~/.hydra_umc_editor_stl/urdf_handoff`): the editable parts as fixed links at their home-pose placement, the meshes copied into `meshes/`. The model folder is not touched and an earlier hand-over of the same model is replaced. With `--launch` the URDF editor is started on the file (`main.py --open FILE`); it is looked for as the git checkout `HYDRA-UMC-EDITOR-URDF` next to the others or at `urdf_editor_path` in the saved settings. The window offers the same as a button only when `open_in_urdf_editor` is `true` in the saved settings.

## `push ... [--lite stl|glb] [--lite-ratio R]`

Besides the full meshes, sends a lighter copy of every part (`<mesh>.lite.stl` or `<mesh>.lite.glb`, `R` of the triangles kept; default `lite_ratio` of the saved settings, else 0.2). Without `--lite`, `push_lite` of the saved settings decides; with neither, nothing extra is sent.

## `sync-libraries ... [--check]`

`--check` makes the exit code 1 when the target library is not in line with the master (nothing is written without `--apply`).

## Saved settings that switch things on

All in `~/.hydra_umc_editor_stl_settings.json`, all off or empty by default: `push_lite` (`"stl"`, `"glb"`), `lite_ratio`, `open_in_urdf_editor` (`true`), `urdf_editor_path`, `urdf_handoff_dir`, `diff_overlay` (`true`: a Compare button in the trash window).
