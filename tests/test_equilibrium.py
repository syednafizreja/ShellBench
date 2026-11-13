"""Global equilibrium of every generator load case (verification, not validation).

File: tests/test_equilibrium.py

``generator.run_case`` asserts that the summed base reactions balance the
applied load. These tests show the assertion holds on the thesis building for
all four cases, and that it fails when the reactions are wrong.
"""

from __future__ import annotations

import pytest

from shellbench import generator as g
from tests.test_generator_anchor import THESIS


def _sizes() -> g.Sizes:
    """Preliminary sizes of the thesis building."""
    return g.preliminary_sizes(THESIS)


@pytest.mark.parametrize("case", ["D", "L", "GE", "E"])
def test_reactions_balance_applied_load(case):
    """run_case completes (its check passes) and the sums agree within the tolerance."""
    z = _sizes()
    lateral = [10.0, 20.0, 30.0, 40.0] if case == "E" else None
    g.run_case(THESIS, z, case, lateral)
    fm = g.build(THESIS, z)
    if case == "E":
        g.ops.timeSeries("Linear", 1)
        g.ops.pattern("Plain", 1, 1)
        for j, f in enumerate(lateral, start=1):
            g.ops.load(fm.node[(j, 0)], f, 0.0, 0.0)
    else:
        g.apply_gravity(fm, THESIS, z, case)
    g.solve()
    g.check_equilibrium(fm, THESIS, z, case, lateral)
    fx, fy = g.applied_load_kn(fm, THESIS, z, case, lateral)
    assert (fx, fy) != (0.0, 0.0)


def test_check_fails_when_a_load_is_missing():
    """Dropping one joint load after the inputs are summed breaks equilibrium and is caught."""
    z = _sizes()
    fm = g.build(THESIS, z)
    g.apply_gravity(fm, THESIS, z, "D")
    g.ops.load(fm.node[(1, 0)], 0.0, -50.0, 0.0)  # extra load the input sum does not know
    g.solve()
    with pytest.raises(RuntimeError, match="equilibrium failed"):
        g.check_equilibrium(fm, THESIS, z, "D")
