# Surrogate study notes (Paper 2, H4)

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Code: `src/shellbench/ml/` (data and splits, three models, conformal intervals). Rules: preregistration 2.4. Results shown here come from pre-release data and test the pipeline only; Paper 2 uses the published dataset.

## Why a random split flatters a model

A building appears in the data once per floor variant and topping: up to 144 rows with the same storey count and PGA. A random split puts some of these rows in training and some in testing. The test row is then almost a copy of a training row, so the model looks accurate without having learnt anything about a building it has not seen. The unseen-storeys split removes every row of one storey count from training, so the test measures what a designer needs: a prediction for a height the model has not met.

## Split-conformal prediction on 10 points

Suppose the model, fitted on the training rows, makes these absolute errors on 10 calibration rows [kgCO2e/m2]:

0.2, 0.3, 0.5, 0.6, 0.8, 0.9, 1.1, 1.2, 1.5, 2.0

1. n = 10 and the target coverage is 90 %.
2. Take k = ceil((n + 1) x 0.9) = ceil(9.9) = 10.
3. The 10th smallest error is 2.0. This is the half-width.
4. For a new building with prediction 100.0, the interval is 98.0 to 102.0.

Why it works: if the new building is exchangeable with the calibration rows, its error is equally likely to land in any of the 11 positions among the 10 calibration errors and itself. It is no larger than the 10th smallest of the ten in at least 10 of 11 cases, which is 91 %. With only 9 calibration points k would be ceil(9.0) = 9 and the coverage guarantee 90 %.

When it fails: on the unseen-storeys split, the test errors are not drawn from the same distribution as the calibration errors, because the calibration rows come from storey counts the model was trained on. Then coverage can fall below 90 %, and the report says so.

## Frozen choices [J]

- Targets: whole-building carbon, floor carbon, largest drift ratio, period T1.
- Splits: random (80 / 20) and unseen storeys (leave one storey count out, six folds), as in preregistration 2.4. The playbook mentions a third split; adding it would need a change-log entry.
- Hyperparameter grids and the Gaussian-process subsample (1,000 rows): `ml/train.py`. Frozen by commit before the dataset DOI. **Frozen 9 Nov 2026 at commit 5c11ce8** (`src/shellbench/ml/` unchanged since PR #151); approved by the author on 9 Nov 2026. Any later change to models, grids, split rules or the calibration fraction needs a change-log entry in the preregistration.
- Calibration set: 20 % of the training rows.

## Day 46: leakage test and decision test (10 Nov 2026, pre-release data)

Code: `src/shellbench/ml/decision.py`. It adds a test and changes no frozen setting (models, grids, split rules, calibration fraction are as at commit 5c11ce8).

**Leakage test.** Six checks per fold: no storey count, building or identical feature vector in both train and test; train and test rows disjoint; calibration rows inside the training rows and outside the test rows. Two global checks: no target and no identifier among the features. Result: unseen-storeys split 36 of 36 pass. The random split fails the storey and building checks, as it should (it mixes rows of one building); that failure shows the test can fail. H4 may now be judged.

**Decision test.** For each building with a slab and a rigid shell row (33 of 36), the full analysis picks the lower whole-building carbon: the slab, or the best rigid shell variant. The surrogate (HGB, fitted without that building's storey count) picks the same way from its predictions.
- Agreement 31 of 33 = 93.9 %. Threshold 80 % (preregistration 2.4).
- Always choosing the shell agrees in 32 of 33 = 97.0 %. So the surrogate does worse than the trivial rule here. The 80 % criterion is easy to meet when the shell wins almost everywhere; I report both.
- The full analysis picks the slab once (s05-p030, saving -0.3 %). The two misses are that building and s04-p005 (saving 4.6 % by the full analysis, the surrogate predicts -0.3 %). Neither is a clear call.
- Shell variant: the surrogate picks the same variant as the full analysis in 5 of 33 (15 %). Mean regret 5.5 kgCO2e/m2 (3.7 % of the best shell carbon); largest 83.9. The surrogate ranks systems better than it ranks variants [J].
- RMSE of the saving, surrogate against full analysis: 5.8 percentage points, on savings of 3 to 9 % for most buildings.

**H4 read on pre-release data (10 Nov; the verdict of 13 Nov is in the next section).** Error ratio unseen/random for HGB 25.62 / 11.30 = 2.27 (needs 1.5): holds. Conformal coverage on unseen storeys 73.3 % (needs 88 to 92 %): fails. Decision agreement 93.9 % (needs 80 %): holds. Two of three: *partly supported* by the rule in 2.4. The published-data run on 12 Nov decides.

**Limits for Paper 2.** 33 buildings in the decision test is small: one building moves agreement by 3 points. The slab family has one design per building. Tuning grids were frozen before this run.

## Day 47: H4 verdict on the published data (13 Nov 2026)

The frozen pipeline (commit 5c11ce8, unchanged) ran once on the family files of the published dataset (Zenodo 10.5281/zenodo.24194144). Run time 13 minutes on four cores. Leakage test first: 36 of 36 checks pass on the unseen-storeys split. Results: error ratio 25.62 / 11.30 = 2.27 (holds); conformal coverage on unseen storeys 73.3 % (fails); decision agreement 93.9 %, against 97.0 % for always choosing the shell (holds). **H4 partly supported**, two of three conditions (preregistration section 3). The output files were byte-identical to the pre-release run: the family files differ only in the `release` and `shellbench_version` columns, and the pipeline is deterministic.

Why coverage fails: the calibration rows are drawn from the storey counts the model was trained on, so exchangeability with the held-out storey count does not hold. The shortfall is largest at 7 storeys (56.1 %) and smallest at 6 storeys (87.1 %). The random split gives 90.1 %, so the method works when the exchangeability assumption holds. A way to restore coverage on unseen storeys (for example calibrating on a held-out storey count) is a new method, not part of this frozen study; it belongs in Paper 2 as future work [J].

Figures for Paper 2 (house style, `python -m shellbench.figures --paper`): `surrogate_parity`, `surrogate_coverage`, `surrogate_decision`.
