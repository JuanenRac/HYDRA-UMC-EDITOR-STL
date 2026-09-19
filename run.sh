#!/usr/bin/env bash
# HYDRA_UMC_SCRIPT_STANDARD_HEADER_BEGIN
# *****************************************************************************
# Project   : HYDRA-UMC-EDITOR-STL
# Script    : run.sh
# Purpose   : Runtime workflow for the project entry point.
# Author    : JuanenRac (Electro Hobby 3D)
# Email     : electrohobby3d@gmail.com
# Copyright : (C) 2026 JuanenRac
# License   : GPL-3.0 - see LICENSE
# *****************************************************************************
# HYDRA_UMC_SCRIPT_STANDARD_HEADER_END
# HYDRA_UMC_SCRIPT_STANDARD_BANNER_BEGIN
printf '\n*******************************************************************************\n'
printf '%s\n' "* HYDRA-UMC-EDITOR-STL - run.sh"
printf '%s\n' "* Mode      : RUN WORKFLOW"
printf '%s\n' "* Author    : JuanenRac (Electro Hobby 3D)"
printf '%s\n' "* Email     : electrohobby3d@gmail.com"
printf '%s\n' "* Copyright : (C) 2026 JuanenRac"
printf '%s\n' "* License   : GPL-3.0 - see LICENSE"
printf '%s\n' "* ------------------------------------------------------------------------- *"
printf '%s\n' "* 1. Resolve the runtime prerequisites declared by this script."
printf '%s\n' "* 2. Start the project entry point and forward user arguments unchanged."
printf '%s\n' "* 3. Preserve its result and keep an interactive terminal open."
printf '%s\n' "*******************************************************************************"
printf '\n'
# HYDRA_UMC_SCRIPT_STANDARD_BANNER_END
# Runs HYDRA-UMC-EDITOR-STL. Run ./build.sh first.
#
# Usage:
#   ./run.sh                                          - launch the windowed GUI (default)
#   ./run.sh --cli categories studio                  - list categories in a library
#   ./run.sh --cli models studio robots-6-dof          - list models in a category
#   ./run.sh --cli parts studio robots-6-dof ar3       - list a model's real part files
#   ./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
#   ./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /path/new.stl
#   ./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
#   ./run.sh --cli add studio robots-6-dof ar3 /path/new.stl
# --cli never imports Qt - safe on a headless machine with no display.
# See main.py's own header comment.
set -uo pipefail  # no -e: we need to reach the trap below even if the process exits non-zero
cd "$(dirname "$0")"

# Keep the window open if this was double-clicked instead of run from an
# already-open terminal - matters most for `--cli status` (real output a
# double-click would otherwise flash-close before it's readable); the
# default GUI mode already blocks on its own mainloop, so this only adds
# one harmless extra prompt there. Only prompts when stdin is actually a
# terminal (never in CI/piped/non-interactive runs).
trap '[ -t 0 ] && read -r -p "Press Enter to close..." _' EXIT

if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
fi

python -m hydra_umc_editor_stl.main "$@"
exit $?
