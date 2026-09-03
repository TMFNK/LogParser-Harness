# LogParser-Harness

A reproducible harness that runs two log parsers on LogHub-2.0 2k datasets
and scores them with the same shared eval code: **Drain** (the classic
baseline) and **EFParser** (a 2026 small-model LLM parser). Output is one
honest table per dataset: GA / PA / FGA / FTA plus wall time.

Why this exists: most parser papers report message-level accuracy, which
hides failures on rare templates. This harness reports all four LogHub-2.0
metrics, including the template-level FGA and FTA that treat rare and common
templates equally, with fixed settings anyone can re-run.

Keywords: log parsing, log parser benchmark, eval harness, reproducible
evaluation, Drain, EFParser, LogHub-2.0, small language models, offline
on-prem parsing, open-weights models.

Suggested GitHub topics: `log-parsing` `llm-evaluation` `harness`
`anomaly-detection` `small-language-models` `reproducibility`

## Stack

- Python >= 3.12, `uv` (or Poetry)
- Parsers: Drain (`logpai/logparser`), EFParser (`LogAnalysisTech/EFParser-Log-Parser`)
- Eval: `logpai/Loghub-2.0` `benchmark/evaluation/` (pinned commit, see below)
- Model backend: llama.cpp `llama-server` only (no Ollama, no cloud APIs),
  with Qwen3.8-2B-Q6_K (`empero-ai/Qwen3.8-2B-Distill-GGUF`, local, 1.5 GB)
- Data: LogHub-2.0 2k datasets only (runs on an 8 GB Mac)

## One-command run

```bash
./reproduce.sh
```

This runs Drain on Apache_2k, starts `llama-server`, runs EFParser on
Apache_2k, scores both, and writes `results/results.md`.

## Manual steps

```bash
# 1. env
uv sync

# 2. fetch eval code (pin the commit you used, record it here)
git clone --depth 1 https://github.com/logpai/Loghub-2.0 /tmp/loghub2
cp -r /tmp/loghub2/benchmark/evaluation/* ./evaluation/

# 2b. fetch EFParser yourself (upstream has no license file, so this
# repo never vendors it — clone into the git-ignored third_party/)
git clone https://github.com/LogAnalysisTech/EFParser-Log-Parser \
  third_party/EFParser-Log-Parser

# 3. put 2k logs in dataset/  (Apache, Linux, OpenSSH first)
#    source: Loghub-2.0 2k_dataset/ + EFParser-Log-Parser-main/dataset/

# 4. model server (llama.cpp, 127.0.0.1 only — never localhost)
./scripts/start_parser_server.sh start
curl 127.0.0.1:8090/v1/models

# 5. run + score (uv run uses the synced .venv)
uv run python scripts/run_drain.py --dataset Apache
uv run python scripts/run_efparser.py --dataset Apache
uv run python scripts/make_table.py   # -> results/results.md

# 6. stop server
./scripts/start_parser_server.sh stop
```

Eval commit pinned: _fill in after first run, e.g. `logpai/Loghub-2.0@<sha>`_

## Results

See `results/results.md` (per dataset GA / PA / FGA / FTA + wall time).

## License

Apache-2.0, copyright 2026 MbitAI. See LICENSE and
NOTICE — redistribution must preserve the Mbitai attribution.

Need help applying this to your own log pipelines or data-quality work?
Contact https://www.mbitai.com.

## Must-cite (LogHub-2.0 terms)

The LogHub-2.0 datasets are for research/academic use and require
citing both papers in any publication of results:

- Zhihan Jiang et al., "A Large-scale Evaluation for Log Parsing
  Techniques: How Far are We?" ISSTA, 2024.
  https://arxiv.org/abs/2308.10828
- Jieming Zhu et al., "LogHub: A Large Collection of System Log
  Datasets for AI-driven Log Analytics." ISSRE, 2023.
  https://arxiv.org/abs/2008.06448

## Limitations

- 2k scale only; full LogHub-2.0 needs 16 GB RAM / 100 GB disk.
- Linux/OpenSSH Drain formats still need copying from
  `run_statistic_2k.sh` (marked in `configs/drain.ini`).
- `run_efparser.py` needs wiring to the EFParser entry point on first run.
- Ground-truth labels are disputed (SLGParser report, corrected Zenodo
  re-release); this harness reports scores, it does not fix labels.
