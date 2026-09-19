# Security Policy 🔒 (HYDRA-UMC-EDITOR-STL)

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.x.x   | ✅ Yes    |

## Reporting a Vulnerability

**CRITICAL: Do not report vulnerabilities through public GitHub issues.**

This tool reads and writes real files under the ecosystem's own model
libraries (`HYDRA-UMC-STUDIO/public/models/`, `HYDRA-UMC-SUITE/assets/
meshes/`) - a real, meaningful attack surface for a tool whose whole job
is mutating files on disk. If you discover a vulnerability affecting:

- **Where a write lands** - a path-traversal or similar issue in how a
  part filename, category or model id maps to a real filesystem path
  under the ecosystem root (`model_catalog.py`/`stl_ops.py`).
- **What gets overwritten without a backup** - a way to make
  `replace_part()`/`remove_part()` skip the `.trash/` backup step and
  actually destroy the original file.
- **What gets accepted as a real STL** - a way to make `is_real_stl()`
  accept a file that is not a genuine STL, letting a malformed/malicious
  file get copied into a model's own real folder.

please report it responsibly:

1. **Email**: Send a detailed report to `electrohobby3d@gmail.com`.
2. **Impact**: Describe the attack surface affected and a realistic
   scenario (this tool has no network-facing service of its own - it's a
   desktop app a person runs by hand against their own local checkout,
   so most realistic scenarios involve a malicious STL/replacement file
   handed to someone, not a remote attacker directly reaching this tool).
3. **Response**: Initial acknowledgment within 48 hours.

We follow a coordinated disclosure policy.
