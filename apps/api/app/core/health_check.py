"""Health check service for comprehensive system monitoring."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Optional
import structlog

from app.core.cache import get_cached, set_cached
from app.services.metrics import get_system_health

log = structlog.get_logger()


class HealthCheckResult:
    """Result of a health check."""

    def __init__(
        self,
        name: str,
        status: str = "healthy",
        message: Optional[str] = None,
        latency_ms: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.name = name
        self.status = status  # healthy, degraded, unhealthy
        self.message = message
        self.latency_ms = latency_ms
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms else None,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class DependencyHealthCheck:
    """Base class for dependency health checks."""

    def __init__(self, name: str, timeout_seconds: float = 5.0):
        self.name = name
        self.timeout_seconds = timeout_seconds
        self._last_check: Optional[HealthCheckResult] = None
        self._consecutive_failures = 0
        self._total_checks = 0
        self._total_failures = 0

    async def check(self) -> HealthCheckResult:
        """Perform health check (to be implemented by subclasses)."""
        raise NotImplementedError

    def _create_result(
        self,
        status: str,
        message: str,
        latency_ms: float,
        details: Optional[dict[str, Any]] = None,
    ) -> HealthCheckResult:
        """Create and store a health check result."""
        self._total_checks += 1
        if status != "healthy":
            self._consecutive_failures += 1
            self._total_failures += 1
        else:
            self._consecutive_failures = 0

        result = HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            latency_ms=latency_ms,
            details=details,
        )
        self._last_check = result
        return result

    def get_stats(self) -> dict[str, Any]:
        """Get health check statistics."""
        return {
            "name": self.name,
            "last_status": self._last_check.status if self._last_check else "unknown",
            "consecutive_failures": self._consecutive_failures,
            "total_checks": self._total_checks,
            "total_failures": self._total_failures,
            "success_rate": (
                round((self._total_checks - self._total_failures) / self._total_checks * 100, 2)
                if self._total_checks > 0
                else 0
            ),
        }


class DatabaseHealthCheck(DependencyHealthCheck):
    """Health check for database connectivity."""

    def __init__(self, db_session_factory, timeout_seconds: float = 5.0):
        super().__init__("database", timeout_seconds)
        self.db_session_factory = db_session_factory

    async def check(self) -> HealthCheckResult:
        """Check database connectivity."""
        start_time = time.perf_counter()

        try:
            # Use asyncio.to_thread for blocking DB operations
            await asyncio.wait_for(
                asyncio.to_thread(self._check_db),
                timeout=self.timeout_seconds,
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            return self._create_result(
                status="healthy",
                message="Database connection successful",
                latency_ms=latency_ms,
            )
        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return self._create_result(
                status="unhealthy",
                message="Database connection timeout",
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            log.error("database_health_check_failed", error=str(e))
            return self._create_result(
                status="unhealthy",
                message=f"Database connection failed: {str(e)}",
                latency_ms=latency_ms,
            )

    def _check_db(self) -> None:
        """Perform actual database check (blocking)."""
        from sqlalchemy import text

        session = self.db_session_factory()
        try:
            session.execute(text("SELECT 1"))
        finally:
            session.close()


class RedisHealthCheck(DependencyHealthCheck):
    """Health check for Redis connectivity."""

    def __init__(self, redis_client_factory, timeout_seconds: float = 3.0):
        super().__init__("redis", timeout_seconds)
        self.redis_client_factory = redis_client_factory

    async def check(self) -> HealthCheckResult:
        """Check Redis connectivity."""
        start_time = time.perf_counter()

        try:
            client = self.redis_client_factory()
            await asyncio.wait_for(
                asyncio.to_thread(client.ping),
                timeout=self.timeout_seconds,
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            return self._create_result(
                status="healthy",
                message="Redis connection successful",
                latency_ms=latency_ms,
            )
        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return self._create_result(
                status="unhealthy",
                message="Redis connection timeout",
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            log.error("redis_health_check_failed", error=str(e))
            return self._create_result(
                status="unhealthy",
                message=f"Redis connection failed: {str(e)}",
                latency_ms=latency_ms,
            )


class ExternalServiceHealthCheck(DependencyHealthCheck):
    """Health check for external HTTP services."""

    def __init__(
        self,
        name: str,
        url: str,
        timeout_seconds: float = 5.0,
        expected_status: int = 200,
    ):
        super().__init__(name, timeout_seconds)
        self.url = url
        self.expected_status = expected_status

    async def check(self) -> HealthCheckResult:
        """Check external service availability."""
        start_time = time.perf_counter()

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await asyncio.wait_for(
                    client.get(self.url, timeout=self.timeout_seconds),
                    timeout=self.timeout_seconds + 1,
                )

            latency_ms = (time.perf_counter() - start_time) * 1000

            if response.status_code == self.expected_status:
                return self._create_result(
                    status="healthy",
                    message=f"Service responded with {response.status_code}",
                    latency_ms=latency_ms,
                    details={"status_code": response.status_code},
                )
            else:
                return self._create_result(
                    status="degraded",
                    message=f"Unexpected status code: {response.status_code}",
                    latency_ms=latency_ms,
                    details={"status_code": response.status_code},
                )

        except asyncio.TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return self._create_result(
                status="unhealthy",
                message="Service request timeout",
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            log.error("external_service_health_check_failed", url=self.url, error=str(e))
            return self._create_result(
                status="unhealthy",
                message=f"Service check failed: {str(e)}",
                latency_ms=latency_ms,
            )


class CompositeHealthChecker:
    """Aggregate multiple health checks into a comprehensive report."""

    def __init__(self):
        self._checks: list[DependencyHealthCheck] = []
        self._cache_key = "health:composite"
        self._cache_ttl = 30  # seconds

    def add_check(self, check: DependencyHealthCheck) -> None:
        """Add a health check to the composite checker."""
        self._checks.append(check)

    async def check_all(self) -> dict[str, Any]:
        """Run all health checks and return aggregated results."""
        # Check cache first
        cached = get_cached(self._cache_key)
        if cached:
            return cached

        start_time = time.perf_counter()
        results = []
        overall_status = "healthy"

        # Run all checks concurrently
        tasks = [check.check() for check in self._checks]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(completed_results):
            if isinstance(result, Exception):
                # Handle unexpected exceptions
                check_name = self._checks[i].name if i < len(self._checks) else "unknown"
                log.error("health_check_exception", check=check_name, error=str(result))
                results.append({
                    "name": check_name,
                    "status": "unhealthy",
                    "message": f"Check failed with exception: {str(result)}",
                    "latency_ms": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                overall_status = "unhealthy"
            else:
                results.append(result.to_dict())
                if result.status == "unhealthy":
                    overall_status = "unhealthy"
                elif result.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"

        total_latency_ms = (time.perf_counter() - start_time) * 1000

        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_latency_ms": round(total_latency_ms, 2),
            "checks": results,
            "summary": {
                "total_checks": len(results),
                "healthy_count": sum(1 for r in results if r["status"] == "healthy"),
                "degraded_count": sum(1 for r in results if r["status"] == "degraded"),
                "unhealthy_count": sum(1 for r in results if r["status"] == "unhealthy"),
            },
        }

        # Cache the result
        set_cached(self._cache_key, report, ttl=self._cache_ttl)

        return report

    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics for all health checks."""
        return {
            "checks": [check.get_stats() for check in self._checks],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def create_default_health_checker(
    db_session_factory=None,
    redis_client_factory=None,
) -> CompositeHealthChecker:
    """Create a health checker with default checks."""
    checker = CompositeHealthChecker()

    # Add system health check (always included)
    system_check = DependencyHealthCheck("system")

    async def system_check_impl() -> HealthCheckResult:
        try:
            health = get_system_health()
            return HealthCheckResult(
                name="system",
                status=health.get("status", "unknown"),
                message="System metrics collected",
                details=health,
            )
        except Exception as e:
            return HealthCheckResult(
                name="system",
                status="unhealthy",
                message=f"System check failed: {str(e)}",
            )

    system_check.check = system_check_impl
    checker.add_check(system_check)

    # Add database check if session factory provided
    if db_session_factory:
        checker.add_check(DatabaseHealthCheck(db_session_factory))

    # Add Redis check if client factory provided
    if redis_client_factory:
        checker.add_check(RedisHealthCheck(redis_client_factory))

    return checker
