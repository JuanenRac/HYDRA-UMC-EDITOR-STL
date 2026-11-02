# =============================================================================
# HYDRA-UMC-EDITOR-STL - A part as a binary glTF (GLB): glb.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
#
# A compact copy of a mesh for viewers that read glTF: the vertices are shared between triangles (an STL repeats every vertex
# once per triangle), the positions are 32-bit floats and the indices 32-bit integers. There is no compression library here (no
# Draco): the saving comes from the shared vertices and, together with the light copy of decimate.py, from fewer triangles.
# =============================================================================
from __future__ import annotations

import json
import struct

import numpy as np

_MAGIC = 0x46546C67  # "glTF"
_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


def _padded(data: bytes, fill: bytes) -> bytes:
    return data + fill * (-len(data) % 4)


def mesh_to_glb(vectors: np.ndarray, name: str = "part") -> bytes:
    """The GLB bytes of triangles given as an (N, 3, 3) array. Triangles with a value that is not finite are left out."""
    triangles = np.asarray(vectors, dtype=np.float64)
    triangles = triangles[np.isfinite(triangles).all(axis=(1, 2))] if len(triangles) else triangles.reshape(0, 3, 3)
    if len(triangles) == 0:
        raise ValueError("there are no triangles to write")
    points = triangles.reshape(-1, 3).astype(np.float32)
    unique, inverse = np.unique(points, axis=0, return_inverse=True)
    indices = inverse.reshape(-1).astype(np.uint32)
    positions = unique.astype("<f4").tobytes()
    index_bytes = indices.astype("<u4").tobytes()
    binary = _padded(positions, b"\x00") + _padded(index_bytes, b"\x00")
    document = {
        "asset": {"version": "2.0", "generator": "hydra-umc-editor-stl"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]}],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
            {"buffer": 0, "byteOffset": len(_padded(positions, b"\x00")), "byteLength": len(index_bytes), "target": 34963},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": int(len(unique)),
                "type": "VEC3",
                "min": [float(v) for v in unique.min(axis=0)],
                "max": [float(v) for v in unique.max(axis=0)],
            },
            {"bufferView": 1, "componentType": 5125, "count": int(len(indices)), "type": "SCALAR"},
        ],
    }
    json_bytes = _padded(json.dumps(document, separators=(",", ":")).encode("utf-8"), b" ")
    total = 12 + 8 + len(json_bytes) + 8 + len(binary)
    return (
        struct.pack("<III", _MAGIC, 2, total)
        + struct.pack("<II", len(json_bytes), _JSON_CHUNK)
        + json_bytes
        + struct.pack("<II", len(binary), _BIN_CHUNK)
        + binary
    )


def read_glb(data: bytes) -> tuple[dict, bytes]:
    """The JSON document and the binary chunk of a GLB (used by the tests and by anything that wants to check a file)."""
    if len(data) < 20:
        raise ValueError("not a GLB: too short")
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != _MAGIC or version != 2 or length != len(data):
        raise ValueError("not a version 2 GLB")
    json_length, json_type = struct.unpack_from("<II", data, 12)
    if json_type != _JSON_CHUNK:
        raise ValueError("the first chunk is not JSON")
    document = json.loads(data[20 : 20 + json_length].decode("utf-8"))
    offset = 20 + json_length
    binary = b""
    if offset + 8 <= len(data):
        bin_length, bin_type = struct.unpack_from("<II", data, offset)
        if bin_type == _BIN_CHUNK:
            binary = data[offset + 8 : offset + 8 + bin_length]
    return document, binary
