# Contributing to ShellBench

© 2026 Syed Nafiz Reja Hasib.

ShellBench is a frozen research record. Its results back pre-registered hypotheses, so changes follow the rules below. Issues and pull requests are welcome; a change that would alter a result needs a dated entry in the change log of [docs/preregistration.md](docs/preregistration.md).

## Rules

1. **No invented values.** Never invent references, numbers, code clauses, results or DOIs. A value that cannot be traced is marked `[?]` with the rule that closes it.
2. **Every number has a source:** a thesis section or table, a code clause, a paper page, or the code in this repository.
3. **Thesis errors are flagged, not fixed.** Values are typed as printed; disputed ones are settled by a recorded decision in [docs/baseline_spec.md](docs/baseline_spec.md).
4. **The pre-registration is fixed.** Hypotheses, thresholds and the analysis plan change only by a dated amendment that says why. Verdicts are reported as found.
5. **Plain British English.** Short sentences, no hype words. Judgement that is not a sourced value is marked `[J]`.

## Code standards

- SI units everywhere; every CSV header states its unit, e.g. `M_end [kN*m]`.
- Every public function has a docstring.
- No hidden constants: a constant in the source names its clause or source.
- Global equilibrium is asserted on every frame analysis.
- Figures follow [docs/visual_standard.md](docs/visual_standard.md) and are drawn from `results/` by script.

## Checks before a pull request

```bash
pip install -e . --no-deps
pytest
```

All tests must pass, and `git status` must show no change under `results/` unless the change is intended and recorded. If `results/` changes on purpose, rerun `python scripts/make_checksums.py` after committing and commit the new `SHA256SUMS`.

## Markers

| Marker | Meaning |
|---|---|
| `[J]` | A judgement call, accepted or changed by the author |
| `author to confirm` | A reading or value the author still has to confirm |
| `[?]` | A missing value, with the rule that closes it |
