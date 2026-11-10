# Visual standard and design review

© 2026 Syed Nafiz Reja Hasib. All rights reserved.

Adopted 9 Nov 2026. This file is the bar every ShellBench output has to clear before it leaves the repository: figures, paper graphics, the README, command-line output, release notes, slides and social cards. The author set the rule on 9 Nov 2026: nothing should look quick or ordinary, and everything should read as careful, expert work. The house style makes the easy part automatic. The review below catches the rest.

Presentation never changes a number. A figure shows only values that sit in a file in `results/`, and restyling is done by redrawing from those files (`python -m shellbench.figures`), never by re-running an analysis.

## 1. The house style in numbers

| Item | Value | Source |
|---|---|---|
| Figure widths | 90 mm (single column), 140 mm (1.5 column), 190 mm (full width) | Elsevier, Artwork sizing (read 9 Nov 2026) |
| Lettering | 7 pt at printed size; nothing smaller, except sub/superscripts at 6 pt minimum | Elsevier, Artwork sizing |
| Fonts | Arial; Liberation Sans on Linux (same metrics); embedded as TrueType in PDF | Elsevier, Artwork overview |
| Vector masters | PDF and SVG, text kept as text in SVG | Elsevier, Artwork overview (PDF accepted for all artwork) |
| Raster preview | PNG at 600 dpi [J]; if a journal wants a raster, TIFF at 1000 dpi for line art | Elsevier, Artwork sizing |
| Axes | left and bottom spines only, 0.6 pt, ticks out, 3 pt long [J] | house choice |
| Grid | hairline 0.4 pt `#e1e0d9`, one direction only, behind the data [J] | dataviz reference palette |
| Data lines | 1.25 pt, round caps; markers 4 pt [J] | house choice |
| Colours | fixed categorical order (below); diverging blue/red with grey midpoint | dataviz reference palette, validated |
| Panel labels | bold (a), (b), ... at 8 pt, top left outside the plot area [J] | house choice |
| Footer | repository figures: owner, ShellBench, data file, qualifier; paper figures: none | author rule 23 Oct 2026; journal credit line |

Links: https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing and .../artwork-overview.

Everything marked [J] is a house choice, not a rule from a source. It can change, but only here, and then for every figure at once.

## 2. Colour

Colour is given a job before it is given a value.

- **Identity** (models, methods, elements): categorical slots in fixed order. `#2a78d6` blue, `#eb6834` orange, `#1baf7a` aqua, `#eda100` yellow, `#e87ba4` magenta, `#008300` green, `#6250d6` violet, `#e34948` red. A series keeps its colour in every figure. Colour never follows rank, and slots are never cycled.
- **Direction** (carbon added or removed): blue for less carbon, red for more, neutral grey `#52514e` for totals.
- **Magnitude**: one hue, light to dark. Never a rainbow.
- **Reference bands** (tolerances, target bands): neutral fill `#f0efec`, labelled in the legend.

Validator runs (dataviz `validate_palette.js`, light surface, 9 Nov 2026):

| Set | Pairs | Result |
|---|---|---|
| Slots 1-6 (stacked bars by element) | adjacent | all hard checks pass; worst CVD ΔE 9.1, worst normal ΔE 19.6 |
| Slots 1-3 (line and scatter plots) | all | all hard checks pass; worst CVD ΔE 9.2, worst normal ΔE 24.0 |

Both runs warn that aqua, yellow and magenta sit below 3:1 contrast on white. So these colours never carry meaning alone: lines also differ by marker and dash, stacked bars carry a legend and a total label, and every value a reader needs is written as text.

Scatter, map and small-multiple figures with more than three colours on screen at once fail the all-pairs check. Use small multiples with one colour per panel instead (as in `surrogate_parity`), or fold the rest into "Other".

## 3. Figure rules

1. **Pick the form from the question.** Proportions near 1 (coverage, agreement) are dot plots against the target, not bars from zero. Additive steps are a waterfall. Profiles over height put storey on the y-axis. Predicted against true is a square panel with a 1:1 line.
2. **One y-scale per panel.** Never a second y-axis. Two quantities with different units get two panels.
3. **Labels say quantity and unit.** "Storey shear [kN]", SI units, sentence case, true minus sign (−), subscripts typeset (CO₂, m²).
4. **No title inside a paper figure.** The caption carries it. Repository figures may carry panel headers, never a sentence-long title.
5. **Every series is named.** A legend whenever there are two or more series; direct labels where they fit. Identity never rests on colour alone.
6. **Selective numbers.** Label totals, end points and the values the text cites, not every mark.
7. **Bars start at zero.** A floating bar (waterfall) shows its own sign and value.
8. **Reference values are drawn and labelled**: the 2 % benchmark band, the H4 88-92 % coverage band (preregistration 2.4), the 1:1 line, the nominal 90 %.
9. **Pre-release and screening-level status is visible** in the footer of every figure that uses pre-release data or elastic, screening-level results.
10. **Draw at final size.** Open the figure with `style.figure("single" | "onehalf" | "double")`. Never resize a finished figure in Word or LaTeX.

## 4. Review checklist

A figure, graphic or output ships only when every line below is ticked. The person who made it does part A and B; part C is the Reviewer 2 pass.

### A. Automated (`style.review`, runs inside every `figures.*` builder)

- [ ] Width is 90, 140 or 190 mm.
- [ ] No text below 7 pt.
- [ ] No text runs off the figure.
- [ ] Every numeric axis has a label.
- [ ] Paper copies carry no title and no footer.

### B. Looked at (open the 600 dpi PNG at 100 % and the PDF)

- [ ] Nothing overlaps: labels, legend, annotations, markers.
- [ ] The eye lands first on the point the caption makes.
- [ ] Colours follow section 2; the same entity has the same colour as in every other figure.
- [ ] Would still read in greyscale (markers, dashes, labels carry identity).
- [ ] Units, sentence case, minus signs and subscripts are right.
- [ ] Legend order matches the visual order of the marks.
- [ ] Footer present on repository figures, with the correct data file.
- [ ] Alignment: panels share axes where they compare the same quantity; ticks are round numbers.
- [ ] No leftover default matplotlib look (box frame, 10 pt labels, tab10 colours).

### C. Reviewer 2 (integrity)

- [ ] Every plotted and written number is in the named results file, or is computed from it by the formula stated in the builder's docstring.
- [ ] Nothing was filtered, re-ordered or rescaled to make a hypothesis look better. Failures and outliers are shown.
- [ ] Wording is "estimate", "screening-level", "under the stated assumptions" where true; no claim of seismic safety.
- [ ] The caption (in the paper or the README) says what is plotted, the sample size and the data status.
- [ ] Nothing from the author's former employer appears.

## 5. Other outputs

**Command-line output.** Plain text that pastes cleanly into a log. Columns aligned, units in the header (`carbon [kgCO2e/m2]`), the same rounding as the CSV, one summary line at the end with counts of passes and failures, and a non-zero exit code on failure. No colour codes in output that may be redirected to a file.

**README and docs.** One H1, sentence-case headings, short paragraphs, tables for anything with three or more comparable items, figures embedded as PNG with a one-line caption below, links that work, no badges that do not tell the reader something true.

**Paper graphics.** Built with `python -m shellbench.figures --paper` into `figures/paper/`, sent as PDF. Fonts embedded. Figure numbers in file names follow Elsevier's naming (`FIG1.pdf`). The caption is written in the manuscript, never in the artwork.

**Social cards and slides.** 1080 × 1350 px (4:5) cards, rendered from HTML at 2× so text stays sharp on phones. Inter for text, JetBrains Mono for code and terminal output, the same colour roles as the figures, one idea per card, a source line and the ownership line at the foot. Terminal cards show real output, shortened only where marked. Template and renderer: project files, `brand/`.

## 6. Making a figure

```python
from shellbench import figures, style

# Rebuild every figure from results/ (repository versions, with footer):
figures.build_all()
# Paper copies, no footer, into figures/paper/:
figures.build_all(paper=True)

# A new figure: draw at final size, label, then finish through the review.
fig, ax = style.figure("single", height_mm=64)
ax.plot(x, y, color=style.SERIES[0], marker=style.MARKERS[0])
ax.set_xlabel("Storeys [–]")
ax.set_ylabel("Saving [%]")
style.footer(fig, "results/my_file.csv")
assert style.review(fig) == []
style.save(fig, "figures/my_figure.png")  # writes .png, .pdf and .svg
```

New figures belong in `src/shellbench/figures.py` with a builder that takes plain rows, so they can be redrawn from `results/` and tested in `tests/test_style.py`.

## 7. Change log

- 9 Nov 2026: adopted. All seven repository figures redrawn in the house style (no number changed); coverage changed from bars to a dot plot with the H4 band; parity changed to one panel per model and split; `results/surrogate_predictions.csv` added (by `scripts/surrogate_figures.py`, which calls the frozen surrogate code without changing it) so the parity figure can be redrawn without re-training.
