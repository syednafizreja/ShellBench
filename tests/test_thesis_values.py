"""Format checks for the thesis validation targets in validation/thesis_values/.

The CSV files hold values typed from the author's thesis (Day 3). These tests do
not judge whether the thesis values are right; they check that every file is
well formed, so later validation code can read it without guessing units.

Rules checked:
1. The six expected files exist.
2. Every header cell has the form ``name [unit]``. Labels use ``[text]`` and
   dimensionless numbers use ``[-]``.
3. Every row has as many cells as the header and no cell is empty.
4. Every column whose unit is not ``[text]`` holds numbers only.
"""

import csv
import re
from pathlib import Path

import pytest

THESIS_DIR = Path(__file__).resolve().parents[1] / "validation" / "thesis_values"

EXPECTED_FILES = [
    "gravity_beam_end_moments.csv",
    "gravity_column_axial_forces.csv",
    "lateral_stiffness_d_values.csv",
    "wind_drift.csv",
    "seismic_storey_shear_drift.csv",
    "beam_steel_areas.csv",
]

HEADER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]* \[[^\[\]]+\]$")


def read_csv(path):
    """Read a CSV file and return (header, rows) as lists of strings."""
    with path.open(newline="", encoding="utf-8") as handle:
        table = list(csv.reader(handle))
    return table[0], table[1:]


def test_all_expected_files_exist():
    """All six Day 3 files are present in validation/thesis_values/."""
    missing = [name for name in EXPECTED_FILES if not (THESIS_DIR / name).is_file()]
    assert not missing, f"missing files: {missing}"


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_header_has_units(name):
    """Every header cell names its unit in square brackets."""
    header, _ = read_csv(THESIS_DIR / name)
    bad = [cell for cell in header if not HEADER_PATTERN.match(cell)]
    assert not bad, f"{name}: header cells without 'name [unit]': {bad}"


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_no_empty_cells(name):
    """Every row is complete: right length and no blank cells."""
    header, rows = read_csv(THESIS_DIR / name)
    assert rows, f"{name}: no data rows"
    for number, row in enumerate(rows, start=2):
        assert len(row) == len(header), f"{name} line {number}: {len(row)} cells, header has {len(header)}"
        blanks = [header[i] for i, cell in enumerate(row) if cell.strip() == ""]
        assert not blanks, f"{name} line {number}: empty cells in {blanks}"


@pytest.mark.parametrize("name", EXPECTED_FILES)
def test_numeric_columns_are_numbers(name):
    """Columns with a physical or [-] unit contain values that parse as floats."""
    header, rows = read_csv(THESIS_DIR / name)
    numeric = [i for i, cell in enumerate(header) if not cell.endswith("[text]")]
    for number, row in enumerate(rows, start=2):
        for i in numeric:
            try:
                float(row[i])
            except ValueError:
                pytest.fail(f"{name} line {number}: '{row[i]}' in {header[i]} is not a number")
