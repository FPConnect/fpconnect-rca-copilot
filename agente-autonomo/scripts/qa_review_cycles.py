from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from statistics import mean


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} nao pode ser negativo: {value}")


def _validate_inputs(loops: int, sleep: float, max_step_seconds: float, max_pytest_seconds: float) -> None:
    if loops < 1:
        raise ValueError(f"loops deve ser >= 1: {loops}")
    _validate_non_negative("sleep", sleep)
    _validate_non_negative("max_step_seconds", max_step_seconds)
    _validate_non_negative("max_pytest_seconds", max_pytest_seconds)


def _run_step(command: list[str], cwd: Path) -> tuple[bool, float, str]:
    start = time.perf_counter()
    process = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    elapsed = time.perf_counter() - start
    output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
    return process.returncode == 0, elapsed, output.strip()


def _command_label(command: list[str]) -> str:
    if len(command) >= 3 and command[1] == "-m" and command[2] == "pytest":
        return "pytest"
    if len(command) >= 2:
        return " ".join(command[1:])
    return " ".join(command)


def _write_summary_json(
    summary_path: Path,
    *,
    status: str,
    loops: int,
    ok_cycles: int,
    include_network: bool,
    step_durations: dict[str, list[float]],
    started_at: str,
    finished_at: str,
    failure_reason: str | None = None,
) -> None:
    step_stats: dict[str, dict[str, float]] = {}
    for name, samples in step_durations.items():
        if not samples:
            continue
        step_stats[name] = {
            "count": float(len(samples)),
            "avg_seconds": round(mean(samples), 4),
            "min_seconds": round(min(samples), 4),
            "max_seconds": round(max(samples), 4),
        }

    payload = {
        "status": status,
        "loops": loops,
        "ok_cycles": ok_cycles,
        "include_network": include_network,
        "started_at": started_at,
        "finished_at": finished_at,
        "failure_reason": failure_reason,
        "step_stats": step_stats,
    }
    summary_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa revisoes ciclicas de qualidade")
    parser.add_argument("--loops", type=int, default=50, help="Quantidade de ciclos de revisao")
    parser.add_argument("--include-network", action="store_true", help="Inclui smoke de mercado com rede")
    parser.add_argument("--sleep", type=float, default=0.0, help="Pausa em segundos entre ciclos")
    parser.add_argument(
        "--max-step-seconds",
        type=float,
        default=0.0,
        help="Falha se qualquer etapa exceder esse tempo (0 desabilita)",
    )
    parser.add_argument(
        "--max-pytest-seconds",
        type=float,
        default=0.0,
        help="Falha se a etapa de pytest exceder esse tempo (0 desabilita)",
    )
    args = parser.parse_args()

    try:
        _validate_inputs(args.loops, args.sleep, args.max_step_seconds, args.max_pytest_seconds)
    except ValueError as exc:
        parser.error(str(exc))

    root = Path(__file__).resolve().parents[1]
    python = Path(sys.executable)

    log_dir = root / "scripts" / "qa_loop_reports"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"review_cycles_{stamp}.log"
    summary_path = log_dir / f"review_cycles_{stamp}.json"
    started_at = datetime.now().isoformat(timespec="seconds")

    commands: list[list[str]] = [
        [str(python), "-m", "pytest", "-q"],
        [str(python), "scripts/_smoke_check.py", "--fail-fast"],
    ]
    if args.include_network:
        commands.append([str(python), "scripts/_smoke_check.py", "--network", "--fail-fast"])

    ok_cycles = 0
    step_durations: dict[str, list[float]] = {}
    failure_reason: str | None = None
    with log_path.open("w", encoding="utf-8") as fh:
        fh.write(
            "[START] "
            f"loops={args.loops} "
            f"include_network={args.include_network} "
            f"max_step_seconds={args.max_step_seconds} "
            f"max_pytest_seconds={args.max_pytest_seconds}\n"
        )
        for cycle in range(1, args.loops + 1):
            fh.write(f"\n[CYCLE {cycle}]\n")
            cycle_ok = True
            for cmd in commands:
                step_name = _command_label(cmd)
                success, elapsed, output = _run_step(cmd, root)
                step_durations.setdefault(step_name, []).append(elapsed)
                fh.write(f"CMD: {' '.join(cmd)}\n")
                fh.write(f"OK={success} ELAPSED={elapsed:.2f}s\n")
                if output:
                    fh.write(output + "\n")

                if args.max_step_seconds > 0 and elapsed > args.max_step_seconds:
                    success = False
                    limit_msg = (
                        f"Limite geral excedido em {step_name}: "
                        f"{elapsed:.2f}s > {args.max_step_seconds:.2f}s"
                    )
                    fh.write(limit_msg + "\n")
                    failure_reason = limit_msg

                if (
                    success
                    and step_name == "pytest"
                    and args.max_pytest_seconds > 0
                    and elapsed > args.max_pytest_seconds
                ):
                    success = False
                    limit_msg = (
                        f"Limite de pytest excedido: "
                        f"{elapsed:.2f}s > {args.max_pytest_seconds:.2f}s"
                    )
                    fh.write(limit_msg + "\n")
                    failure_reason = limit_msg

                if not success:
                    cycle_ok = False
                    if failure_reason is None:
                        failure_reason = f"Falha em {step_name} no ciclo {cycle}"
                    break

            if cycle_ok:
                ok_cycles += 1
                fh.write(f"[CYCLE {cycle}] PASS\n")
            else:
                fh.write(f"[CYCLE {cycle}] FAIL\n")
                finished_at = datetime.now().isoformat(timespec="seconds")
                _write_summary_json(
                    summary_path,
                    status="failed",
                    loops=args.loops,
                    ok_cycles=ok_cycles,
                    include_network=args.include_network,
                    step_durations=step_durations,
                    started_at=started_at,
                    finished_at=finished_at,
                    failure_reason=failure_reason,
                )
                print(
                    f"Falha no ciclo {cycle}. "
                    f"Log: {log_path} | Resumo: {summary_path}"
                )
                return 1
            if args.sleep > 0 and cycle < args.loops:
                time.sleep(args.sleep)

        fh.write(f"\n[DONE] ok_cycles={ok_cycles} total={args.loops}\n")

    finished_at = datetime.now().isoformat(timespec="seconds")
    _write_summary_json(
        summary_path,
        status="passed",
        loops=args.loops,
        ok_cycles=ok_cycles,
        include_network=args.include_network,
        step_durations=step_durations,
        started_at=started_at,
        finished_at=finished_at,
    )

    print(
        f"Revisao ciclica concluida: {ok_cycles}/{args.loops} ciclos aprovados. "
        f"Log: {log_path} | Resumo: {summary_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
