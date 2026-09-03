# LogParser-Harness

Reproducible **Drain** baseline on LogHub-2k, scored with the four LogHub-2.0
metrics: **GA**, **PA**, **FGA**, **FTA**.

This is an evaluation harness, not a new parser. A stranger should be able to
clone, run one command, and match the committed Apache_2k numbers. EFParser and
any original parser are out of scope for this release.

Keywords: log parsing, Drain, LogHub-2k, LogHub-2.0, grouping accuracy, parsing
accuracy, FGA, FTA, reproducible evaluation.

GitHub topics: `log-parsing` `log-parser` `benchmark` `reproducibility` `drain`

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

## What is pinned

| Item | Where |
|---|---|
| Loghub-2.0 git commit (2k files only) | `configs/datasets.yaml` |
| File sha256 | same file, checked on fetch |
| Drain `log_format`, `depth`, `st`, `regex` | `configs/drain.yaml` (from logpai/logparser Drain benchmark) |
| Metric formulas | `harness/metrics.py` (Jiang et al., ISSTA'24 §4.2) |
| Expected Apache scores | `expected/drain_apache_2k.json` |
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
- **FTA** — F1 of template accuracy (group set and tokens both match)

## Manual steps

```bash
uv sync --extra dev
uv run python scripts/fetch_assets.py --dataset Apache
uv run python scripts/run_drain.py --dataset Apache
uv run python scripts/score.py --dataset Apache --parser drain
uv run python scripts/verify_golden.py
uv run python scripts/make_table.py
uv run pytest -q
```

## Results

See `results/results.md`. Apache_2k Drain is the CI golden. Linux_2k grouping
accuracy matches the logpai Drain toolkit (GA 0.69).

## License

Apache-2.0, copyright 2026 MbitAI. See LICENSE and NOTICE.

Need this applied to your own log pipelines? https://www.mbitai.com

## Must-cite (LogHub terms)

The LogHub-2k files are for research use. Cite both papers if you publish
numbers from this harness:

- Zhihan Jiang et al., "A Large-scale Evaluation for Log Parsing Techniques:
  How Far are We?" ISSTA, 2024. https://arxiv.org/abs/2308.10828
- Jieming Zhu et al., "LogHub: A Large Collection of System Log Datasets for
  AI-driven Log Analytics." ISSRE, 2023. https://arxiv.org/abs/2008.06448
- Drain: Pinjia He et al., ICWS 2017. logpai/logparser (Apache-2.0)

## Limitations

- 2k scale only. Full LogHub-2.0 needs 16 GB RAM and 100 GB disk.
- Ground-truth labels are disputed (SLGParser, Zenodo corrected release). This
  harness reports scores; it does not relabel.
- EFParser is not wired. Upstream has no license file; this repo never vendors it.
