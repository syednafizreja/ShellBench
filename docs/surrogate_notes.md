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
