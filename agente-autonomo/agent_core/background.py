from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


DEFAULT_QA_COUNT = 40
DEFAULT_QA_INTERVAL = 3600
DEFAULT_LEARNING_INTERVAL_SECONDS = 1.0


def _reports_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "scripts" / "qa_loop_reports"


def _pid_path() -> Path:
    return _reports_dir() / "qa_background.pid"


def _learning_pid_path() -> Path:
    return _reports_dir() / "learning_background.pid"


def _is_truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _read_existing_pid() -> int | None:
    pid_file = _pid_path()
    if not pid_file.exists():
        return None
    try:
        raw = pid_file.read_text(encoding="utf-8").strip()
        pid = int(raw)
    except Exception:
        return None
    return pid if _is_process_alive(pid) else None


def _clear_pid_file() -> None:
    try:
        _pid_path().unlink(missing_ok=True)
    except Exception:
        pass


def _stop_process(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        if os.name == "nt":
            completed = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return completed.returncode == 0

        os.kill(pid, 15)
        return True
    except Exception:
        return False


def stop_hidden_qa_loop() -> bool:
    existing_pid = _read_existing_pid()
    if not existing_pid:
        _clear_pid_file()
        return False

    stopped = _stop_process(existing_pid)
    _clear_pid_file()
    return stopped


def _read_existing_learning_pid() -> int | None:
    pid_file = _learning_pid_path()
    if not pid_file.exists():
        return None
    try:
        raw = pid_file.read_text(encoding="utf-8").strip()
        pid = int(raw)
    except Exception:
        return None
    return pid if _is_process_alive(pid) else None


def _clear_learning_pid_file() -> None:
    try:
        _learning_pid_path().unlink(missing_ok=True)
    except Exception:
        pass


def stop_hidden_learning_loop() -> bool:
    existing_pid = _read_existing_learning_pid()
    if not existing_pid:
        _clear_learning_pid_file()
        return False

    stopped = _stop_process(existing_pid)
    _clear_learning_pid_file()
    return stopped


def _build_hidden_popen_kwargs() -> dict:
    kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
        )
    return kwargs


def ensure_hidden_qa_loop() -> int | None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return None

    if not _is_truthy(os.getenv("AGENTE_AUTONOMO_BACKGROUND_QA", "0"), default=False):
        stop_hidden_qa_loop()
        return None

    existing_pid = _read_existing_pid()
    if existing_pid:
        return existing_pid

    script_path = Path(__file__).resolve().parent.parent / "scripts" / "qa_hourly_loop.py"
    if not script_path.exists():
        return None

    reports_dir = _reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)

    count = os.getenv("AGENTE_AUTONOMO_BACKGROUND_QA_COUNT", str(DEFAULT_QA_COUNT))
    interval = os.getenv("AGENTE_AUTONOMO_BACKGROUND_QA_INTERVAL", str(DEFAULT_QA_INTERVAL))

    command = [
        sys.executable,
        str(script_path),
        "--count",
        str(count),
        "--interval",
        str(interval),
        "--reports-dir",
        str(reports_dir),
    ]

    try:
        process = subprocess.Popen(command, **_build_hidden_popen_kwargs())
    except Exception:
        return None

    _pid_path().write_text(str(process.pid), encoding="utf-8")
    return process.pid


def ensure_hidden_learning_loop() -> int | None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return None

    if not _is_truthy(os.getenv("AGENTE_AUTONOMO_CONTINUOUS_LEARNING", "1"), default=True):
        stop_hidden_learning_loop()
        return None

    existing_pid = _read_existing_learning_pid()
    if existing_pid:
        return existing_pid

    script_path = Path(__file__).resolve().parent.parent / "scripts" / "continuous_learning_loop.py"
    if not script_path.exists():
        return None

    reports_dir = _reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)

    interval = os.getenv(
        "AGENTE_AUTONOMO_LEARNING_INTERVAL_SECONDS",
        str(DEFAULT_LEARNING_INTERVAL_SECONDS),
    )

    command = [
        sys.executable,
        str(script_path),
        "--interval-seconds",
        str(interval),
        "--reports-dir",
        str(reports_dir),
    ]

    try:
        process = subprocess.Popen(command, **_build_hidden_popen_kwargs())
    except Exception:
        return None

    _learning_pid_path().write_text(str(process.pid), encoding="utf-8")
    return process.pid