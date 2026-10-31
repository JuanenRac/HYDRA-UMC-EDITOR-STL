# =============================================================================
# HYDRA-UMC-EDITOR-STL - Entry point: main.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# Bare invocation (no arguments, or double-clicked) launches the Qt Quick
# desktop GUI (qt_gui.py) - the same real visual shell HYDRA-UMC-UPDATER's
# own qt_gui.py/Main.qml already established for this ecosystem's PC
# tools (dark canvas, cyan/blue/amber/red accents, angular Bahnschrift
# type). `--cli` switches to the headless argparse CLI below, real
# subcommands over model_catalog.py/stl_ops.py - no GUI/Qt import at all
# on that path, so a headless CM5 can still browse/edit the model
# libraries without a display.
# =============================================================================
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from . import __version__, settings
from .catalog_push import CatalogPushError, ServerClient, push_warnings
from .decimate import DEFAULT_RATIO, make_light_copy
from .library_sync import LibrarySyncError, sync_libraries
from .mesh_diff import diff_with_trash, render_diff_with_trash
from .model_catalog import list_categories, list_models, load_model
from .stl_ops import StlOpsError, add_part, remove_part, replace_part, transform_part


def default_ecosystem_root() -> Path:
    """This project's own parent directory - correct as long as
    HYDRA-UMC-EDITOR-STL itself was checked out the same way every other
    ecosystem project is (a sibling of HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE
    under one common parent). Always overridable with --root."""
    return Path(__file__).resolve().parents[3]


def resolve_ecosystem_root() -> Path:
    """Prefers a previously chosen, still-real directory over the
    parent-directory heuristic - used only by the GUI launch path below;
    `--cli` subcommands take an explicit --root instead so a script's
    own behavior never depends on a GUI preference saved on this same
    machine."""
    return settings.get_saved_ecosystem_root() or default_ecosystem_root()


def cmd_categories(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    categories = list_categories(root, args.library)
    if args.json:
        print(json.dumps(categories))
    else:
        for name in categories:
            print(name)
    return 0


def cmd_models(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    models = list_models(root, args.library, args.category)
    if args.json:
        print(json.dumps(models))
    else:
        for name in models:
            print(name)
    return 0


def cmd_parts(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    model = load_model(root, args.library, args.category, args.model)
    if model is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([{"filename": p.filename, "sizeBytes": p.size_bytes, "editable": p.editable} for p in model.parts]))
    else:
        for part in model.parts:
            marker = "" if part.editable else "  (read-only)"
            print(f"{part.filename}\t{part.size_bytes} bytes{marker}")
    return 0


def _resolve_model_dir(args: argparse.Namespace) -> Path | None:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    model = load_model(root, args.library, args.category, args.model)
    return model.path if model is not None else None


def cmd_transform(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    try:
        bbox = transform_part(
            model_dir, args.part,
            translate_mm=(args.tx, args.ty, args.tz),
            rotate_deg=(args.rx, args.ry, args.rz),
            scale=args.scale,
        )
    except StlOpsError as error:
        print(f"Transform failed: {error}", file=sys.stderr)
        return 1
    print(f"Transformed {args.part} - new bounds: min {bbox.min_xyz}, max {bbox.max_xyz}")
    return 0


def cmd_replace(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    try:
        replace_part(model_dir, args.part, Path(args.source).resolve())
    except StlOpsError as error:
        print(f"Replace failed: {error}", file=sys.stderr)
        return 1
    print(f"Replaced {args.part} (original kept in .trash/)")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    try:
        destination = remove_part(model_dir, args.part)
    except StlOpsError as error:
        print(f"Remove failed: {error}", file=sys.stderr)
        return 1
    print(f"Moved {args.part} to {destination}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    try:
        filename = add_part(model_dir, Path(args.source).resolve(), args.dest_filename)
    except StlOpsError as error:
        print(f"Add failed: {error}", file=sys.stderr)
        return 1
    print(f"Added as {filename}")
    return 0


def cmd_lite(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    ratio = args.ratio if args.ratio is not None else _saved_ratio()
    names = [args.part] if args.part else [p.filename for p in load_model(  # type: ignore[union-attr]
        Path(args.root).resolve() if args.root else default_ecosystem_root(), args.library, args.category, args.model).parts if p.editable]
    for name in names:
        try:
            done = make_light_copy(model_dir, name, ratio)
        except StlOpsError as error:
            print(f"Light copy failed for {name}: {error}", file=sys.stderr)
            return 1
        print(f"{name}: {done['triangles_before']} -> {done['triangles_after']} triangles, {done['bytes_before']} -> {done['bytes_after']} bytes ({done['path']})")
    return 0


def _saved_ratio() -> float:
    """The share of the triangles a light copy keeps when --ratio is not given: `lite_ratio` in the saved settings."""
    value = settings.load_settings().get("lite_ratio", DEFAULT_RATIO)
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 < value <= 1 else DEFAULT_RATIO


def cmd_diff(args: argparse.Namespace) -> int:
    model_dir = _resolve_model_dir(args)
    if model_dir is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    try:
        result = diff_with_trash(model_dir, args.part, args.entry)
        if args.svg:
            Path(args.svg).write_text(render_diff_with_trash(model_dir, args.part, args.entry), encoding="utf-8")
    except (StlOpsError, OSError) as error:
        print(f"Diff failed: {error}", file=sys.stderr)
        return 1
    print(f"triangles: {result.triangles_before} -> {result.triangles_after}")
    print("size (x, y, z): " + " -> ".join(", ".join(f"{v:.3f}" for v in size) for size in (result.size_before, result.size_after)))
    print("center shift: " + ", ".join(f"{v:.3f}" for v in result.center_shift))
    print(f"volume: {result.volume_before:.3f} -> {result.volume_after:.3f}")
    if args.svg:
        print(f"picture written to {args.svg}")
    return 0


def cmd_sync_libraries(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    try:
        outcome = sync_libraries(root, args.master, args.target, apply=args.apply)
    except LibrarySyncError as error:
        print(f"Library sync failed: {error}", file=sys.stderr)
        return 1
    diff = outcome["diff"]
    print(f"same: {diff.same}  to copy: {len(diff.only_in_master)}  to replace: {len(diff.different)}  only in {args.target} (left alone): {len(diff.only_in_target)}")
    if not args.apply and not diff.in_sync:
        print("Nothing was written: add --apply to bring the target in line (replaced files are kept in .sync-backup/).")
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else default_ecosystem_root()
    model = load_model(root, args.library, args.category, args.model)
    if model is None:
        print(f"No such model: {args.library}/{args.category}/{args.model}", file=sys.stderr)
        return 1
    password = args.password or os.environ.get("HYDRA_UMC_PASSWORD") or getpass.getpass("Server password: ")
    for warning in push_warnings(model, args.server_category or args.category, root):
        print(f"Warning: {warning}", file=sys.stderr)
    client = ServerClient(args.host, args.port)
    try:
        client.login(args.username, password)
        slug = client.push_model(
            model, args.server_category or args.category, args.overwrite, allow_stacked=args.allow_stacked_push,
            ecosystem_root=root,
        )
    except CatalogPushError as error:
        print(f"Push failed: {error}", file=sys.stderr)
        return 1
    print(f"Pushed as {slug}")
    return 0


def _add_model_selector_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", help="Ecosystem root to scan (default: this tool's own parent directory).")
    parser.add_argument("library", choices=["studio", "suite"], help="Which model library to use.")
    parser.add_argument("category", help="Category folder (e.g. robots-6-dof, machine-pnp, heatedbeds).")
    parser.add_argument("model", help="Model folder name inside that category.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hydra-umc-editor-stl --cli",
        description="Browses and edits HYDRA-UMC-STUDIO's/HYDRA-UMC-SUITE's own real STL model libraries.",
    )
    parser.add_argument("--version", action="version", version=f"hydra-umc-editor-stl {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    categories_p = subparsers.add_parser("categories", help="List every real category in a library.")
    categories_p.add_argument("--root", help="Ecosystem root to scan (default: this tool's own parent directory).")
    categories_p.add_argument("library", choices=["studio", "suite"])
    categories_p.add_argument("--json", action="store_true")
    categories_p.set_defaults(func=cmd_categories)

    models_p = subparsers.add_parser("models", help="List every real model in a category.")
    models_p.add_argument("--root", help="Ecosystem root to scan (default: this tool's own parent directory).")
    models_p.add_argument("library", choices=["studio", "suite"])
    models_p.add_argument("category")
    models_p.add_argument("--json", action="store_true")
    models_p.set_defaults(func=cmd_models)

    parts_p = subparsers.add_parser("parts", help="List every real part file in a model.")
    _add_model_selector_args(parts_p)
    parts_p.add_argument("--json", action="store_true")
    parts_p.set_defaults(func=cmd_parts)

    transform_p = subparsers.add_parser("transform", help="Translate/rotate/scale one part in place.")
    _add_model_selector_args(transform_p)
    transform_p.add_argument("part", help="Part filename (as shown by `parts`).")
    transform_p.add_argument("--tx", type=float, default=0.0)
    transform_p.add_argument("--ty", type=float, default=0.0)
    transform_p.add_argument("--tz", type=float, default=0.0)
    transform_p.add_argument("--rx", type=float, default=0.0)
    transform_p.add_argument("--ry", type=float, default=0.0)
    transform_p.add_argument("--rz", type=float, default=0.0)
    transform_p.add_argument("--scale", type=float, default=1.0)
    transform_p.set_defaults(func=cmd_transform)

    replace_p = subparsers.add_parser("replace", help="Replace one part's STL file with another (original kept in .trash/).")
    _add_model_selector_args(replace_p)
    replace_p.add_argument("part", help="Part filename to replace.")
    replace_p.add_argument("source", help="Path to the replacement STL file.")
    replace_p.set_defaults(func=cmd_replace)

    remove_p = subparsers.add_parser("remove", help="Move one part into the model's own .trash/ subfolder.")
    _add_model_selector_args(remove_p)
    remove_p.add_argument("part", help="Part filename to remove.")
    remove_p.set_defaults(func=cmd_remove)

    add_p = subparsers.add_parser("add", help="Add a new STL part to a model.")
    _add_model_selector_args(add_p)
    add_p.add_argument("source", help="Path to the STL file to add.")
    add_p.add_argument("--dest-filename", help="Save under this filename instead of the source's own name.")
    add_p.set_defaults(func=cmd_add)

    lite_p = subparsers.add_parser("lite", help="Write a lighter copy of the parts to .lite/ in the model folder (the originals are not touched).")
    _add_model_selector_args(lite_p)
    lite_p.add_argument("--part", help="Only this part (default: every editable part).")
    lite_p.add_argument("--ratio", type=float, help=f"Share of the triangles to keep, above 0 and up to 1 (default: lite_ratio in the saved settings, else {DEFAULT_RATIO}).")
    lite_p.set_defaults(func=cmd_lite)

    diff_p = subparsers.add_parser("diff", help="Compare a part with the version that .trash/ kept before its last change.")
    _add_model_selector_args(diff_p)
    diff_p.add_argument("part", help="Part filename.")
    diff_p.add_argument("--entry", help="The .trash/ entry to compare with (default: the newest one for this part).")
    diff_p.add_argument("--svg", help="Also write a picture with both versions laid over each other to this file.")
    diff_p.set_defaults(func=cmd_diff)

    sync_p = subparsers.add_parser("sync-libraries", help="Bring one model library in line with the other (a plan unless --apply is given; nothing is deleted).")
    sync_p.add_argument("--root", help="Ecosystem root to scan (default: this tool's own parent directory).")
    sync_p.add_argument("--master", choices=["studio", "suite"], default="studio", help="The library that is right (default: studio).")
    sync_p.add_argument("--target", choices=["studio", "suite"], default="suite", help="The library that is brought in line (default: suite).")
    sync_p.add_argument("--apply", action="store_true", help="Write the changes; without it only the plan is shown.")
    sync_p.set_defaults(func=cmd_sync_libraries)

    push_p = subparsers.add_parser("push", help="Push a model's editable parts to a running server's model-submission catalog.")
    _add_model_selector_args(push_p)
    push_p.add_argument("--host", required=True, help="HYDRA-UMC-SERVER host/IP, or a full https://host URL to avoid sending the password in clear text.")
    push_p.add_argument("--port", type=int, default=3000)
    push_p.add_argument("--username", required=True, help="Admin account username (POST /api/models/submit requires admin).")
    push_p.add_argument("--password", help="Not recommended (visible in the process list and shell history): leave it out to be prompted, or set HYDRA_UMC_PASSWORD.")
    push_p.add_argument("--server-category", help="Category to file this under on the server (default: the same folder name used locally).")
    push_p.add_argument(
        "--allow-stacked-push",
        action="store_true",
        help="Send a robot or machine even when the home-pose placement of its parts is not known here (they would arrive stacked at the origin).",
    )
    push_p.add_argument("--overwrite", action="store_true", help="Replace an existing submission with the same name/category.")
    push_p.set_defaults(func=cmd_push)

    return parser


def main() -> int:
    if "--cli" not in sys.argv:
        try:
            from .qt_gui import launch_qt_gui
        except ImportError:
            print(
                "The Qt Quick GUI runtime is not installed. Run build.bat/build.sh "
                "to install it, or use `--cli` on a headless system.",
                file=sys.stderr,
            )
            return 1
        return launch_qt_gui(resolve_ecosystem_root())

    argv = [a for a in sys.argv[1:] if a != "--cli"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
