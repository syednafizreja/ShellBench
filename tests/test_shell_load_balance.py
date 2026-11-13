"""Load balance of the CalculiX shell-strip decks (no CalculiX needed).

File: tests/test_shell_load_balance.py

The ``shellfe`` deck prints displacements only, so the shell runs cannot check
reactions against the load (panel.py, module docstring). What can be checked
without the solver is the load side of equilibrium: the nodal forces written
to the deck add up to the plan pressure times the loaded plan area, and the
springing weights used for the tie force and the spread add up to one. A lost
or doubled node load would change every thrust and spread, so these are the
shell counterpart of ``generator.check_equilibrium`` [J].
"""

from __future__ import annotations

import pytest

from shellbench import panel as pn

THICKNESS_M: float = 0.08  # any thickness in the library range (50-150 mm)
PRESSURE_PA: float = 1.0  # the unit plan pressure of the flexibility cases
REL_TOL: float = 1e-9  # sums of exact fractions (1/12, 1/3) in floating point
FILL_REL_TOL: float = 1e-2  # mid-point rule against the exact integral f L / 3 [J]


def _vertical_sum(forces) -> float:
    """Sum of the vertical (dof 3) nodal forces [N]."""
    assert all(dof == 3 for _, dof, _ in forces)
    return sum(f for _, _, f in forces)


@pytest.mark.parametrize("vault", [pn.DAY25_VAULT, pn.Vault(span_m=4.0, rise_ratio=1.0 / 12.0)],
                         ids=["day25", "L4.0-r12"])
@pytest.mark.parametrize("fraction", [1.0, 0.5], ids=["full", "half"])
def test_plan_loads_add_up_to_pressure_times_area(vault, fraction):
    """Full and half-span cases: sum of nodal forces = -p x (loaded length x strip width)."""
    model, _ = pn.strip(THICKNESS_M, rigid_tie=False, vault=vault)
    forces = pn.plan_loads(model, PRESSURE_PA, vault.span_m * fraction, vault)
    expected = -PRESSURE_PA * vault.span_m * fraction * pn.TIE_SPACING_M
    assert _vertical_sum(forces) == pytest.approx(expected, rel=REL_TOL)


def test_fill_load_matches_parabolic_fill_volume():
    """Fill case (unit weight 1 N/m^3, depth f - z): total = f L / 3 x strip width."""
    v = pn.DAY25_VAULT
    model, _ = pn.strip(THICKNESS_M, rigid_tie=False, vault=v)
    forces = pn.plan_loads(model, 1.0, v.span_m, v, shape=lambda x: pn.fill_depth(x, v))
    expected = -pn.rise_m(v) * v.span_m / 3.0 * pn.TIE_SPACING_M
    assert _vertical_sum(forces) == pytest.approx(expected, rel=FILL_REL_TOL)


def test_springing_weights_sum_to_one():
    """The tie force and the spread are spread over springing B with weights that sum to 1."""
    _, grid = pn.strip(THICKNESS_M, rigid_tie=False)
    assert sum(pn.edge_weights(grid).values()) == pytest.approx(1.0, rel=REL_TOL)
