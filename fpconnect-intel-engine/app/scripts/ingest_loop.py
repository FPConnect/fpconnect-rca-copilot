import time
from app.scripts.ingest_once import run_once
from app.core.config import settings


def main():
    interval = int(settings.poll_interval_seconds)
    print(f"[ingest_loop] Starting. Interval={interval}s")
    while True:
        try:
            stats = run_once()
            print(f"[ingest_loop] run_once: {stats}")
        except Exception as e:
            print(f"[ingest_loop] error: {e}")
        time.sleep(interval)


if __name__ == '__main__':
    main()
