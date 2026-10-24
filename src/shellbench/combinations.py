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
  the printed headers of Tables 8-13 and 8-15. The author should confirm in
  their own copy which code clause gives them (GB 55001-2021 or the revised
  GB 50009 [?]); this module does not supply a clause.
- Seismic combination 1.2 x gravity + 1.3 x earthquake: Th §8.7 text, which is
  garbled ("multiplied by1.21.3 times") [?]. To be checked against GB 50011
  in the author's copy before Day 9 uses it. The definition of ``GE`` is not
  made here.

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
#: combination [-]. Th §8.7 text (garbled) [?].
GAMMA_EG: float = 1.2

#: Partial factor on the horizontal earthquake action [-]. Th §8.7 text
#: (garbled) [?].
GAMMA_EH: float = 1.3


@dataclass(frozen=True)
class Combination:
    """One linear load combination.

    Attributes:
        name: Short label as the thesis writes it.
        factors: Load-case name -> factor applied to that case's effects.
        source: Where the combination comes from.
        status: ``"thesis"`` for factors printed in the thesis, ``"unverified"``
            for factors read from garbled text [?].
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
                "Th s8.7 text (garbled)", "unverified"),
    Combination("1.2GE+1.3E_right", {"GE": GAMMA_EG, "E_right": GAMMA_EH},
                "Th s8.7 text (garbled)", "unverified"),
)

#: What Table 8-13 actually computed in its "1.3 Dead load + 1.5 x live"
#: column: every roof row equals 1.0 x dead + 1.5 x live (checked in
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
