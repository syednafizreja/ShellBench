# ShellBench

Quantifying the whole-building embodied-carbon savings of thin-shell floors in code-designed reinforced-concrete frames in seismic zones.

## Research question

How much embodied carbon do thin-shell floors save in code-designed RC frames in seismic zones, once every knock-on effect is counted?

## Status

Work in progress — Day 0.

## Repository structure

```
ShellBench/
├── src/shellbench/   Python package (analysis and design code)
├── tests/            pytest test suite
├── data/             input data
├── results/          generated results
├── figures/          generated figures
├── notes/            working notes
├── paper/            manuscript
├── environment.yml   conda environment specification
├── CITATION.cff      citation metadata
├── LICENSE           MIT licence
└── LOG.md            research log
```

## Installation

Create the conda environment `research` (Python 3.12) from `environment.yml`, then activate it:

```bash
conda env create -f environment.yml
conda activate research
```

## Running tests

From the repository root, with the `research` environment active:

```bash
pytest
```

## Author

Syed Nafiz Reja Hasib

## Licence

Released under the MIT Licence. See [LICENSE](LICENSE).
