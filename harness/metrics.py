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
    gt_templates: Sequence[object], parsed_templates: Sequence[object]
) -> int:
    """N̂_c: parsed templates that map only to the same ground-truth template."""
    groundtruth_by_parsed: dict[tuple[str, ...], set[tuple[str, ...]]] = defaultdict(
        set
    )
    for gt, parsed in zip(gt_templates, parsed_templates):
        groundtruth_by_parsed[_normalize_template(parsed)].add(
            _normalize_template(gt)
        )
    return sum(
        groundtruth == {parsed}
        for parsed, groundtruth in groundtruth_by_parsed.items()
    )


def fta(
    gt_ids: Sequence[object],
    parsed_ids: Sequence[object],
    gt_templates: Sequence[object],
    parsed_templates: Sequence[object],
) -> float:
    """F1 of template accuracy (strictest LogHub-2.0 score).

    A parsed template is correct iff all of its messages share one ground-truth
    template and its tokens match that template.
    PTA = N̂_c / N_p, RTA = N̂_c / N_g.
    """
    if not (
        len(gt_ids)
        == len(parsed_ids)
        == len(gt_templates)
        == len(parsed_templates)
    ):
        raise ValueError("all sequences must have the same length")
    n_g = len({_normalize_template(template) for template in gt_templates})
    n_p = len({_normalize_template(template) for template in parsed_templates})
    if n_g == 0 or n_p == 0:
        return 0.0
    n_hat = _correctly_identified_template_count(gt_templates, parsed_templates)
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


def align_rows(
    gt_rows: Sequence[Mapping[str, object]],
    parsed_rows: Sequence[Mapping[str, object]],
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    """Align structured rows by LineId and reject incomplete parser output."""

    def index(
        rows: Sequence[Mapping[str, object]], label: str
    ) -> dict[object, Mapping[str, object]]:
        indexed: dict[object, Mapping[str, object]] = {}
        for row in rows:
            if "LineId" not in row:
                raise ValueError(f"{label} row is missing LineId")
            line_id = row["LineId"]
            if line_id in indexed:
                raise ValueError(f"{label} has duplicate LineId {line_id!r}")
            indexed[line_id] = row
        return indexed

    gt_by_id = index(gt_rows, "ground truth")
    parsed_by_id = index(parsed_rows, "parsed output")
    if gt_by_id.keys() != parsed_by_id.keys():
        missing = sorted(gt_by_id.keys() - parsed_by_id.keys(), key=str)
        extra = sorted(parsed_by_id.keys() - gt_by_id.keys(), key=str)
        raise ValueError(f"LineId mismatch: missing={missing}, extra={extra}")
    return list(gt_rows), [parsed_by_id[row["LineId"]] for row in gt_rows]


def score_rows(
    gt_rows: Sequence[Mapping[str, object]],
    parsed_rows: Sequence[Mapping[str, object]],
) -> dict[str, float]:
    """Score complete structured rows after aligning them by LineId."""
    gt, parsed = align_rows(gt_rows, parsed_rows)
    return score_all(
        [row["EventId"] for row in gt],
        [row["EventId"] for row in parsed],
        [row["EventTemplate"] for row in gt],
        [row["EventTemplate"] for row in parsed],
    )
