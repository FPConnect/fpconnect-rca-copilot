from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import qa_review_cycles


@pytest.mark.parametrize(
    ("loops", "sleep", "max_step", "max_pytest", "expected_message"),
    [
        (0, 0.0, 0.0, 0.0, "loops deve ser >= 1"),
        (1, -0.1, 0.0, 0.0, "sleep nao pode ser negativo"),
        (1, 0.0, -1.0, 0.0, "max_step_seconds nao pode ser negativo"),
        (1, 0.0, 0.0, -1.0, "max_pytest_seconds nao pode ser negativo"),
    ],
)
def test_validate_inputs_rejects_invalid_values(
    loops: int,
    sleep: float,
    max_step: float,
    max_pytest: float,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        qa_review_cycles._validate_inputs(loops, sleep, max_step, max_pytest)


def test_write_summary_json_writes_step_stats(tmp_path: Path) -> None:
    output_file = tmp_path / "summary.json"
    qa_review_cycles._write_summary_json(
        output_file,
        status="passed",
        loops=3,
        ok_cycles=3,
        include_network=False,
        step_durations={"pytest": [5.0, 7.0, 6.0]},
        started_at="2026-03-13T19:00:00",
        finished_at="2026-03-13T19:00:20",
    )

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["loops"] == 3
    assert payload["ok_cycles"] == 3
    assert payload["step_stats"]["pytest"] == {
        "count": 3.0,
        "avg_seconds": 6.0,
        "min_seconds": 5.0,
        "max_seconds": 7.0,
    }
