"""Load combinations used by the thesis (anchor, Layer 1).

File: src/shellbench/combinations.py

What this module does
---------------------
It holds the load combinations the thesis used (Th §8.7 and the headers of
Tables 8-13 and 8-15; docs/baseline_spec.md S13) and combines load-case
results linearly with them. The model is linear-elastic, so a combination of
load effects equals the effect of the combined load, and each case is solved
once.

The combinations are stored as data (``THESIS_COMBINATIONS``), one factor per
load case. A load case is a name:

``"D"``          dead load (Day 5)
``"L"``          live load (Day 6)
``"W_left"``     wind from the left (Day 8)
``"W_right"``    wind from the right (Day 8)
``"GE"``         gravity load representative value for seismic design (Day 9)
``"E_left"``     horizontal earthquake from the left (Day 9)
``"E_right"``    horizontal earthquake from the right (Day 9)

A combination whose cases are not yet solved is reported as pending, not
silently skipped. On Day 6 only ``1.3D + 1.5L`` can be evaluated.

Sources and their status
------------------------
- Partial factors 1.3 (dead) and 1.5 (live, wind) and the combination values
  0.6 (wind accompanying live) and 0.7 (live accompanying wind): Th §8.7 and
  the printed headers of Tables 8-13 and 8-15. The 1.3 and 1.5 equal the
  minimum values of GB 55001-2021 cl. 3.1.13 items 1 and 4 (checked 24 Oct
  2026 against the online text; the author to confirm in their copy). The
  thesis does not cite GB 55001. The 0.6 and 0.7 are not traced to a clause.
- Seismic combination 1.2 x gravity + 1.3 x earthquake: Th §8.7 text, which is
  garbled ("multiplied by1.21.3 times"). The reading equals GB 50011-2010
  cl. 5.4.1 and Table 5.4.1 (gamma_G = 1.2, gamma_Eh = 1.3), the code the
  thesis cites (checked 24 Oct 2026 against the 2010 text). The definition of
  ``GE`` is not made here.
- Current seismic factors for Layer 2: GB 55002-2021 cl. 4.3.2, Tables
  4.3.2-1 and 4.3.2-2: gamma_G >= 1.3, gamma_Eh >= 1.4 when only horizontal
  earthquake is computed (checked 24 Oct 2026 against the online text; the
  author to confirm in their copy). In force from 1 Jan 2022, so it applied
  when the thesis was completed (29 May 2023); the thesis values are lower
  (flag D21). ``CODE_SEISMIC_COMBINATIONS`` holds these; the anchor keeps
  the thesis values so that it can reproduce the thesis.

Units: whatever the case results carry (kN, kN*m); factors are dimensionless.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass, field

#: Partial factor on dead load [-]. Th §8.7; Tables 8-13, 8-15 headers.
GAMMA_G: float = 1.3

#: Partial factor on live load [-]. Th §8.7; Tables 8-13, 8-15 headers.
GAMMA_Q: float = 1.5

#: Partial factor on wind load [-]. Th §8.7; Tables 8-13, 8-15 headers
#: ("1.5 x (0.7 live + wind)").
GAMMA_W: float = 1.5

#: Combination value of wind when live load leads [-]. Th §8.7; Table 8-13
#: header "1.3 dead + 1.5 x (live + 0.6 wind)".
PSI_WIND: float = 0.6

#: Combination value of live load when wind leads [-]. Th §8.7; Table 8-13
#: header "1.3 dead + 1.5 x (0.7 live + wind)".
PSI_LIVE: float = 0.7

#: Partial factor on the gravity representative value in the seismic
#: combination, as the thesis used it [-]. Th §8.7 text (garbled);
#: equals GB 50011-2010 cl. 5.4.1.
GAMMA_EG: float = 1.2

#: Partial factor on the horizontal earthquake action, as the thesis used
#: it [-]. Th §8.7 text (garbled); equals GB 50011-2010 Table 5.4.1.
GAMMA_EH: float = 1.3

#: Minimum partial factor on the gravity load in the seismic combination
#: under the current code [-]. GB 55002-2021 cl. 4.3.2, Table 4.3.2-1.
GAMMA_EG_CODE: float = 1.3

#: Minimum partial factor on the horizontal earthquake action, horizontal
#: earthquake only, under the current code [-]. GB 55002-2021 cl. 4.3.2,
#: Table 4.3.2-2.
GAMMA_EH_CODE: float = 1.4


@dataclass(frozen=True)
class Combination:
    """One linear load combination.

    Attributes:
        name: Short label as the thesis writes it.
        factors: Load-case name -> factor applied to that case's effects.
        source: Where the combination comes from.
        status: ``"thesis"`` for factors the thesis used, ``"code"`` for the
            current code minimum values used by Layer 2.
    """

    name: str
    factors: dict[str, float] = field(default_factory=dict)
    source: str = ""
    status: str = "thesis"

    def cases(self) -> set[str]:
        """Return the names of the load cases this combination needs.

        Returns:
            The keys of ``factors``.
        """
        return set(self.factors)


_TABLE_SRC = "Th s8.7; Table 8-13 and 8-15 headers; baseline_spec S13"
_SEISMIC_SRC = "Th s8.7 text (garbled), read as GB 50011-2010 cl. 5.4.1"
_CODE_SEISMIC_SRC = "GB 55002-2021 cl. 4.3.2, Tables 4.3.2-1 and 4.3.2-2"

#: The combinations of Th §8.7, in the order of Table 8-13.
THESIS_COMBINATIONS: tuple[Combination, ...] = (
    Combination("1.3D+1.5L", {"D": GAMMA_G, "L": GAMMA_Q}, _TABLE_SRC),
    Combination("1.3D+1.5(L+0.6W_left)",
                {"D": GAMMA_G, "L": GAMMA_Q, "W_left": GAMMA_Q * PSI_WIND}, _TABLE_SRC),
    Combination("1.3D+1.5(L+0.6W_right)",
                {"D": GAMMA_G, "L": GAMMA_Q, "W_right": GAMMA_Q * PSI_WIND}, _TABLE_SRC),
    Combination("1.3D+1.5(0.7L+W_left)",
                {"D": GAMMA_G, "L": GAMMA_W * PSI_LIVE, "W_left": GAMMA_W}, _TABLE_SRC),
    Combination("1.3D+1.5(0.7L+W_right)",
                {"D": GAMMA_G, "L": GAMMA_W * PSI_LIVE, "W_right": GAMMA_W}, _TABLE_SRC),
    Combination("1.2GE+1.3E_left", {"GE": GAMMA_EG, "E_left": GAMMA_EH},
                _SEISMIC_SRC),
    Combination("1.2GE+1.3E_right", {"GE": GAMMA_EG, "E_right": GAMMA_EH},
                _SEISMIC_SRC),
)

#: Seismic combinations with the current code minimum factors, for the
#: generator (Layer 2). Not used by the anchor, which reproduces the thesis.
CODE_SEISMIC_COMBINATIONS: tuple[Combination, ...] = (
    Combination("1.3GE+1.4E_left", {"GE": GAMMA_EG_CODE, "E_left": GAMMA_EH_CODE},
                _CODE_SEISMIC_SRC, "code"),
    Combination("1.3GE+1.4E_right", {"GE": GAMMA_EG_CODE, "E_right": GAMMA_EH_CODE},
                _CODE_SEISMIC_SRC, "code"),
)

#: What Table 8-13 actually computed in its "1.3 Dead load + 1.5 x live"
#: column: 13 of the 15 roof rows equal 1.0 x dead + 1.5 x live; the two
#: D-support rows fit neither factor set (checked in
#: tests/test_combinations.py against validation/thesis_values/
#: combination_beam_roof.csv). Kept only to document that finding; it is not
#: a design combination.
THESIS_AS_COMPUTED_GRAVITY: Combination = Combination(
    "1.0D+1.5L (as computed in Table 8-13)", {"D": 1.0, "L": GAMMA_Q},
    "Th Table 8-13, level-5 rows, column '1.3 Dead load + 1.5 x live'", "thesis")


def is_available(combo: Combination, cases: Mapping[str, object]) -> bool:
    """Say whether every load case a combination needs has been solved.

    Args:
        combo: The combination.
        cases: Solved load cases keyed by case name.

    Returns:
        True if all of ``combo.cases()`` are keys of ``cases``.
    """
    return combo.cases() <= set(cases)


def combine(cases: Mapping[str, Mapping[Hashable, float]],
            combo: Combination) -> dict[Hashable, float]:
    """Combine load-case effects linearly: sum of factor x effect.

    Every case used must give the same set of keys (for example, the same
    beam ends), so that no effect is dropped by accident.

    Args:
        cases: Load-case name -> mapping of effect key -> value.
        combo: The combination to apply.

    Returns:
        Effect key -> combined value.

    Raises:
        KeyError: If a case the combination needs is missing.
        ValueError: If the cases do not share the same keys.
    """
    missing = combo.cases() - set(cases)
    if missing:
        raise KeyError(f"{combo.name}: load cases not solved yet: {sorted(missing)}")
    names = sorted(combo.cases())
    keys = set(cases[names[0]])
    for name in names[1:]:
        if set(cases[name]) != keys:
            raise ValueError(f"{combo.name}: case {name} has different effect keys")
    return {k: sum(combo.factors[n] * cases[n][k] for n in names) for k in keys}


def evaluate_all(cases: Mapping[str, Mapping[Hashable, float]],
                 combos: tuple[Combination, ...] = THESIS_COMBINATIONS
                 ) -> tuple[dict[str, dict[Hashable, float]], list[str]]:
    """Evaluate every combination whose cases are solved.

    Args:
        cases: Load-case name -> mapping of effect key -> value.
        combos: Combinations to try; defaults to the thesis set.

    Returns:
        (results, pending): results maps combination name to combined
        effects; pending lists the names that still need unsolved cases.
    """
    results, pending = {}, []
    for c in combos:
        if is_available(c, cases):
            results[c.name] = combine(cases, c)
        else:
            pending.append(c.name)
    return results, pending
