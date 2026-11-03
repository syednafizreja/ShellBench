# Preregistration: hypotheses H1-H4

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

This file holds the four hypotheses of ShellBench, the analysis that will test each one, and, at the end of the project, the verdict on each. The hypotheses below are frozen. They are copied word for word from the ShellBench Project Charter (amended 22 Oct 2026, p. 11, "Hypotheses (frozen; never reworded)") and must never be reworded. Each verdict will be reported as it comes out, including any hypothesis that fails.

## Status

| Part | What it holds | Status |
|---|---|---|
| 1. Hypotheses | H1-H4, verbatim | Committed 25 Oct 2026, before any family result exists |
| 2. Analysis plan | Variables, comparisons and decision rules for each hypothesis | Draft added 3 Nov 2026; pre-registered when the author approves it and it is merged, before any family row |
| 3. Verdicts | One verdict per hypothesis, with the result files behind it | After Week 5 (H1-H3) and Week 7 (H4) |

The hypotheses were committed ahead of the 3 Nov date so that the public record of their wording is as early as possible. No family result, pilot run or surrogate run existed when they were committed: the repository at this point holds only the anchor building under gravity load (Days 5-6). Git history gives the timestamp.

## 1. Hypotheses (frozen)

**H1:** The whole-building saving is smaller than the floor-level saving but stays positive across the family.

**H2:** The saving grows with seismic intensity and storey count, because mass reductions compound into a smaller lateral system.

**H3:** Without a topping, the shell floor cannot be assumed to act as a rigid diaphragm. The topping it needs takes back a measurable share of the saving.

**H4:** Surrogate error on unseen storey counts is clearly larger than on random test splits. Conformal intervals restore the stated coverage, and the surrogate's choice of floor system agrees with the full analysis in most cases.

## 2. Analysis plan

Draft by the AI assistant, 3 Nov 2026 (Day 17), for the author to approve or change. **It counts as pre-registered only once the author approves it and the PR that adds it is merged, and that must happen before any family row exists.** At the time of writing the repository holds the anchor building, the generator (Day 16) and the shell benchmarks (Day 24). No family, pilot or surrogate row exists. Every threshold marked [J] is a choice, not a code value, and the author may change it before approval but not after.

### 2.1 Quantities used by all four hypotheses

- **Carbon:** A1-A3 only, kgCO2e per m² of floor area, from the take-off of `carbon.py` and `data/carbon_factors.csv`, using one factor set (D29). The same factors are used for both floor systems.
- **Conventional baseline:** the lowest-carbon code-compliant conventional floor on the same grid, storey height and loads (charter, "Fair baseline"). The saving against the anchor-style 120 mm beam-slab is reported as a secondary result.
- **Floor-level saving:** S_floor = (C_floor,conv − C_floor,shell) / C_floor,conv, where C_floor is the floor system's carbon (slab or shell, topping, ties, secondary beams) per m².
- **Whole-building saving:** S_bldg = (C_bldg,conv − C_bldg,shell) / C_bldg,conv, where both buildings are sized again by the generator for their own mass. Absolute savings (kgCO2e/m²) are reported next to every percentage.
- **The family:** 3 to 8 storeys, with PGA at 0.05, 0.10, 0.15, 0.20, 0.30 and 0.40 g (charter). Any PGA level whose GB 50011 values (Tables 5.1.4-1, 6.1.2 and 6.3.6) are still [?] when the family runs is left out. The verdict then says which levels were tested.
- **Valid buildings:** every building with both versions passing every generator check. Failed or non-converged buildings are counted and listed by cause, never dropped silently. If more than 5 % of the family fails [J], no verdict is given until the cause is fixed and the run is repeated in full.
- **Uncertainty:** 95 % intervals come from a bootstrap with 2,000 resamples of buildings and a fixed seed [J].

### 2.2 H1: the saving shrinks at building level but stays positive

- **Measure:** S_floor and S_bldg for every valid building.
- **Supported** if S_bldg < S_floor and S_bldg > 0 in at least 95 % of valid buildings [J], and the 5th percentile of S_bldg is above 0.
- **Partly supported** if S_bldg > 0 in at least 95 % of buildings but S_bldg ≥ S_floor in more than 5 %. The building-level knock-on is then larger than the floor-level saving, which is a finding in its own right.
- **Not supported** otherwise. The PGA and storey cells where S_bldg ≤ 0 are reported.

### 2.3 H2: the saving grows with seismic intensity and storey count

- **Measure:** the absolute whole-building saving ΔC = C_bldg,conv − C_bldg,shell (kgCO2e/m²), against PGA and storey count n.
- **Model:** a linear regression ΔC = b0 + b1·PGA + b2·n + b3·PGA·n over the valid buildings. Spearman ρ for each variable is reported as a check that does not assume a straight line.
- **Supported** if b1 > 0 and b2 > 0 (or the marginal effects at the family mean, if b3 is in the model) with 95 % bootstrap intervals above 0, **and** the mechanism shows: the share of ΔC coming from columns, beams and footings rises with PGA (Spearman ρ > 0, with its interval above 0).
- **Partly supported** if only one of PGA or n meets the rule. The verdict names which one.
- **Not supported** if neither does. If only 0.10 g can be run (see 2.1), the PGA half is "not tested", not "not supported".
- The percentage saving S_bldg is analysed the same way as a secondary result.

### 2.4 H3: without a topping the shell is not a rigid diaphragm, and the topping takes back a measurable share

- **Rigidity test:** for each shell floor without a topping, the in-plane FE model (CalculiX, floor-r2) under the storey seismic force gives the largest in-plane diaphragm deformation δ_d and the mean storey drift Δ. The floor is treated as not rigid if δ_d / Δ > 2. This is the ASCE 7-16 cl. 12.3.1.3 definition [?]. The GB 50011 / JGJ 3 rule, if one exists, replaces it once it is opened [?].
- **Topping share:** R = (S_bldg without topping − S_bldg with the required topping) / S_bldg without topping. The topping thickness comes from the Day 27 rule.
- **Supported** if the untopped shell fails the rigidity test in more than half of the valid buildings [J], **and** the median R is at least 10 % [J] with a 95 % interval above 0.
- **Partly supported** if only one half holds. **Not supported** if neither does.

### 2.5 H4: surrogate error, coverage and decisions

The models, features, hyperparameters and split rules are fixed in the surrogate freeze commit, which the author approves before the dataset DOI (schedule.md). They are tuned on the conventional family only, and then run once on the published data.

- **Splits:** (a) a random 80/20 split of buildings with a fixed seed; (b) leave-one-storey-count-out, holding out each storey count from 3 to 8 in turn.
- **Error:** RMSE of predicted whole-building carbon (kgCO2e/m²) on each test set. The error ratio is r = RMSE(storey hold-out, mean over folds) / RMSE(random).
- **"Clearly larger"** means r ≥ 1.5 [J], with the 95 % bootstrap interval of r above 1.
- **Coverage:** split conformal intervals at a nominal 90 % [J]. Coverage counts as restored if the empirical coverage on the storey hold-out is at least 88 % [J] on average over folds, with no single fold below 80 % [J].
- **Decisions:** in each test building the surrogate picks the floor system with the lower predicted carbon, and the full analysis gives the true choice. "Most cases" means agreement in at least 80 % of test buildings [J] on the storey hold-out.
- **Verdict:** supported if all three parts hold. Otherwise each part is reported on its own as holding or not.

### 2.6 Rules that cover all four

- No hypothesis is reworded, and no threshold above changes after approval.
- Any departure from this plan goes into a dated "Deviations" list below, with the reason, before the verdict it affects.
- Each hypothesis is judged by its own rule. No result is reported as "significant" unless it meets that rule.
- Sensitivity cases are reported next to the verdicts and do not change them. They cover the second carbon factor set (if the author supplies one), the beam-stiffness factor 1.5 against 2.0, and ψ_T from 0.6 to 0.9.

### Deviations

None yet.

## 3. Verdicts

None yet.
