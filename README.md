# ShellBench

[![Tests](https://github.com/syednafizreja/ShellBench/actions/workflows/tests.yml/badge.svg)](https://github.com/syednafizreja/ShellBench/actions/workflows/tests.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)
![Status: week 2 of 8](https://img.shields.io/badge/status-week%202%20of%208-orange)

**How much do thin-shell floors cut the whole-building A1–A3 embodied carbon of a GB 50010 / GB 50011 RC frame across 3–8 storeys, and how does the saving change with storey count and seismic intensity once diaphragm, tie and topping needs are met?**

(Revised 22 Oct 2026; see [docs/research_question.md](docs/research_question.md).)

A thinner floor weighs less. Less weight means smaller seismic forces, which can mean smaller beams, columns and footings. ShellBench follows that chain through the whole building, using real design codes, rather than comparing floors on their own.

> **Status.** Week 1 of an 8-week plan is complete (review in [docs/week01_review.md](docs/week01_review.md)); Week 2 finishes the anchor. The thesis building has been audited and its published results typed in as validation targets. The thesis frame runs in OpenSeesPy under dead load (Day 5), live load and the thesis gravity combination (Day 6) the thesis wind forces (Day 8), the GB 50011 base-shear method for earthquake (Day 9) a response-spectrum check with a 3D whole-building model (Day 10) and GB 50010 / GB 50011 design checks of the beams and columns against the thesis steel (Day 11). Every difference above 10 % from the thesis has a written reason; the wind drifts of thesis Table 8-2 fail the 15 % test set before the run, and the notes show why the printed drifts cannot come from one elastic frame. The base-shear method puts the forces up the height the way the thesis did, but its base shear is 19 % lower with the bare-frame period; the notes give the two possible causes. In the design checks every axial ratio passes, but every column (4C22, 0.42 %) is below the 0.75 % code minimum, and two level-1 beam ends are short on their printed bars. First release: [v0.0.1](https://github.com/syednafizreja/ShellBench/releases/tag/v0.0.1), "Baseline spec and gravity check". Daily progress is in [LOG.md](LOG.md).

---

## Approach

The study is checked against one real, fully documented building: the author's own thesis design. That building is validation case 0. Every model must reproduce it before it is trusted on anything else. The result is the generator, the building family and the floor interface, which anyone can run on their own building or floor (see [docs/impact_strategy.md](docs/impact_strategy.md)).

```mermaid
flowchart LR
    T["Thesis building<br/>(4-storey RC frame)"] --> A["Audit<br/>baseline spec"]
    A --> V["Validation<br/>targets"]
    V --> M["Anchor model<br/>OpenSeesPy"]
    M --> G["Generator<br/>building family"]
    G --> F["Design each building twice<br/>flat slab vs shell floor"]
    S["Shell floor module<br/>form-finding + FE check"] --> F
    F --> P1(["Paper 1<br/>whole-building carbon"])
    F --> D[("Open dataset")]
    D --> AI["Surrogate model"] --> P2(["Paper 2<br/>does AI pick the same floor?"])

    classDef done fill:#c8e6c9,stroke:#2e7d32,color:#000;
    classDef doing fill:#fff3c4,stroke:#b8860b,color:#000;
    classDef todo fill:#eeeeee,stroke:#888,color:#000;
    class A,V done;
    class M doing;
    class T,G,S,F,D,AI,P1,P2 todo;
```

Green: done. Yellow: in progress. Grey: not started.

1. **Anchor.** Rebuild the thesis building in code (gravity, wind, earthquake), add the code checks and the embodied-carbon count, and match the thesis results.
2. **Generator.** Write code that designs a building the way the thesis did, prove it on the thesis sizes, then use it to produce a family of buildings.
3. **Shell floor.** Form-find a vaulted floor panel, check it with a benchmarked shell finite-element solver, and size it for thickness, ties and buckling.
4. **Comparison.** Design every building in the family twice, once with a flat slab and once with a shell floor, and explain the saving term by term.
5. **Surrogate.** Train a fast model on the family and test whether it picks the same floor as the full design.

## Roadmap

Each week has a GitHub issue with its goals.

| Week | Dates (2026) | Goal | Release | Status |
|---|---|---|---|---|
| 1 | 19–25 Oct | [Audit the thesis and model it under gravity](https://github.com/syednafizreja/ShellBench/issues/1) | v0.0.1 | Done |
| 2 | 26 Oct–1 Nov | [Finish the anchor: lateral loads, code checks, carbon](https://github.com/syednafizreja/ShellBench/issues/2) | v0.1 (31 Oct) | |
| 3 | 1–6 Nov | [The generator and the building family](https://github.com/syednafizreja/ShellBench/issues/3) | v0.2 | |
| 4 | 7–13 Nov | [The thin-shell floor module](https://github.com/syednafizreja/ShellBench/issues/4) | v0.3 | |
| 5 | 13–21 Nov | [Whole-building results](https://github.com/syednafizreja/ShellBench/issues/5) | dataset DOI (17 Nov) | |
| 6 | 22–29 Nov | [Write and submit Paper 1](https://github.com/syednafizreja/ShellBench/issues/6) | preprint (29 Nov) | |
| 7 | 21 Nov–3 Dec | [The AI surrogate study](https://github.com/syednafizreja/ShellBench/issues/7) | v0.5 | |
| 8 | 4–8 Dec (profile to 13 Dec) | [Paper 2 and the public package](https://github.com/syednafizreja/ShellBench/issues/8) | v1.0 (8 Dec) | |

Dates moved on 26 Oct 2026 with the author's approval (finish earlier, no check dropped). The day-by-day map is [docs/schedule.md](docs/schedule.md).

The hypotheses (H1–H4) will be frozen in public in Week 3, before any family result exists.

Reuse items built into the weeks above (details in [docs/impact_strategy.md](docs/impact_strategy.md)): carbon factors as data files and a Zenodo DOI for every release from v0.1 (Week 2); buildings defined as data, not code (Week 3); a written floor plug-in contract with a conformance test (Week 4); reference problems and a datasheet in the dataset (Week 5); one-command reproduction of each paper's figures (Weeks 6 and 8); JOSS-ready documentation and two tutorials in v1.0 (Week 8).

## Done so far

| Item | What it holds |
|---|---|
| [docs/baseline_spec.md](docs/baseline_spec.md) | Every model input for the thesis building, each with its thesis section or table. 16 inconsistencies found in the thesis (B1–B16), each with the author's decision and reason. |
| [validation/thesis_values/](validation/thesis_values/) | Eight CSV files of thesis results: beam-end moments, column axial forces, D-values, wind drift, seismic storey shear and drift, beam steel, the full live-load distribution table and the roof rows of the combination table. Every row names its source table. Flags D1–D21 mark values that look wrong; they are left as printed. |
| [tests/](tests/) | Checks that every validation file has units in its headers, no empty cells and numbers where numbers belong; closed-form and equilibrium tests of the anchor frame. |
| [src/shellbench/anchor_frame.py](src/shellbench/anchor_frame.py) | The thesis transverse frame as a 2D elastic OpenSeesPy model, loaded with dead and live load the way the thesis distributes them. |
| [src/shellbench/combinations.py](src/shellbench/combinations.py) | The thesis load combinations as data (1.3D + 1.5L now; wind and seismic ones wait for their load cases). |
| [src/shellbench/thesis_checks.py](src/shellbench/thesis_checks.py) | Arithmetic checks on the thesis tables: column sums and joint balance of the live-load moment distribution, factors of the combination table. |
| [results/](results/) | Dead-load, live-load and 1.3D + 1.5L comparisons with the thesis (beam-end moments, column axial forces, % differences, check runs), and the thesis-table checks. Causes of every difference above 10 % in [docs/anchor_notes.md](docs/anchor_notes.md). |
| [docs/gap_matrix.md](docs/gap_matrix.md) | 23 papers from 2020-2026, each with what it studied, whether seismic loads and ties were included, and a section locator; gap statements G1-G4. Sources in [docs/reading_list.md](docs/reading_list.md), all legal open copies. |
| [docs/goal_stress_test.md](docs/goal_stress_test.md) | Red-team review of the research question (holes H1-H9) and the fixes adopted. |
| [docs/week01_review.md](docs/week01_review.md) | Week 1 review: every Done-when line checked against a file, and the weak points to handle before the anchor report. |
| [notes/gb50011_base_shear_primer.md](notes/gb50011_base_shear_primer.md) | Study note on the GB 50011 base-shear method worked on the thesis building, with the clauses to check before Day 9. |
| [docs/impact_strategy.md](docs/impact_strategy.md) | How others will reuse and cite ShellBench: what the charter already covers, additions A1-A10 placed in Weeks 2-8 without moving a date, and ideas parked under Later. |
| [docs/q1_standards.md](docs/q1_standards.md) | Journal and publication-ethics rules (Elsevier, Springer Nature, COPE) that the project follows every day, with a daily compliance check. |

## The anchor building

A four-storey cast-in-place RC moment-frame office building in Panzhihua, Sichuan, China, designed by the author as a 2023 thesis. Values below are from [docs/baseline_spec.md](docs/baseline_spec.md); the ID in brackets is the row there.

| Property | Value |
|---|---|
| Transverse spans | 7.2 m + 6.6 m + 7.2 m (G3) |
| Storey height | 3.6 m typical, 4.55 m ground storey (G6, G7) |
| Columns | 600 × 600 mm (M5) |
| Frame beams | 300 × 600 mm side spans, 300 × 500 mm corridor (M1, M2) |
| Slab | 120 mm (G10) |
| Materials | C40 concrete, HRB400 bars (X1, X5) |
| Seismic | Intensity 7 (0.10 g), group 1, site class II, Tg = 0.35 s, seismic grade three (S1–S5) |
| Design codes | Chinese codes GB 50009 (loads), GB 50010 (concrete), GB 50011 (seismic) |

The thesis is kept private and is not in this repository. Only the values typed from it are.

## Repository map

```
ShellBench/
├── src/shellbench/       Python package (anchor frame, load combinations, thesis checks)
├── tests/                pytest suite
├── docs/                 specifications, literature, charter and journal-rule notes
├── validation/
│   └── thesis_values/    thesis results as CSV validation targets, with flags
├── data/                 input data (empty so far)
├── results/              generated results (anchor frame, gravity)
├── figures/              generated figures (empty so far)
├── paper/                manuscripts (empty so far)
├── notes/                working notes (empty so far)
├── LOG.md                daily research log
├── CLAUDE.md             rules for AI assistance
├── environment.yml       conda environment "research"
├── pyproject.toml        package and pytest configuration
└── CITATION.cff          citation metadata
```

## Getting started

Requires [conda](https://docs.conda.io/). The environment pins Python 3.12, which OpenSeesPy needs.

```bash
git clone https://github.com/syednafizreja/ShellBench.git
cd ShellBench
conda env create -f environment.yml
conda activate research
pip install -e .
pytest
```

The environment includes OpenSeesPy (frame analysis), gmsh (meshing) and CalculiX (shell finite elements), plus the usual numpy, scipy, pandas and matplotlib.

## Working rules

- **SI units everywhere.** Every CSV header states its unit, e.g. `M_end [kN*m]`.
- **Every number traces to a source:** a thesis section or table, a code clause, or the code in this repository.
- **Thesis errors are flagged, not fixed.** Values are typed as printed, and disputed ones are settled by a recorded decision.
- **Judgement is marked.** Anything that is reasoning rather than a sourced value carries `[J]`.

## Use of AI assistance

Code and documents in this repository are drafted with Claude (Anthropic) and checked by the author. All engineering decisions are the author's. The rules Claude works under are in [CLAUDE.md](CLAUDE.md).

## How to cite

Citation metadata is in [CITATION.cff](CITATION.cff); GitHub's "Cite this repository" button uses it. A software DOI is planned for v1.0.

## Author

Syed Nafiz Reja Hasib

## Licence

MIT. See [LICENSE](LICENSE).
