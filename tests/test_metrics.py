# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MbitAI — see NOTICE for attribution.
import pytest

from harness.metrics import (
    align_rows,
    fga,
    fta,
    grouping_accuracy,
    parsing_accuracy,
    score_all,
)


def test_perfect_match():
    gt_ids = ["A", "A", "B", "B"]
    parsed_ids = ["x", "x", "y", "y"]
    gt_t = ["foo <*>", "foo <*>", "bar", "bar"]
    parsed_t = ["foo <*>", "foo <*>", "bar", "bar"]
    s = score_all(gt_ids, parsed_ids, gt_t, parsed_t)
    assert s["GA"] == 1.0
    assert s["PA"] == 1.0
    assert s["FGA"] == 1.0
    assert s["FTA"] == 1.0


def test_ga_penalizes_split_group():
    gt_ids = ["A", "A", "A"]
    parsed_ids = ["x", "x", "y"]
    assert grouping_accuracy(gt_ids, parsed_ids) == 0.0


def test_pa_token_mismatch():
    assert parsing_accuracy(["a <*> b"], ["a b"]) == 0.0
    assert parsing_accuracy(["a   <*>"], ["a <*>"]) == 1.0


def test_fga_template_level_not_message_level():
    # 3 messages of template A (split) + 1 of B (ok) => GA=0.25, two GT templates
    # N_c=1 (B only), N_g=2, N_p=3 => PGA=1/3, RGA=1/2, FGA=0.4
    gt_ids = ["A", "A", "A", "B"]
    parsed_ids = ["x", "x", "y", "z"]
    ga = grouping_accuracy(gt_ids, parsed_ids)
    assert ga == 0.25
    assert abs(fga(gt_ids, parsed_ids) - 0.4) < 1e-9


def test_fta_requires_token_match():
    gt_ids = ["A", "A"]
    parsed_ids = ["x", "x"]
    gt_t = ["const <*>", "const <*>"]
    parsed_wrong = ["const", "const"]
    parsed_ok = ["const <*>", "const <*>"]
    assert fta(gt_ids, parsed_ids, gt_t, parsed_wrong) == 0.0
    assert fta(gt_ids, parsed_ids, gt_t, parsed_ok) == 1.0


def test_fta_does_not_require_an_exact_group_match():
    gt_ids = ["A", "A"]
    parsed_ids = ["x", "y"]
    templates = ["const <*>", "const <*>"]
    assert fta(gt_ids, parsed_ids, templates, templates) == 1.0


def test_align_rows_uses_line_id_order():
    truth = [{"LineId": "1"}, {"LineId": "2"}]
    parsed = [{"LineId": "2"}, {"LineId": "1"}]
    _, aligned = align_rows(truth, parsed)
    assert [row["LineId"] for row in aligned] == ["1", "2"]


def test_align_rows_rejects_missing_output():
    truth = [{"LineId": "1"}, {"LineId": "2"}]
    parsed = [{"LineId": "1"}]
    with pytest.raises(ValueError, match=r"missing=\['2'\]"):
        align_rows(truth, parsed)


def test_align_rows_rejects_duplicate_ids():
    truth = [{"LineId": "1"}]
    parsed = [{"LineId": "1"}, {"LineId": "1"}]
    with pytest.raises(ValueError, match="duplicate LineId"):
        align_rows(truth, parsed)
