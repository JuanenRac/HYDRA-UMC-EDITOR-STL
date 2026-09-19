<!--
=============================================================================
HYDRA-UMC-EDITOR-STL - CLI reference
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0 - see LICENSE
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

## `push <library> <category> <model> --host HOST --username USER --password PASS [options]`

Submits `model`'s own current editable (`.stl`) parts to a running
HYDRA-UMC-SERVER's real model-submission catalog (`POST
/api/models/submit`) - the same real integration point
HYDRA-UMC-EDITOR-URDF already uses for URDF models. Requires an
admin-role account (that endpoint's own `requireAdmin`). Since the
endpoint's own contract is URDF-shaped, this wraps the parts in the
smallest real URDF it accepts: one root link plus one un-jointed
(`fixed`) child link per part - each part's actual position is already
baked into its own STL vertices, never a synthetic pose invented here.

| Option | Meaning | Default |
| --- | --- | --- |
| `--host` | HYDRA-UMC-SERVER host/IP (required) | - |
| `--port` | Server port | `3000` |
| `--username`/`--password` | Admin account credentials (required) | - |
| `--server-category` | Category to file this under server-side | same as `<category>` |
| `--overwrite` | Replace an existing submission with the same name/category | off |

```bash
hydra-umc-editor-stl --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin --password ***
```

## Global options

- `--root PATH` - ecosystem root to scan (default: this tool's own
  parent directory - the standard "every project as a sibling
  directory" layout every other cross-repo tool in this ecosystem
  already assumes).
- `--json` (on `categories`/`models`/`parts`) - machine-readable JSON
  instead of one entry per line.
- `--version` - print this tool's own version and exit.
