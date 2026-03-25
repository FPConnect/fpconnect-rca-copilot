from __future__ import annotations

from pathlib import Path

from agent_core import background


def test_hidden_qa_loop_is_disabled_during_pytest(monkeypatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests::case")
    assert background.ensure_hidden_qa_loop() is None


def test_hidden_qa_loop_is_opt_in_outside_pytest(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("AGENTE_AUTONOMO_BACKGROUND_QA", raising=False)
    assert background.ensure_hidden_qa_loop() is None


def test_hidden_qa_loop_disabled_path_stops_existing_process(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("AGENTE_AUTONOMO_BACKGROUND_QA", raising=False)

    called: list[str] = []

    monkeypatch.setattr(background, "_read_existing_pid", lambda: 321)
    monkeypatch.setattr(background, "_stop_process", lambda pid: called.append(str(pid)) or True)
    monkeypatch.setattr(background, "_clear_pid_file", lambda: called.append("cleared"))

    assert background.ensure_hidden_qa_loop() is None
    assert called == ["321", "cleared"]


def test_hidden_qa_loop_starts_silently_and_records_pid(tmp_path: Path, monkeypatch) -> None:
    pid_file = tmp_path / "qa_background.pid"
    reports_dir = tmp_path / "qa_loop_reports"
    script_path = tmp_path / "scripts" / "qa_hourly_loop.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("print('ok')\n", encoding="utf-8")

    class DummyProcess:
        pid = 43210

    captured: dict = {}

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("AGENTE_AUTONOMO_BACKGROUND_QA", "1")
    monkeypatch.setattr(background, "__file__", str(tmp_path / "agent_core" / "background.py"))
    monkeypatch.setattr(background, "_reports_dir", lambda: reports_dir)
    monkeypatch.setattr(background, "_pid_path", lambda: pid_file)
    monkeypatch.setattr(background, "_read_existing_pid", lambda: None)

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return DummyProcess()

    monkeypatch.setattr(background.subprocess, "Popen", fake_popen)

    started_pid = background.ensure_hidden_qa_loop()

    assert started_pid == 43210
    assert pid_file.read_text(encoding="utf-8") == "43210"
    assert str(script_path) in captured["command"]
    assert str(reports_dir) in captured["command"]
    count_index = captured["command"].index("--count")
    assert captured["command"][count_index + 1] == str(background.DEFAULT_QA_COUNT)
    assert captured["kwargs"]["stdout"] is background.subprocess.DEVNULL
    assert captured["kwargs"]["stderr"] is background.subprocess.DEVNULL