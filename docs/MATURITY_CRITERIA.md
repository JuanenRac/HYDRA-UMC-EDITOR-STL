<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Maturity exit criteria
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0 - see LICENSE
============================================================================= -->

# Exit Criteria: Scaffolding to Functional

This project is labelled `scaffolding`. The label moves to `functional` only
when every item below is true and verifiable in the repository (a test, a
CI check or a reproducible command) - not when the code merely exists.

- [ ] Mesh validation before saving or pushing: non-empty, parseable, finite coordinates.
- [ ] Units and dimensional limits are checked (millimeters vs meters, a sane size range) and reported instead of silently accepted.
- [ ] Provenance metadata (source and licence) is recorded for added parts.
- [ ] The version has a single source, verified in the build test.

Verified on real hardware or services is a separate, later step: a passing
software check does not certify physical behaviour.
