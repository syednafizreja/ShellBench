"""Five spot checks of the floor library (Playbook Day 26 Done-when).

File: tests/test_floor_library.py

The Done-when is 60 or more library cases with 5 spot checks. Each check
below recomputes a library value by hand, from closed forms, without the
functions of panel.py (only its input constants). Each check runs on every
sized case it applies to, not on one case only.

1. Thrust under uniform load (raised floor): H = w L^2 / (8 f), reduced for
   axial shortening by 1 / (1 + (15/8) i^2 / f^2), i^2 = t^2 / 12.
2. Membrane stress at the springing (raised floor): N = sqrt(H^2 + (w L / 2)^2), sigma = N / t.
3. Tie strength: A f_y >= H s.
4. Concrete per m^2 of floor: t times the closed-form arc length of a parabola over L.
5. Thrust under true-depth fill: H = int M_0 z ds / int z^2 ds (two-pinned arch),
   with the same shortening factor, against the CalculiX value.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

from shellbench import panel as p

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "results" / "floor_library.csv"


def rows() -> list[dict]:
    """Library rows with numbers as floats."""
    with LIBRARY.open(newline="") as fh:
        out = []
        for r in csv.DictReader(fh):
            for k, v in r.items():
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
            r["sized"] = r["sized"] == "True"
            out.append(r)
    return out


def arc_factor_closed(rise_ratio: float) -> float:
    """Arc length / span of z = 4 f x (L - x) / L^2, closed form."""
    a = 4.0 * rise_ratio
    return 0.5 * math.sqrt(1.0 + a * a) + math.asinh(a) / (2.0 * a)


def shortening_factor(t: float, f: float) -> float:
    """Axial-shortening reduction of a parabolic two-pinned arch thrust.

    H = H_0 / (1 + (15/8) i^2 / f^2) with i^2 = t^2 / 12 (rectangular strip).
    Standard closed form for a shallow parabolic arch of constant section.
    """
    return 1.0 / (1.0 + 15.0 / 8.0 * (t * t / 12.0) / (f * f))


def test_library_size():
    """At least 60 cases, one row each, IDs unique (Done-when)."""
    r = rows()
    assert len(r) >= 60
    assert len({x["variant_id"] for x in r}) == len(r)


def sized(levelling: str | None = None) -> list[dict]:
    """Sized rows, optionally of one levelling option."""
    return [r for r in rows() if r["sized"] and (levelling is None or r["levelling"] == levelling)]


def test_spot_1_uniform_thrust():
    """Raised floor: CalculiX thrust within 2 % of w L^2 / (8 f)."""
    for r in sized("raised_floor"):
        t, L, n = r["thickness_m"], r["span_m"], r["rise_ratio"]
        w = 1.3 * (25.0e3 * t * arc_factor_closed(n) + 1.05e3 + 29.0 * 9.81) + 1.5 * 2.5e3
        assert w == pytest.approx(r["w_uls_pa"], rel=1e-3)
        h = w * L**2 / (8.0 * n * L) * shortening_factor(t, n * L)
        assert r["h_rigid_n_m"] == pytest.approx(h, rel=0.01), r["variant_id"]


def test_spot_2_membrane_stress():
    """Raised floor: sigma = sqrt(H^2 + (w L / 2)^2) / t at the springing, within 1 %."""
    for r in sized("raised_floor"):
        h, w, L, t = r["h_rigid_n_m"], r["w_uls_pa"], r["span_m"], r["thickness_m"]
        assert r["membrane_stress_pa"] == pytest.approx(math.hypot(h, w * L / 2.0) / t, rel=0.01)


def test_spot_3_tie_strength():
    """Every sized tie carries the rigid-tie force, A f_y >= H s (HRB400, s = 1.2 m)."""
    for r in sized():
        area = math.pi * (r["tie_bar_mm"] * 1e-3) ** 2 / 4.0
        assert area * 360.0e6 >= r["h_rigid_n_m"] * 1.2 * (1 - 1e-3), r["variant_id"]


def test_spot_4_concrete_and_mesh():
    """Concrete = t x closed-form arc factor; mesh = 2 x layers x rho x t x arc x 7850."""
    rho = max(0.0015, 45.0 * 1.71e6 / 360.0e6 / 100.0)
    for r in sized():
        k = arc_factor_closed(r["rise_ratio"])
        assert r["concrete_m3_m2"] == pytest.approx(r["thickness_m"] * k, rel=1e-3)
        mesh = 2.0 * r["mesh_layers"] * rho * r["thickness_m"] * k * 7850.0
        assert r["mesh_kg_m2"] == pytest.approx(mesh, rel=1e-3)


def test_spot_5_true_fill_thrust():
    """True-depth fill: CalculiX thrust within 5 % of the two-pinned-arch energy formula."""
    checked = 0
    for r in sized():
        if not p.is_fill(r["levelling"]):
            continue
        t, L, n = r["thickness_m"], r["span_m"], r["rise_ratio"]
        f = n * L
        x = np.linspace(0.0, L, 2001)
        z = 4.0 * f * x * (L - x) / L**2
        ds = np.sqrt(1.0 + (4.0 * f * (L - 2.0 * x) / L**2) ** 2)
        gamma = p.LEVELLING[r["levelling"]][1] * 9.81
        q = 1.3 * (25.0e3 * t * ds + 1.05e3 + gamma * (f - z)) + 1.5 * 2.5e3
        ra = np.trapezoid(q * (L - x), x) / L
        v = ra - np.concatenate(([0.0], np.cumsum((q[1:] + q[:-1]) / 2.0 * np.diff(x))))
        m0 = np.concatenate(([0.0], np.cumsum((v[1:] + v[:-1]) / 2.0 * np.diff(x))))
        h = np.trapezoid(m0 * z * ds, x) / np.trapezoid(z * z * ds, x) * shortening_factor(t, f)
        assert r["h_rigid_n_m"] == pytest.approx(h, rel=0.05), r["variant_id"]
        checked += 1
    assert checked > 0
