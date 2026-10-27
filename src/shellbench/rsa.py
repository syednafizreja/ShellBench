"""Modal response-spectrum check of the anchor frame against the Day 9 base-shear method.

File: src/shellbench/rsa.py

What this module does
---------------------
It is the second, independent route to the seismic answer (Playbook Day 10).
With the same storey weights, masses and GB 50011 design spectrum as the
primary base-shear run of ``shellbench.seismic`` (reading rule 1,
docs/anchor_notes.md, "How the response-spectrum check is read"), it:

1. computes the first three modes of the 2D frame on axis (2), their
   participation factors and effective mass ratios;
2. forms the modal storey forces F_ji = alpha_j gamma_j X_ji G_i
   (GB 50011-2010 cl. 5.2.2 [?]: formula to be checked in the author's copy);
3. applies each mode's forces statically and combines storey shears and
   inter-storey drifts by SRSS (cl. 5.2.2 [?]);
4. compares base shear, storey shears and drifts with the base-shear method
   and with thesis Table 8-12 (as read on Day 9), and draws
   ``figures/anchor_seismic_compare.png``.

The 3D whole-building periods are in ``shellbench.anchor_3d``.

Units: kN, m, s inside OpenSees; drifts reported in mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import openseespy.opensees as ops

from shellbench import anchor_frame as af
from shellbench import seismic as s

#: Number of modes combined. Playbook Day 10 prompt ("first 3 modes").
N_MODES: int = 3


@dataclass
class Mode:
    """One vibration mode of the 2D frame with lumped level masses.

    Attributes:
        number: Mode number, 1 = longest period.
        period_s: Period [s].
        shape: Mean horizontal eigenvector component at levels 1..n [-].
        gamma: Participation factor sum(X G) / sum(X^2 G) [-].
        mass_ratio: Effective modal mass / total mass [-].
    """

    number: int
    period_s: float
    shape: list[float]
    gamma: float
    mass_ratio: float


def modes(weights_kn: list[float], n_modes: int = N_MODES) -> list[Mode]:
    """Return the first modes of the bare frame with G_i / g lumped at the levels.

    The level shape is the mean horizontal eigenvector component of the four
    column-line nodes (as storey displacements are read elsewhere).

    Args:
        weights_kn: G_i, level 1 first [kN].
        n_modes: Number of modes.

    Returns:
        Modes, longest period first. Each shape is scaled to 1.0 at the roof,
        so gamma is the factor for that scaling (gamma X does not depend on it).
    """
    fm = af.build_frame()
    s.assign_level_masses(fm, weights_kn)
    eig = ops.eigen(n_modes)
    out = []
    total = sum(weights_kn)
    for j, lam in enumerate(eig, start=1):
        shape = [sum(ops.nodeEigenvector(fm.node[(ax, lvl)], j, 1) for ax in af.AXES) / len(af.AXES)
                 for lvl in range(1, len(weights_kn) + 1)]
        shape = [x / shape[-1] for x in shape]
        sxg = sum(x * g for x, g in zip(shape, weights_kn))
        sx2g = sum(x * x * g for x, g in zip(shape, weights_kn))
        out.append(Mode(j, 2.0 * math.pi / math.sqrt(lam), shape, sxg / sx2g,
                        sxg * sxg / (sx2g * total)))
    ops.wipe()
    return out


def modal_forces(mode: Mode, weights_kn: list[float], alpha_max: float, tg_s: float) -> list[float]:
    """Return F_ji = alpha_j gamma_j X_ji G_i for one mode [kN] (cl. 5.2.2 [?]).

    Args:
        mode: The mode.
        weights_kn: G_i, level 1 first [kN].
        alpha_max: Maximum influence coefficient [-].
        tg_s: Characteristic period [s].

    Returns:
        Storey forces of the mode, level 1 first [kN].
    """
    a = s.alpha_spectrum(mode.period_s, alpha_max, tg_s)
    return [a * mode.gamma * x * g for x, g in zip(mode.shape, weights_kn)]


def srss(values: list[list[float]]) -> list[float]:
    """Combine modal values level by level by the square root of the sum of squares.

    Args:
        values: One list per mode, each with one value per level.

    Returns:
        Combined values, one per level.
    """
    return [math.sqrt(sum(v[i] ** 2 for v in values)) for i in range(len(values[0]))]


@dataclass
class RsaResult:
    """Output of the response-spectrum run.

    Attributes:
        modes: The modes used.
        forces_kn: Modal storey forces, one list per mode [kN].
        shears_kn: Modal storey shears, one list per mode [kN].
        du_mm: Modal inter-storey drifts, one list per mode [mm].
        shear_srss_kn: SRSS storey shears [kN].
        du_srss_mm: SRSS inter-storey drifts [mm].
        theta_srss: SRSS drift / storey height [-].
    """

    modes: list[Mode]
    forces_kn: list[list[float]]
    shears_kn: list[list[float]]
    du_mm: list[list[float]]
    shear_srss_kn: list[float]
    du_srss_mm: list[float]
    theta_srss: list[float]


def run_rsa(dead_model: str = "actual_shape", live_model: str = "actual_shape",
            n_modes: int = N_MODES, psi_t: float = 1.0) -> RsaResult:
    """Run the modal response-spectrum method on the anchor frame (reading rules 1-3).

    Args:
        dead_model: Key of ``anchor_frame.LOAD_MODELS`` for the weights.
        live_model: Key of ``anchor_frame.LIVE_LOAD_MODELS`` for the weights.
        n_modes: Number of modes combined.
        psi_t: Infill period factor applied to every modal period [-]; 1.0 is
            the bare frame (Day 10 reading rule 1). The anchor value is
            ``seismic.ANCHOR_PSI_T`` (decision of 27 Oct 2026, after the run).

    Returns:
        An RsaResult.
    """
    g = [w.g_kn for w in s.storey_weights(dead_model, live_model)]
    a_max = s.alpha_max_frequent(7, 0.10)
    ms = modes(g, n_modes)
    for m in ms:
        m.period_s *= psi_t
    forces, shears, drifts = [], [], []
    for m in ms:
        f = modal_forces(m, g, a_max, s.TG_ANCHOR_S)
        lat = s.run_lateral(f)
        forces.append(f)
        shears.append(lat.column_shear_kn)
        drifts.append(lat.du_mm)
    du = srss(drifts)
    heights = af.STOREY_HEIGHTS_M
    return RsaResult(ms, forces, shears, drifts, srss(shears), du,
                     [d / (1000.0 * h) for d, h in zip(du, heights)])


def comparison_rows(rsa: RsaResult, bsm: s.SeismicResult,
                    thesis: list[s.ThesisSeismicRow],
                    rsa_anchor: RsaResult | None = None,
                    bsm_anchor: s.SeismicResult | None = None) -> list[dict]:
    """Build ``results/anchor_rsa.csv``: per level, both methods and the thesis.

    Args:
        rsa: The response-spectrum run.
        bsm: The primary base-shear run of Day 9.
        thesis: Rows from ``seismic.read_thesis_seismic``.
        rsa_anchor: The response-spectrum run with ``seismic.ANCHOR_PSI_T``.
        bsm_anchor: The base-shear run with ``seismic.ANCHOR_PSI_T``.

    Returns:
        One dict per level 1-4.
    """
    rows = []
    for i in range(4):
        v4 = thesis[i].v_kn - s.THESIS_LEVEL5_FORCE_KN
        row = {
            "level [text]": i + 1,
            "V_rsa [kN]": round(rsa.shear_srss_kn[i], 2),
            "V_base_shear_method [kN]": round(bsm.shears_kn[i], 2),
            "V_rsa_pct_vs_bsm [%]": round(s.percent_difference(rsa.shear_srss_kn[i], bsm.shears_kn[i]), 1),
            "V_thesis_4storey [kN]": round(v4, 2),
            "V_rsa_pct_vs_thesis_4storey [%]": round(s.percent_difference(rsa.shear_srss_kn[i], v4), 1),
            "du_rsa [mm]": round(rsa.du_srss_mm[i], 3),
            "du_base_shear_method [mm]": round(bsm.lateral.du_mm[i], 3),
            "du_rsa_pct_vs_bsm [%]": round(s.percent_difference(rsa.du_srss_mm[i], bsm.lateral.du_mm[i]), 1),
            "du_thesis_printed [mm]": thesis[i].du_mm,
            "du_rsa_pct_vs_thesis_printed [%]": round(s.percent_difference(rsa.du_srss_mm[i], thesis[i].du_mm), 1),
            "theta_rsa [-]": round(rsa.theta_srss[i], 7),
            "drift_limit_met [text]": str(rsa.theta_srss[i] <= s.DRIFT_LIMIT),
        }
        for j, m in enumerate(rsa.modes):
            row[f"V_mode{m.number} [kN]"] = round(rsa.shears_kn[j][i], 2)
        if rsa_anchor is not None and bsm_anchor is not None:
            row.update({
                "V_rsa_anchor_psi [kN]": round(rsa_anchor.shear_srss_kn[i], 2),
                "V_bsm_anchor_psi [kN]": round(bsm_anchor.shears_kn[i], 2),
                "V_anchor_rsa_pct_vs_bsm [%]": round(s.percent_difference(
                    rsa_anchor.shear_srss_kn[i], bsm_anchor.shears_kn[i]), 1),
                "du_rsa_anchor_psi [mm]": round(rsa_anchor.du_srss_mm[i], 3),
                "du_bsm_anchor_psi [mm]": round(bsm_anchor.lateral.du_mm[i], 3),
                "theta_rsa_anchor_psi [-]": round(rsa_anchor.theta_srss[i], 7),
            })
        rows.append(row)
    return rows


def mode_rows(rsa: RsaResult) -> list[dict]:
    """Build ``results/anchor_rsa_modes.csv``: one row per mode.

    Args:
        rsa: The response-spectrum run.

    Returns:
        Period, alpha, participation factor, mass ratio (and cumulative),
        modal base shear and the level shape for each mode.
    """
    a_max = s.alpha_max_frequent(7, 0.10)
    rows, cum = [], 0.0
    for j, m in enumerate(rsa.modes):
        cum += m.mass_ratio
        row = {
            "mode [text]": m.number,
            "T [s]": round(m.period_s, 4),
            "alpha [-]": round(s.alpha_spectrum(m.period_s, a_max, s.TG_ANCHOR_S), 5),
            "gamma [-]": round(m.gamma, 4),
            "mass_ratio [-]": round(m.mass_ratio, 4),
            "mass_ratio_cumulative [-]": round(cum, 4),
            "base_shear [kN]": round(rsa.shears_kn[j][0], 2),
        }
        for lvl, x in enumerate(m.shape, start=1):
            row[f"shape_level{lvl} [-]"] = round(x, 4)
        rows.append(row)
    return rows


def plot_comparison(rsa: RsaResult, bsm: s.SeismicResult, thesis: list[s.ThesisSeismicRow],
                    path: Path) -> None:
    """Draw ``figures/anchor_seismic_compare.png``: storey shear and drift by storey.

    Storey on the y-axis; three lines per quantity (reading rule 4):
    base-shear method, response spectrum, thesis Table 8-12 (four-storey
    shears V_i - 98.29 kN; printed Δu).

    Args:
        rsa: The response-spectrum run.
        bsm: The primary base-shear run.
        thesis: Rows from ``seismic.read_thesis_seismic``.
        path: Output PNG path.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    storeys = [1, 2, 3, 4]
    v_thesis = [t.v_kn - s.THESIS_LEVEL5_FORCE_KN for t in thesis[:4]]
    du_thesis = [t.du_mm for t in thesis[:4]]
    series = [
        # Categorical slots 1-3 of the dataviz reference palette (validated
        # for colour-vision deficiency); markers and line styles also differ,
        # so identity never rests on colour alone.
        ("Base-shear method", "#2a78d6", "o", "-"),
        ("Response spectrum (3 modes, SRSS)", "#eb6834", "s", "--"),
        ("Thesis Table 8-12", "#1baf7a", "^", ":"),
    ]
    data = {
        "shear": [bsm.shears_kn, rsa.shear_srss_kn, v_thesis],
        "drift": [bsm.lateral.du_mm, rsa.du_srss_mm, du_thesis],
    }
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.2), sharey=True)
    for ax, key, xlabel in zip(axes, ("shear", "drift"),
                               ("Storey shear [kN]", "Inter-storey drift Δu [mm]")):
        for (label, colour, marker, ls), values in zip(series, data[key]):
            ax.plot(values, storeys, color=colour, marker=marker, linestyle=ls, linewidth=1.6,
                    label=label)
        ax.set_xlabel(xlabel)
        ax.set_xlim(left=0)
        ax.grid(True, color="#dddddd", linewidth=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_ylabel("Storey")
    axes[0].set_yticks(storeys)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=8, loc="upper center", ncol=3,
               bbox_to_anchor=(0.5, 0.93))
    fig.suptitle("Anchor frame, axis (2): earthquake at 7 degrees, 0.10 g (bare-frame period)",
                 fontsize=10)
    fig.text(0.01, 0.01, "Thesis shears exclude the level-5 row (decision B4); thesis Δu as printed. "
             "© 2026 Syed Nafiz Reja Hasib.", fontsize=6.5, color="#666666")
    fig.tight_layout(rect=(0, 0.04, 1, 0.88))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, metadata={"Software": None})
    plt.close(fig)


def main(repo_root: Path | None = None) -> dict[str, list[dict]]:
    """Run the response-spectrum check and the 3D periods; save tables and the figure.

    Writes ``results/anchor_rsa.csv``, ``results/anchor_rsa_modes.csv``,
    ``results/anchor_3d_periods.csv`` and ``figures/anchor_seismic_compare.png``.

    Args:
        repo_root: Repository root; defaults to two levels above this file's
            package folder.

    Returns:
        The rows written, keyed ``"rsa"``, ``"modes"`` and ``"periods_3d"``.
    """
    from shellbench import anchor_3d

    root = repo_root or Path(__file__).resolve().parents[2]
    thesis = s.read_thesis_seismic(root)
    rsa = run_rsa()
    bsm = s.run_base_shear()
    rsa_anchor = run_rsa(psi_t=s.ANCHOR_PSI_T)
    bsm_anchor = s.run_base_shear(psi_t=s.ANCHOR_PSI_T, variant="anchor")
    tables = {
        "rsa": comparison_rows(rsa, bsm, thesis, rsa_anchor, bsm_anchor),
        "modes": mode_rows(rsa),
        "periods_3d": anchor_3d.period_rows([m.period_s for m in rsa.modes]),
    }
    af.write_csv(tables["rsa"], root / "results" / "anchor_rsa.csv")
    af.write_csv(tables["modes"], root / "results" / "anchor_rsa_modes.csv")
    af.write_csv(tables["periods_3d"], root / "results" / "anchor_3d_periods.csv")
    plot_comparison(rsa, bsm, thesis, root / "figures" / "anchor_seismic_compare.png")
    return tables


if __name__ == "__main__":
    for name, rows in main().items():
        print("==", name)
        for r in rows:
            print(r)
