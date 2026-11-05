"""Independent hand checks of three pilot buildings (D-value method).

File: scripts/hand_check_pilot.py
Run:  python scripts/hand_check_pilot.py results/family_rc_pilot.csv

Hand methods: gravity take-down by tributary length, Rayleigh period with the
D-value (Muto) storey stiffness, base-shear method (cl. 5.2.1) without the top
force, D-value storey drift, cantilever-method seismic axial force. Only cited
constants are imported from shellbench; no generator function is called.
Results and the comparison: docs/pilot_hand_checks.md.
Units: kN, m, s.
"""
import csv
import math
import sys

from shellbench import batch as bt
from shellbench import checks as c
from shellbench import generator as g
from shellbench import seismic as s

from shellbench import anchor_frame as af

SPANS = af.SPANS_M
_XS = [sum(SPANS[:k]) for k in range(len(SPANS) + 1)]
X = tuple(x - sum(SPANS) / 2 for x in _XS)  # column lines about the centroid [m]
GACC = 9.80665  # standard gravity [m/s^2]


def floor_weights(b, row, n):
    """Representative gravity load per level and per column line [kN] (cl. 5.1.3, live x 0.5)."""
    tw, gc = b.tributary_width_m, g.CONCRETE_UNIT_WEIGHT_KN_M3
    col = row["column_mm"] / 1000.0
    bw = [int(v) / 1000 for v in row["beam_b_mm"].split("/")]
    bh = [int(v) / 1000 for v in row["beam_h_mm"].split("/")]
    hs = bt.storey_heights(n)
    levels = []
    for i in range(n):
        roof = i == n - 1
        dead = b.roof_dead_kn_m2 if roof else b.floor_dead_kn_m2
        live = [b.roof_live_kn_m2] * 3 if roof else list(b.live_kn_m2)
        sec = b.roof_secondary_kn_m if roof else b.floor_secondary_kn_m
        wall = (0, 0, 0) if roof else b.floor_beam_wall_kn_m
        w = [dead * tw + 0.5 * live[j] * tw + sec[j] + wall[j] + gc * bw[j] * bh[j] for j in range(3)]
        p = [0.0] * 4
        for j in range(3):
            p[j] += w[j] * SPANS[j] / 2
            p[j + 1] += w[j] * SPANS[j] / 2
        h_col = (hs[i] + (hs[i + 1] if i + 1 < n else 0)) / 2  # half column above and below [J]
        for k in range(4):
            edge = k in (0, 3)
            p[k] += b.longitudinal_beam_kn_m * tw + gc * col * col * h_col
            p[k] += (b.exterior_wall_kn_m if edge else b.interior_wall_kn_m) * tw  # walls at every level [J]
            if roof and edge:
                p[k] += b.parapet_kn_m * tw
        levels.append(p)
    return levels


def check(row, b):
    """Return the hand values and the generator values for one row."""
    n = int(row["storeys"])
    hs = bt.storey_heights(n)
    E = b.concrete_e_mpa * 1e3  # kN/m^2
    col = row["column_mm"] / 1000.0
    bw = [int(v) / 1000 for v in row["beam_b_mm"].split("/")]
    bh = [int(v) / 1000 for v in row["beam_h_mm"].split("/")]
    ib = [E * b.beam_i_factor * bw[j] * bh[j] ** 3 / 12 / SPANS[j] for j in range(3)]
    joint_ib = [ib[0], ib[0] + ib[1], ib[1] + ib[2], ib[2]]
    ic_I = col ** 4 / 12
    D = []
    for i, h in enumerate(hs):
        ic = E * ic_I / h
        tot = 0.0
        for k in range(4):
            if i == 0:
                K = joint_ib[k] / ic
                a = (0.5 + K) / (2 + K)
            else:
                K = 2 * joint_ib[k] / (2 * ic)
                a = K / (2 + K)
            tot += a * 12 * ic / h ** 2
        D.append(tot)
    W = [sum(p) for p in floor_weights(b, row, n)]
    H = [sum(hs[: i + 1]) for i in range(n)]
    # Rayleigh with gravity as lateral load
    V = [sum(W[i:]) for i in range(n)]
    u, acc = [], 0.0
    for i in range(n):
        acc += V[i] / D[i]
        u.append(acc)
    t_bare = 2 * math.pi * math.sqrt(sum(W[i] / GACC * u[i] ** 2 for i in range(n)) / sum(W[i] * u[i] for i in range(n)))
    t1 = b.psi_t * t_bare
    amax, tg = float(row["alpha_max"]), b.tg_s
    a1 = amax if t1 <= tg else (tg / t1) ** s.GAMMA * s.ETA2 * amax
    fek = a1 * 0.85 * sum(W)  # cl. 5.2.1, G_eq = 0.85 G_E
    F = [fek * W[i] * H[i] / sum(W[j] * H[j] for j in range(n)) for i in range(n)]  # no top force [J]
    Vs = [sum(F[i:]) for i in range(n)]
    drift = max(Vs[i] / D[i] / hs[i] for i in range(n))
    # axial: gravity take-down + cantilever method
    lv = floor_weights(b, row, n)
    n_ge = [sum(p[k] for p in lv) for k in range(4)]
    m_ot = sum(F[i] * H[i] for i in range(n))
    sx2 = sum(x * x for x in X)
    n_e = [m_ot * abs(x) / sx2 for x in X]
    mu = max(g.GAMMA_G_SEISMIC * n_ge[k] + g.GAMMA_EH * n_e[k] for k in range(4)) * 1e3 / (c.FC_N_MM2 * row["column_mm"] ** 2)
    return dict(period=(t1, float(row["period_s"])), drift=(drift, float(row["max_drift_ratio"])),
                axial=(mu, float(row["axial_ratio"])), weight_kN=sum(W), fek_kN=fek)


if __name__ == "__main__":
    rows = {r["building_id"]: r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
    for bid in ("s04-p010-tg35-C40", "s03-p030-tg35-C40", "s06-p040-tg35-C40"):
        r = rows[bid]
        r["column_mm"] = int(float(r["column_mm"]))
        out = check(r, bt.ANCHOR)
        print(bid, f"col {r['column_mm']} beams {r['beam_b_mm']}x{r['beam_h_mm']}",
              f"W={out['weight_kN']:.0f} FEk={out['fek_kN']:.0f}")
        for key in ("period", "drift", "axial"):
            hv, gv = out[key]
            print(f"  {key}: hand {hv:.4g} gen {gv:.4g} hand/gen {hv / gv:.3f}")
