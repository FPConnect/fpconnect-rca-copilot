"""Metrics and monitoring service for system health tracking."""

from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import psutil
import structlog

from app.core.cache import get_cached, set_cached

log = structlog.get_logger()


class MetricsCollector:
    """Collect and store application metrics."""

    def __init__(self):
        self._metrics: dict[str, list[dict]] = defaultdict(list)
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._start_time = datetime.now(timezone.utc)

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        self._counters[name] += value

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        self._gauges[name] = value

    def record_histogram(
        self, name: str, value: float, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record a histogram data point."""
        entry = {
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "labels": labels or {},
        }
        # Keep only last 1000 data points per metric
        self._metrics[name].append(entry)
        if len(self._metrics[name]) > 1000:
            self._metrics[name] = self._metrics[name][-1000:]

    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> Optional[float]:
        """Get current gauge value."""
        return self._gauges.get(name)

    def get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        return (datetime.now(timezone.utc) - self._start_time).total_seconds()

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "uptime_seconds": self.get_uptime_seconds(),
            "start_time": self._start_time.isoformat(),
        }


# Global metrics collector instance
metrics = MetricsCollector()


def get_system_health() -> dict[str, Any]:
    """Get comprehensive system health metrics."""
    cache_key = "system:health"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        process = psutil.Process(os.getpid())

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        system_memory = psutil.virtual_memory()

        # Disk metrics
        disk_usage = psutil.disk_usage("/")

        # Network metrics
        net_io = psutil.net_io_counters()

        result = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "per_cpu": psutil.cpu_percent(interval=0.1, percpu=True),
            },
            "memory": {
                "process_used_mb": round(memory_info.rss / 1024 / 1024, 2),
                "process_percent": round(memory_percent, 2),
                "system_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "system_used_percent": system_memory.percent,
                "system_available_gb": round(system_memory.available / 1024 / 1024 / 1024, 2),
            },
            "disk": {
                "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk_usage.used / 1024 / 1024 / 1024, 2),
                "percent": disk_usage.percent,
                "free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            },
            "application": {
                "uptime_seconds": metrics.get_uptime_seconds(),
                "active_threads": asyncio.active_tasks().__len__() if hasattr(asyncio, 'active_tasks') else 0,
            },
        }

        # Determine overall health status
        if cpu_percent > 90 or memory_percent > 90 or disk_usage.percent > 90:
            result["status"] = "critical"
        elif cpu_percent > 75 or memory_percent > 75 or disk_usage.percent > 75:
            result["status"] = "warning"

        set_cached(cache_key, result, ttl=30)
        return result

    except Exception as e:
        log.error("health_check_failed", error=str(e))
        return {
            "status": "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }


def get_api_metrics() -> dict[str, Any]:
    """Get API-specific metrics."""
    return {
        "requests_total": metrics.get_counter("http_requests_total"),
        "requests_by_status": {
            "2xx": metrics.get_counter("http_requests_2xx"),
            "4xx": metrics.get_counter("http_requests_4xx"),
            "5xx": metrics.get_counter("http_requests_5xx"),
        },
        "average_response_time_ms": metrics.get_gauge("http_response_time_avg_ms"),
        "slow_requests": metrics.get_counter("http_requests_slow"),
    }


async def collect_periodic_metrics():
    """Background task to collect periodic metrics."""
    while True:
        try:
            # Collect system metrics
            health = get_system_health()
            metrics.set_gauge("system_cpu_percent", health["cpu"]["percent"])
            metrics.set_gauge("system_memory_percent", health["memory"]["process_percent"])
            metrics.set_gauge("system_disk_percent", health["disk"]["percent"])

            # Log warnings for high resource usage
            if health["cpu"]["percent"] > 80:
                log.warning("high_cpu_usage", percent=health["cpu"]["percent"])
            if health["memory"]["process_percent"] > 80:
                log.warning("high_memory_usage", percent=health["memory"]["process_percent"])

        except Exception as e:
            log.error("metric_collection_error", error=str(e))

        await asyncio.sleep(60)  # Collect every minute


def track_request(status_code: int, duration_ms: float) -> None:
    """Track HTTP request metrics."""
    metrics.increment_counter("http_requests_total")

    # Track by status code category
    if 200 <= status_code < 300:
        metrics.increment_counter("http_requests_2xx")
    elif 400 <= status_code < 500:
        metrics.increment_counter("http_requests_4xx")
    elif status_code >= 500:
        metrics.increment_counter("http_requests_5xx")

    # Track response time
    metrics.record_histogram("http_response_time_ms", duration_ms)

    # Update average response time (simple moving average)
    current_avg = metrics.get_gauge("http_response_time_avg_ms") or 0
    total_requests = metrics.get_counter("http_requests_total")
    new_avg = ((current_avg * (total_requests - 1)) + duration_ms) / total_requests
    metrics.set_gauge("http_response_time_avg_ms", round(new_avg, 2))

    # Track slow requests
    if duration_ms > 1000:
        metrics.increment_counter("http_requests_slow")
