# LogHub-2k reproduction (Drain + Spell + Trail)

Scorer: `harness.metrics` (Apache-2.0 implementation of Jiang et al.,
ISSTA'24 GA / PA / FGA / FTA). Drain settings from `configs/drain.yaml`
(logpai/logparser Drain benchmark). Spell settings from
`configs/spell.yaml` (same logparser3 dependency, tau=0.5, untuned).
Trail settings from the sibling
`LogParser-Trail` checkout (`configs/miner.yaml`, revision pinned in
each `expected/trail_*_2k.json`). Data: Loghub-2.0 `2k_dataset/`,
commit pinned in `configs/datasets.yaml`.

These reference rows come from the committed golden files in
`expected/`; wall time remains machine-dependent and is recorded only in
each local `results/raw/*_scores.json`.

| Dataset | Parser | GA | PA | FGA | FTA |
|---|---|---|---|---|---|
| Apache_2k | drain | 1.0 | 0.6935 | 1.0 | 0.5 |
| Linux_2k | drain | 0.69 | 0.1835 | 0.930435 | 0.434783 |
| OpenSSH_2k | drain | 0.789 | 0.508 | 0.88 | 0.44 |
| Apache_2k | spell | 0.576 | 0.2695 | 0.727273 | 0.181818 |
| Linux_2k | spell | 0.5975 | 0.0875 | 0.735849 | 0.150943 |
| OpenSSH_2k | spell | 0.2515 | 0.121 | 0.487805 | 0.195122 |
| Apache_2k | trail | 0.984 | 0.6935 | 0.232558 | 0.139535 |
| Linux_2k | trail | 0.69 | 0.1705 | 0.918455 | 0.39485 |
| OpenSSH_2k | trail | 0.542 | 0.508 | 0.784314 | 0.431373 |
