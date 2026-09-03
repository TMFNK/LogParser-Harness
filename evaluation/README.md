# Evaluation code

This repo does **not** vendor `logpai/Loghub-2.0/benchmark/evaluation/`.

Those scripts are part of TA-Eval-Rep and are licensed **GPL-3.0**. Copying
them into an Apache-2.0 tree would contaminate this project's license.

Scoring lives in `harness/metrics.py`: an independent implementation of the
four metrics defined in Jiang et al., ISSTA 2024 (arXiv:2308.10828), section
4.2 (GA, PA, FGA, FTA). Drain hyperparameters come from the Apache-2.0
logpai/logparser Drain benchmark, not from the GPL eval wrappers.
