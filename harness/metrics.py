# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
"""GA, PA, FGA, FTA from Jiang et al., ISSTA'24 (LogHub-2.0), section 4.2.

Independent implementation of the published formulas. Does not copy
Loghub-2.0 benchmark/evaluation (GPL-3, TA-Eval-Rep).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _group_indices(labels: Sequence[object]) -> dict[object, frozenset[int]]:
    groups: dict[object, list[int]] = defaultdict(list)
    for i, lab in enumerate(labels):
        groups[lab].append(i)
    return {lab: frozenset(idxs) for lab, idxs in groups.items()}


def _normalize_template(template: object) -> tuple[str, ...]:
    text = "" if template is None else str(template)
    return tuple(text.split())


def grouping_accuracy(gt_ids: Sequence[object], parsed_ids: Sequence[object]) -> float:
    """Share of messages whose parsed group equals the ground-truth group.

    A message is correctly grouped iff the set of messages sharing its
    parsed template id is identical to the set sharing its ground-truth id.
    """
    if len(gt_ids) != len(parsed_ids):
        raise ValueError("gt_ids and parsed_ids must have the same length")
    n = len(gt_ids)
    if n == 0:
        return 0.0
    gt_groups = _group_indices(gt_ids)
    parsed_groups = _group_indices(parsed_ids)
    correct = 0
    for i, (g, p) in enumerate(zip(gt_ids, parsed_ids)):
        if gt_groups[g] == parsed_groups[p]:
            correct += 1
    return correct / n


def parsing_accuracy(
    gt_templates: Sequence[object], parsed_templates: Sequence[object]
) -> float:
    """Share of messages whose template tokens match the ground truth exactly."""
    if len(gt_templates) != len(parsed_templates):
        raise ValueError("template sequences must have the same length")
    n = len(gt_templates)
    if n == 0:
        return 0.0
    correct = 0
    for gt, parsed in zip(gt_templates, parsed_templates):
        if _normalize_template(gt) == _normalize_template(parsed):
            correct += 1
    return correct / n


def _correctly_grouped_template_count(
    gt_ids: Sequence[object], parsed_ids: Sequence[object]
) -> int:
    """N_c: ground-truth templates whose message set matches some parsed template."""
    gt_groups = _group_indices(gt_ids)
    parsed_sets = set(_group_indices(parsed_ids).values())
    return sum(1 for s in gt_groups.values() if s in parsed_sets)


def fga(gt_ids: Sequence[object], parsed_ids: Sequence[object]) -> float:
    """F1 of grouping accuracy (template-level).

    PGA = N_c / N_p, RGA = N_c / N_g, FGA = harmonic mean.
    N_c counts ground-truth templates whose message set equals a parsed set.
    """
    if len(gt_ids) != len(parsed_ids):
        raise ValueError("gt_ids and parsed_ids must have the same length")
    n_g = len(_group_indices(gt_ids))
    n_p = len(_group_indices(parsed_ids))
    if n_g == 0 or n_p == 0:
        return 0.0
    n_c = _correctly_grouped_template_count(gt_ids, parsed_ids)
    pga = n_c / n_p
    rga = n_c / n_g
    return _f1(pga, rga)


def _correctly_identified_template_count(
    gt_ids: Sequence[object],
    parsed_ids: Sequence[object],
    gt_templates: Sequence[object],
    parsed_templates: Sequence[object],
) -> int:
    """N̂_c: correctly grouped templates whose tokens also match.

    For each matching message-set pair, compare the (unique) template token
    sequence on the ground-truth side with the parsed side.
    """
    gt_groups = _group_indices(gt_ids)
    parsed_groups = _group_indices(parsed_ids)
    parsed_by_set = {s: True for s in parsed_groups.values()}
    n_hat = 0
    for gt_set in gt_groups.values():
        if gt_set not in parsed_by_set:
            continue
        i = next(iter(gt_set))
        if _normalize_template(gt_templates[i]) == _normalize_template(
            parsed_templates[i]
        ):
            n_hat += 1
    return n_hat


def fta(
    gt_ids: Sequence[object],
    parsed_ids: Sequence[object],
    gt_templates: Sequence[object],
    parsed_templates: Sequence[object],
) -> float:
    """F1 of template accuracy (strictest LogHub-2.0 score).

    A template is correct iff the message set matches and every token matches.
    PTA = N̂_c / N_p, RTA = N̂_c / N_g.
    """
    if not (
        len(gt_ids)
        == len(parsed_ids)
        == len(gt_templates)
        == len(parsed_templates)
    ):
        raise ValueError("all sequences must have the same length")
    n_g = len(_group_indices(gt_ids))
    n_p = len(_group_indices(parsed_ids))
    if n_g == 0 or n_p == 0:
        return 0.0
    n_hat = _correctly_identified_template_count(
        gt_ids, parsed_ids, gt_templates, parsed_templates
    )
    pta = n_hat / n_p
    rta = n_hat / n_g
    return _f1(pta, rta)


def score_all(
    gt_ids: Sequence[object],
    parsed_ids: Sequence[object],
    gt_templates: Sequence[object],
    parsed_templates: Sequence[object],
) -> dict[str, float]:
    return {
        "GA": grouping_accuracy(gt_ids, parsed_ids),
        "PA": parsing_accuracy(gt_templates, parsed_templates),
        "FGA": fga(gt_ids, parsed_ids),
        "FTA": fta(gt_ids, parsed_ids, gt_templates, parsed_templates),
    }


def score_frames(
    gt: Mapping[str, Sequence[object]], parsed: Mapping[str, Sequence[object]]
) -> dict[str, float]:
    """Score aligned EventId / EventTemplate columns (dict or pandas Series)."""
    return score_all(
        list(gt["EventId"]),
        list(parsed["EventId"]),
        list(gt["EventTemplate"]),
        list(parsed["EventTemplate"]),
    )
