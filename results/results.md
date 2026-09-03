# Drain reproduction (LogHub-2k)

Scorer: `harness.metrics` (Apache-2.0 implementation of Jiang et al.,
ISSTA'24 GA / PA / FGA / FTA). Drain settings from `configs/drain.yaml`
(logpai/logparser Drain benchmark). Data: Loghub-2.0 `2k_dataset/`,
commit pinned in `configs/datasets.yaml`.

| Dataset | Parser | GA | PA | FGA | FTA |
|---|---|---|---|---|---|
| Apache_2k | drain | 1.0 | 0.6935 | 1.0 | 0.5 |
| Linux_2k | drain | 0.69 | 0.1835 | 0.930435 | 0.434783 |
| OpenSSH_2k | drain | 0.789 | 0.508 | 0.88 | 0.44 |

Apache_2k is the CI golden (`expected/drain_apache_2k.json`). GA on Apache
and Linux matches the logpai Drain toolkit grouping accuracy (1.0 and 0.69).
Wall time is machine-dependent and omitted here.
