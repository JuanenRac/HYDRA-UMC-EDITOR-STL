"""A translation in mm or m is converted to the unit the model declares."""

import json

import numpy as np
import pytest
from stl import mesh as stl_mesh

from hydra_umc_editor_stl.stl_ops import StlOpsError, transform_part


def _model(tmp_path, unit):
    part = stl_mesh.Mesh(np.zeros(1, dtype=stl_mesh.Mesh.dtype))
    part.vectors[0] = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    part.save(str(tmp_path / "part.stl"))
    if unit:
        (tmp_path / "metadata.json").write_text(json.dumps({"unit": unit}), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(
    ("declared", "unit", "expected"),
    [("m", "mm", 0.01), ("m", "m", 10.0), ("mm", "m", 10000.0), ("mm", "mm", 10.0), ("m", "file", 10.0), (None, "file", 10.0)],
)
def test_the_translation_is_converted_to_the_unit_of_the_model(tmp_path, declared, unit, expected):
    box = transform_part(_model(tmp_path, declared), "part.stl", (10.0, 0.0, 0.0), unit=unit)
    assert box.min_xyz[0] == pytest.approx(expected, rel=1e-5)


def test_a_unit_that_cannot_be_converted_changes_nothing(tmp_path):
    model = _model(tmp_path, None)
    before = (model / "part.stl").read_bytes()
    for unit in ("mm", "cm"):
        with pytest.raises(StlOpsError):
            transform_part(model, "part.stl", (1.0, 0.0, 0.0), unit=unit)
    assert (model / "part.stl").read_bytes() == before
    # a rotation needs no unit
    transform_part(model, "part.stl", rotate_deg=(0.0, 0.0, 90.0), unit="mm")
