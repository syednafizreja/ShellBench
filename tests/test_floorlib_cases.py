"""The floor-library case list: size, unique IDs, and the ID format the dataset files use."""

import re
from pathlib import Path

import pandas as pd

from shellbench import floorlib


def test_case_count_and_unique_ids():
    cs = floorlib.cases()
    assert len(cs) == 72
    assert len({c["variant_id"] for c in cs}) == 72


def test_variant_id_format():
    assert floorlib.variant_id(6.6, 15, "foamed_fill", 1) == "L66-r15-ff-m1"
    assert floorlib.variant_id(6.0, 8, "raised_floor", 2) == "L60-r08-rs-m2"
    pat = re.compile(r"^L(60|66)-r\d{2}-(ff|rf|rs)-m[12]$")
    assert all(pat.match(c["variant_id"]) for c in floorlib.cases())


def test_every_case_is_the_id_it_names():
    for c in floorlib.cases():
        assert c["variant_id"] == floorlib.variant_id(c["span_m"], c["rise_den"], c["levelling"], c["mesh_layers"])


def test_cases_match_the_committed_library():
    lib = pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "floor_library.csv")
    col = "variant_id" if "variant_id" in lib.columns else lib.columns[0]
    assert set(lib[col]) == {c["variant_id"] for c in floorlib.cases()}
