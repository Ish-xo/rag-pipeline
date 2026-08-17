import time
import random
import asyncio
import logging
from typing import Callable, Any, Dict

logger = logging.getLogger("ultron.harness")

class CircuitBreaker:
    """
    Tracks failure rates for an API provider and opens circuit after max_failures.
    Cooldown period allows periodic resets.
    """
    def __init__(self, name: str, max_failures: int = 3, cooldown_seconds: float = 60.0):
        self.name = name
        self.max_failures = max_failures
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time = 0.0

    def is_open(self) -> bool:
        if self.failure_count >= self.max_failures:
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.cooldown_seconds:
                # Half-open: allow trial
                logger.info(f"Circuit breaker for '{self.name}' half-open after {elapsed:.1f}s cooldown.")
                return False
            return True
        return False

    def record_success(self):
        if self.failure_count > 0:
            logger.info(f"Circuit breaker for '{self.name}' reset after successful call.")
        self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(
            f"Circuit breaker for '{self.name}' recorded failure {self.failure_count}/{self.max_failures}."
        )


class ResilienceHarness:
    """
    Executes async LLM calls with exponential backoff retry and circuit breaker management.
    """
    def __init__(self, max_retries: int = 2, base_delay: float = 0.2, max_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get_breaker(self, provider_name: str) -> CircuitBreaker:
        if provider_name not in self.breakers:
            self.breakers[provider_name] = CircuitBreaker(provider_name)
        return self.breakers[provider_name]

    async def execute(self, provider_name: str, func: Callable[[], Any]) -> Any:
        breaker = self.get_breaker(provider_name)
        if breaker.is_open():
            raise RuntimeError(f"Circuit breaker open for provider '{provider_name}'. Skipping.")

        attempt = 0
        last_exception = None

        while attempt <= self.max_retries:
            try:
                result = await func()
                breaker.record_success()
                return result
            except Exception as e:
                last_exception = e
                attempt += 1
                logger.warning(f"Provider '{provider_name}' attempt {attempt} failed: {e}")
                if attempt <= self.max_retries:
                    # Exponential backoff with jitter
                    delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
                    jitter = random.uniform(0, 0.1)
                    await asyncio.sleep(delay + jitter)

        breaker.record_failure()
        raise last_exception or RuntimeError(f"Provider '{provider_name}' failed after {self.max_retries} retries.")
