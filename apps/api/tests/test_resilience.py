"""Tests for resilience patterns: circuit breaker, retry, and health checks."""

import pytest
import time
from unittest.mock import Mock, patch, AsyncMock

from app.core.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerError,
    get_circuit_breaker,
    reset_all_circuit_breakers,
)
from app.core.retry import (
    retry_with_backoff,
    RetryError,
    RetryConfig,
    RetryExecutor,
)


class TestCircuitBreaker:
    """Test circuit breaker pattern implementation."""

    def setup_method(self):
        """Reset circuit breakers before each test."""
        reset_all_circuit_breakers()

    def test_circuit_breaker_initial_state(self):
        """Test that circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker("test_service")
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0

    def test_circuit_breaker_success_resets_failures(self):
        """Test that successful calls reset failure count."""
        cb = CircuitBreaker("test_service", failure_threshold=3)
        
        # Simulate some failures
        cb._failure_count = 2
        
        # Successful call should reset failures
        cb._on_success()
        assert cb._failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_opens_after_threshold(self):
        """Test that circuit opens after reaching failure threshold."""
        cb = CircuitBreaker("test_service", failure_threshold=3)
        
        # Trigger failures up to threshold
        for _ in range(3):
            cb._on_failure()
        
        assert cb.state == CircuitState.OPEN
        assert cb._failure_count == 3

    def test_circuit_breaker_rejects_calls_when_open(self):
        """Test that open circuit rejects calls immediately."""
        cb = CircuitBreaker("test_service", failure_threshold=2, recovery_timeout=60)
        
        # Open the circuit
        cb._on_failure()
        cb._on_failure()
        
        assert cb.state == CircuitState.OPEN
        
        # Attempting to call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            cb.call(lambda: "result")

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test that circuit transitions to HALF_OPEN after timeout."""
        cb = CircuitBreaker("test_service", failure_threshold=2, recovery_timeout=1)
        
        # Open the circuit
        cb._on_failure()
        cb._on_failure()
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Next state check should transition to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN

    def test_circuit_breaker_closes_on_success_in_half_open(self):
        """Test that circuit closes on success in HALF_OPEN state."""
        cb = CircuitBreaker("test_service", failure_threshold=2, recovery_timeout=1)
        
        # Open the circuit
        cb._on_failure()
        cb._on_failure()
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Trigger state transition to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN
        
        # Success should close the circuit
        cb._on_success()
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0

    def test_circuit_breaker_reopens_on_failure_in_half_open(self):
        """Test that circuit reopens on failure in HALF_OPEN state."""
        cb = CircuitBreaker("test_service", failure_threshold=2, recovery_timeout=1)
        
        # Open the circuit
        cb._on_failure()
        cb._on_failure()
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Trigger state transition to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN
        
        # Failure should reopen the circuit
        cb._on_failure()
        assert cb.state == CircuitState.OPEN

    def test_circuit_breaker_stats(self):
        """Test circuit breaker statistics tracking."""
        cb = CircuitBreaker("test_service")
        
        # Simulate some calls
        cb._total_calls = 10
        cb._total_successes = 7
        cb._total_failures = 3
        
        stats = cb.get_stats()
        assert stats["name"] == "test_service"
        assert stats["total_calls"] == 10
        assert stats["total_successes"] == 7
        assert stats["total_failures"] == 3
        assert stats["success_rate"] == 70.0

    def test_circuit_breaker_call_success(self):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker("test_service")
        
        result = cb.call(lambda x: x * 2, 5)
        assert result == 10

    def test_circuit_breaker_call_failure(self):
        """Test failed call through circuit breaker."""
        cb = CircuitBreaker("test_service", failure_threshold=1)
        
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        # Should have recorded the failure
        assert cb._failure_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_async_call(self):
        """Test async call through circuit breaker."""
        cb = CircuitBreaker("test_service")
        
        async def async_func(x):
            return x * 2
        
        result = await cb.call_async(async_func, 5)
        assert result == 10


class TestRetryMechanism:
    """Test retry with exponential backoff implementation."""

    def test_retry_success_on_first_attempt(self):
        """Test that successful function doesn't retry."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_eventually_succeeds(self):
        """Test that retry succeeds after some failures."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_exhausts_all_attempts(self):
        """Test that retry gives up after max attempts."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(RetryError) as exc_info:
            always_fails()
        
        assert call_count == 3  # Initial + 2 retries
        assert isinstance(exc_info.value.last_exception, ValueError)

    def test_retry_only_catches_specified_exceptions(self):
        """Test that retry only catches specified exception types."""
        call_count = 0
        
        @retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )
        def specific_exception():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not a ConnectionError")
        
        with pytest.raises(ValueError):
            specific_exception()
        
        # Should not retry ValueError
        assert call_count == 1

    def test_retry_config_calculates_delay(self):
        """Test retry configuration delay calculation."""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0,
            jitter=False,
        )
        
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 8.0
        assert config.calculate_delay(4) == 10.0  # Capped at max_delay

    def test_retry_executor_stats(self):
        """Test retry executor statistics tracking."""
        executor = RetryExecutor(RetryConfig(max_retries=1))
        
        call_count = 0
        
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("First attempt fails")
            return "success"
        
        result = executor.execute(flaky_func, exceptions=(ConnectionError,))
        
        assert result == "success"
        
        stats = executor.get_stats()
        assert stats["total_attempts"] >= 2
        assert stats["total_successes"] == 1
        assert "success_rate" in stats


class TestHealthCheckIntegration:
    """Test health check integration with main application."""

    def test_health_check_result_to_dict(self):
        """Test health check result serialization."""
        from app.core.health_check import HealthCheckResult
        
        result = HealthCheckResult(
            name="test_service",
            status="healthy",
            message="All good",
            latency_ms=15.5,
            details={"version": "1.0.0"},
        )
        
        data = result.to_dict()
        assert data["name"] == "test_service"
        assert data["status"] == "healthy"
        assert data["message"] == "All good"
        assert data["latency_ms"] == 15.5
        assert data["details"]["version"] == "1.0.0"
        assert "timestamp" in data

    def test_composite_health_checker(self):
        """Test composite health checker aggregation."""
        from app.core.health_check import CompositeHealthChecker, DependencyHealthCheck
        
        checker = CompositeHealthChecker()
        
        # Create mock health check
        mock_check = DependencyHealthCheck("mock_service")
        
        async def mock_check_impl():
            from app.core.health_check import HealthCheckResult
            return HealthCheckResult(name="mock_service", status="healthy")
        
        mock_check.check = mock_check_impl
        checker.add_check(mock_check)
        
        assert len(checker._checks) == 1
