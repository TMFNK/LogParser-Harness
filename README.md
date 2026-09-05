# LogParser-Harness

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22341500.svg)](https://doi.org/10.5281/zenodo.22341500)

Reproducible **Drain** baseline on LogHub-2k, scored with the four LogHub-2.0
metrics: **GA**, **PA**, **FGA**, **FTA**.

This is an evaluation harness, not a new parser. A stranger should be able to
clone, run one command, and match the committed Apache_2k Drain numbers.
EFParser is still unwired. Trail is an optional sibling plugin, not vendored.

Keywords: log parsing, Drain, LogHub-2k, LogHub-2.0, grouping accuracy, parsing
accuracy, FGA, FTA, reproducible evaluation.

GitHub topics: `log-parsing` `log-parser` `benchmark` `reproducibility` `drain`

## Project pipeline

- **Tier A — this harness:** reproducible Drain evaluation on LogHub-2k.
- **Tier B — [LogParser-Dataset](https://github.com/TMFNK/LogParser-Dataset):**
  the synthetic SecOps-2k dataset, grouping rules, and Drain baseline.
- **Tier C — [LogParser-Trail](https://github.com/TMFNK/LogParser-Trail):**
  the auditable parser, its SecOps-2k results, and local-model assist.

## One-command run

```bash
./reproduce.sh --drain-only
```

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/). Downloads Apache_2k
from a pinned Loghub-2.0 commit, runs Drain with the logpai benchmark settings,
scores, checks `expected/drain_apache_2k.json`, and writes `results/results.md`.

Linux and OpenSSH 2k:

```bash
./reproduce.sh --drain-only Apache Linux OpenSSH
```

Spell baseline (same `logparser3` dependency, tau=0.5, untuned):

```bash
./reproduce.sh --with-spell
```

[Trail](https://github.com/TMFNK/LogParser-Trail) is optional and not
vendored. Point `TRAIL_SRC` at a local checkout, or use the sibling default
`../LogParser-Trail`. `--with-trail` runs Drain and Trail on Apache_2k,
Linux_2k, and OpenSSH_2k. It also runs Trail on
[SecOps-2k](https://github.com/TMFNK/LogParser-Dataset) when that repository is
checked out at `../LogParser-Dataset`; set `DATASET_SRC` for another checkout
location. Drain scores still have to match `expected/drain_*_2k.json`, and
Trail scores have to match `expected/trail_*_2k.json`.

```bash
./reproduce.sh --with-trail
```

## What is pinned

| Item | Where |
|---|---|
| Loghub-2.0 git commit (2k files only) | `configs/datasets.yaml` |
| File sha256 | same file, checked on fetch |
| Drain `log_format`, `depth`, `st`, `regex` | `configs/drain.yaml` (from logpai/logparser Drain benchmark) |
| Spell `log_format`, `tau`, `regex` | `configs/spell.yaml` (same dependency, tau=0.5, untuned) |
| Metric formulas | `harness/metrics.py` (Jiang et al., ISSTA'24 §4.2) |
| Expected Apache scores | `expected/drain_apache_2k.json` |
| Expected Linux/OpenSSH Drain scores | `expected/drain_{linux,openssh}_2k.json` |
| Expected Spell scores | `expected/spell_{apache,linux,openssh}_2k.json` |
| Expected Apache Trail scores | `expected/trail_apache_2k.json` (sibling plugin) |
| Expected Linux/OpenSSH Trail scores | `expected/trail_{linux,openssh}_2k.json` (sibling plugin) |
| Expected SecOps-2k Trail scores | `expected/trail_secops_2k.json` (sibling dataset) |
| Trail revision exercised by CI | `.github/workflows/drain-apache.yml` |
| Python deps | `uv.lock` |
| CI | `.github/workflows/drain-apache.yml` |

Each scored run also writes `results/raw/drain_<dataset>_scores.json` with
dataset hashes, git SHA, and wall time.

## Metrics

Independent Apache-2.0 code. We do not copy Loghub-2.0 `benchmark/evaluation/`
(GPL-3 / TA-Eval-Rep). See `evaluation/README.md`.

- **GA** — share of messages whose parsed group equals the ground-truth group
- **PA** — share of messages whose template tokens match exactly
- **FGA** — F1 of grouping accuracy at template level (rare and common templates equal)
- **FTA** — F1 of exact template identification (one ground-truth template
  per parsed template, with matching tokens)

## Manual steps

```bash
uv sync --frozen --extra dev
uv run python scripts/fetch_assets.py --dataset Apache
uv run python scripts/run_drain.py --dataset Apache
uv run python scripts/score.py --dataset Apache --parser drain
uv run python scripts/verify_golden.py
uv run python scripts/make_table.py
uv run pytest -q
```

## Results

See `results/results.md`. Apache_2k Drain is the CI golden. Linux_2k grouping
accuracy matches the logpai Drain toolkit (GA 0.69). Trail rows cover the
same three files: it matches Drain GA on Linux, trails on OpenSSH
(late-line merges the 2-anchor guard misses — see the golden notes),
and over-fragments Apache (37 parsed vs 6 truth templates).
Spell (untuned tau=0.5) trails both parsers on all three files; on
Apache it merges the jk2_init Found/Can't-find pair Trail's anchors
keep apart.

## License

Apache-2.0, copyright 2026 MbitAI. See LICENSE and NOTICE.

Need this applied to your own log pipelines? https://www.mbitai.com

## Cite this (Zenodo)

If you use this harness, please cite the archived release:

> MbitAI. (2026). *LogParser-Harness* (v0.2.1). Zenodo.
> https://doi.org/10.5281/zenodo.22341500

| | |
| --- | --- |
| This version | [10.5281/zenodo.22341500](https://doi.org/10.5281/zenodo.22341500) |
| All versions (concept DOI) | [10.5281/zenodo.22341499](https://doi.org/10.5281/zenodo.22341499) |
| GitHub tag | [`v0.2.1`](https://github.com/TMFNK/LogParser-Harness/releases/tag/v0.2.1) |
| Record | https://zenodo.org/records/22341500 |

Also see [`CITATION.cff`](CITATION.cff).

```bibtex
@software{mbitai_2026_logparser_harness,
  author       = {MbitAI},
  title        = {LogParser-Harness},
  month        = sep,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v0.2.1},
  doi          = {10.5281/zenodo.22341500},
  url          = {https://doi.org/10.5281/zenodo.22341500},
}
```

## Must-cite (LogHub terms)

The LogHub-2k files are for research use. Cite both papers if you publish
numbers from this harness:

- Zhihan Jiang et al., "A Large-scale Evaluation for Log Parsing Techniques:
  How Far are We?" ISSTA, 2024. https://arxiv.org/abs/2308.10828
- Jieming Zhu et al., "LogHub: A Large Collection of System Log Datasets for
  AI-driven Log Analytics." ISSRE, 2023. https://arxiv.org/abs/2008.06448
- Drain: Pinjia He et al., ICWS 2017. logpai/logparser (Apache-2.0)
- Spell: Min Du and Feifei Li, ICDM 2016. Same logpai/logparser package.

## Limitations

- 2k scale only. Full LogHub-2.0 needs 16 GB RAM and 100 GB disk.
- Ground-truth labels are disputed (SLGParser, Zenodo corrected release). This
  harness reports scores; it does not relabel.
- EFParser is not wired. Upstream has no license file; this repo never vendors it.
