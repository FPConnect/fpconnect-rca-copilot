"""Circuit breaker pattern for external service calls."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
import structlog

log = structlog.get_logger()


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for resilient service calls.
    
    Prevents cascading failures by failing fast when a service is unavailable.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for automatic transitions."""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (
                self._last_failure_time
                and time.time() - self._last_failure_time > self.recovery_timeout
            ):
                log.info(
                    "circuit_breaker_half_open",
                    name=self.name,
                    timeout_seconds=self.recovery_timeout,
                )
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        self._total_calls += 1
        
        if self.state == CircuitState.OPEN:
            log.warning(
                "circuit_breaker_open",
                name=self.name,
                failure_count=self._failure_count,
                threshold=self.failure_threshold,
            )
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
            )

        if self.state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                log.warning(
                    "circuit_breaker_half_open_limit",
                    name=self.name,
                    max_calls=self.half_open_max_calls,
                )
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' HALF_OPEN limit reached."
                )
            self._half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function through the circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        self._total_calls += 1
        
        if self.state == CircuitState.OPEN:
            log.warning(
                "circuit_breaker_open",
                name=self.name,
                failure_count=self._failure_count,
                threshold=self.failure_threshold,
            )
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
            )

        if self.state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                log.warning(
                    "circuit_breaker_half_open_limit",
                    name=self.name,
                    max_calls=self.half_open_max_calls,
                )
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' HALF_OPEN limit reached."
                )
            self._half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self._total_successes += 1
        self._success_count += 1
        
        if self._state == CircuitState.HALF_OPEN:
            # Success in half-open state, close the circuit
            log.info(
                "circuit_breaker_closed",
                name=self.name,
                success_count=self._success_count,
            )
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._total_failures += 1
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            # Failure in half-open state, reopen the circuit
            log.warning(
                "circuit_breaker_reopened",
                name=self.name,
                reason="failure_in_half_open",
            )
            self._state = CircuitState.OPEN
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.failure_threshold:
                log.error(
                    "circuit_breaker_opened",
                    name=self.name,
                    failure_count=self._failure_count,
                    threshold=self.failure_threshold,
                )
                self._state = CircuitState.OPEN

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "half_open_calls": self._half_open_calls,
            "half_open_max_calls": self.half_open_max_calls,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "success_rate": (
                round(self._total_successes / self._total_calls * 100, 2)
                if self._total_calls > 0
                else 0
            ),
            "last_failure_time": (
                datetime.fromtimestamp(self._last_failure_time, tz=timezone.utc).isoformat()
                if self._last_failure_time
                else None
            ),
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        log.info("circuit_breaker_reset", name=self.name)
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0


# Global registry of circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker by name."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, **kwargs)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict[str, dict[str, Any]]:
    """Get statistics for all circuit breakers."""
    return {name: cb.get_stats() for name, cb in _circuit_breakers.items()}


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers (useful for testing)."""
    for cb in _circuit_breakers.values():
        cb.reset()
