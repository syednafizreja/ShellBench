# ShellBench

Quantifying the whole-building embodied-carbon savings of thin-shell floors in code-designed reinforced-concrete frames in seismic zones.

## Research question

How much embodied carbon do thin-shell floors save in code-designed RC frames in seismic zones, once every knock-on effect is counted?

## Status

Work in progress.

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
├── pyproject.toml    package and pytest configuration
├── environment.yml   conda environment specification
├── CLAUDE.md         rules for AI assistance
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

## Use of AI assistance

The code in this repository is written with Claude (Anthropic) and checked by the author. The rules Claude works under are in [CLAUDE.md](CLAUDE.md).

## Author

Syed Nafiz Reja Hasib

## Licence

Released under the MIT Licence. See [LICENSE](LICENSE).
