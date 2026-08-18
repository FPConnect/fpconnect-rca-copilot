"""Retry mechanism with exponential backoff for resilient service calls."""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Type, Union
import structlog

log = structlog.get_logger()


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    logger_name: Optional[str] = None,
) -> Callable:
    """
    Decorator for adding retry logic with exponential backoff to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds between retries
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Add randomness to prevent thundering herd
        exceptions: Tuple of exception types to retry on
        logger_name: Name for logging purposes
        
    Returns:
        Decorated function with retry capability
        
    Example:
        @retry_with_backoff(max_retries=3, exceptions=(ConnectionError,))
        def call_external_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        log.error(
                            "retry_exhausted",
                            function=func.__name__,
                            logger=logger_name or func.__module__,
                            attempts=max_retries + 1,
                            error=str(e),
                        )
                        raise RetryError(
                            f"All {max_retries + 1} attempts failed for {func.__name__}",
                            last_exception=e,
                        ) from e
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent synchronized retries
                    if jitter:
                        current_delay *= (0.5 + random.random())
                    
                    log.warning(
                        "retry_attempt",
                        function=func.__name__,
                        logger=logger_name or func.__module__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay_seconds=round(current_delay, 2),
                        error=str(e),
                    )
                    
                    time.sleep(current_delay)
            
            # Should never reach here, but just in case
            raise RetryError(
                f"Unexpected retry loop exit for {func.__name__}",
                last_exception=last_exception,
            )
        
        return wrapper
    return decorator


async def retry_async_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    logger_name: Optional[str] = None,
) -> Callable:
    """
    Async decorator for adding retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds between retries
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Add randomness to prevent thundering herd
        exceptions: Tuple of exception types to retry on
        logger_name: Name for logging purposes
        
    Returns:
        Decorated async function with retry capability
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        log.error(
                            "retry_exhausted",
                            function=func.__name__,
                            logger=logger_name or func.__module__,
                            attempts=max_retries + 1,
                            error=str(e),
                        )
                        raise RetryError(
                            f"All {max_retries + 1} attempts failed for {func.__name__}",
                            last_exception=e,
                        ) from e
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent synchronized retries
                    if jitter:
                        current_delay *= (0.5 + random.random())
                    
                    log.warning(
                        "retry_attempt",
                        function=func.__name__,
                        logger=logger_name or func.__module__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay_seconds=round(current_delay, 2),
                        error=str(e),
                    )
                    
                    await asyncio.sleep(current_delay)
            
            # Should never reach here, but just in case
            raise RetryError(
                f"Unexpected retry loop exit for {func.__name__}",
                last_exception=last_exception,
            )
        
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        if self.jitter:
            delay *= (0.5 + random.random())
        return delay


class RetryExecutor:
    """Execute functions with retry logic."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self._total_attempts = 0
        self._total_failures = 0
        self._total_successes = 0
    
    def execute(
        self,
        func: Callable,
        *args,
        exceptions: tuple[Type[Exception], ...] = (Exception,),
        logger_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Execute a function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            self._total_attempts += 1
            
            try:
                result = func(*args, **kwargs)
                self._total_successes += 1
                return result
            except exceptions as e:
                last_exception = e
                self._total_failures += 1
                
                if attempt == self.config.max_retries:
                    log.error(
                        "retry_exhausted",
                        function=func.__name__,
                        logger=logger_name or func.__module__,
                        attempts=self.config.max_retries + 1,
                        error=str(e),
                    )
                    raise RetryError(
                        f"All {self.config.max_retries + 1} attempts failed for {func.__name__}",
                        last_exception=e,
                    ) from e
                
                delay = self.config.calculate_delay(attempt)
                
                log.warning(
                    "retry_attempt",
                    function=func.__name__,
                    logger=logger_name or func.__module__,
                    attempt=attempt + 1,
                    max_retries=self.config.max_retries,
                    delay_seconds=round(delay, 2),
                    error=str(e),
                )
                
                time.sleep(delay)
        
        raise RetryError(
            f"Unexpected retry loop exit for {func.__name__}",
            last_exception=last_exception,
        )
    
    async def execute_async(
        self,
        func: Callable,
        *args,
        exceptions: tuple[Type[Exception], ...] = (Exception,),
        logger_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Execute an async function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            self._total_attempts += 1
            
            try:
                result = await func(*args, **kwargs)
                self._total_successes += 1
                return result
            except exceptions as e:
                last_exception = e
                self._total_failures += 1
                
                if attempt == self.config.max_retries:
                    log.error(
                        "retry_exhausted",
                        function=func.__name__,
                        logger=logger_name or func.__module__,
                        attempts=self.config.max_retries + 1,
                        error=str(e),
                    )
                    raise RetryError(
                        f"All {self.config.max_retries + 1} attempts failed for {func.__name__}",
                        last_exception=e,
                    ) from e
                
                delay = self.config.calculate_delay(attempt)
                
                log.warning(
                    "retry_attempt",
                    function=func.__name__,
                    logger=logger_name or func.__module__,
                    attempt=attempt + 1,
                    max_retries=self.config.max_retries,
                    delay_seconds=round(delay, 2),
                    error=str(e),
                )
                
                await asyncio.sleep(delay)
        
        raise RetryError(
            f"Unexpected retry loop exit for {func.__name__}",
            last_exception=last_exception,
        )
    
    def get_stats(self) -> dict[str, Any]:
        """Get retry execution statistics."""
        return {
            "total_attempts": self._total_attempts,
            "total_successes": self._total_successes,
            "total_failures": self._total_failures,
            "success_rate": (
                round(self._total_successes / self._total_attempts * 100, 2)
                if self._total_attempts > 0
                else 0
            ),
            "config": {
                "max_retries": self.config.max_retries,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "exponential_base": self.config.exponential_base,
                "jitter": self.config.jitter,
            },
        }


# Default retry executor instance
default_retry_executor = RetryExecutor()
