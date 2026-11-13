"""Reaction side of the shell equilibrium check (needs CalculiX).

File: tests/test_shell_equilibrium.py

``shellfe.run`` prints the support reactions (RF) and asserts that, for a static
run with nodal forces, the reactions balance the applied forces. These tests
run one real strip, show the sums agree, and show the assertion fails when the
reactions are wrong. Together with ``tests/test_shell_load_balance.py`` (load
side) this is the shell counterpart of ``generator.check_equilibrium``.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from shellbench import panel as pn
from shellbench import shellfe as fe
from shellbench.shellfe import find_ccx

needs_ccx = pytest.mark.skipif(find_ccx() is None, reason="CalculiX not installed")
THICKNESS_M: float = 0.08
PRESSURE_PA: float = 1000.0


def _loaded_strip():
    """Day 25 vault strip with a full-span plan pressure [model]."""
    v = pn.DAY25_VAULT
    model, _ = pn.strip(THICKNESS_M, rigid_tie=False, vault=v)
    return replace(model, forces=pn.plan_loads(model, PRESSURE_PA, v.span_m, v)), v


@needs_ccx
def test_reactions_balance_the_plan_pressure(tmp_path):
    """run() passes its own check, and the vertical support force equals p x span x strip width.

    CalculiX omits from ``RF`` the load applied on a fixed dof, so that load is added back here.
    """
    model, v = _loaded_strip()
    res = fe.run(model, tmp_path, "equil")
    fixed_z = {n for n, first, last in model.supports if first <= 3 <= last}
    on_fixed = sum(f for n, d, f in model.forces if d == 3 and n in fixed_z)
    support_z = sum(res.reactions[n][2] for n in fixed_z) - on_fixed
    assert support_z == pytest.approx(PRESSURE_PA * v.span_m * pn.TIE_SPACING_M, rel=1e-6)


@needs_ccx
def test_check_fails_when_a_reaction_is_wrong(tmp_path):
    """Changing one reaction after the run breaks the balance and is caught."""
    model, _ = _loaded_strip()
    res = fe.run(model, tmp_path, "equil")
    node = next(iter(res.reactions))
    fx, fy, fz = res.reactions[node]
    bad = replace(res, reactions={**res.reactions, node: (fx, fy, fz + 50.0)})
    with pytest.raises(RuntimeError, match="equilibrium failed"):
        fe.check_equilibrium(model, bad)


def test_check_needs_reactions():
    """An empty reaction set is an error, not a pass."""
    model, _ = _loaded_strip()
    with pytest.raises(RuntimeError, match="no reactions"):
        fe.check_equilibrium(model, fe.ShellResult({}, {}, []))
