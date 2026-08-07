from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_qa_review_cycles_rejects_invalid_loops() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "qa_review_cycles.py"

    completed = subprocess.run(
        [sys.executable, str(script), "--loops", "0"],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )

    combined = (completed.stdout + "\n" + completed.stderr).lower()
    assert completed.returncode != 0
    assert "loops deve ser >= 1" in combined


def test_qa_review_cycles_rejects_negative_timeout() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "qa_review_cycles.py"

    completed = subprocess.run(
        [sys.executable, str(script), "--loops", "1", "--max-step-seconds", "-1"],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )

    combined = (completed.stdout + "\n" + completed.stderr).lower()
    assert completed.returncode != 0
    assert "max_step_seconds nao pode ser negativo" in combined
