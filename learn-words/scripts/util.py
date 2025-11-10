import asyncio
import logging
import sys
import time
from collections import defaultdict
from typing import Dict

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Token bucket rate limiter with adaptive behavior."""

    def __init__(self, rate: float, burst: int, adaptive: bool = True):
        self.rate = rate  # tokens per second
        self.burst = burst  # max tokens in bucket
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.adaptive = adaptive

        # Adaptive rate limiting
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 60.0  # seconds

    async def acquire(self):
        """Acquire a token from the bucket."""
        async with self.lock:
            now = time.time()

            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    def record_success(self):
        """Record a successful API call for adaptive rate limiting."""
        if self.adaptive:
            self.success_count += 1
            self._adjust_rate_if_needed()

    def record_error(self):
        """Record a failed API call for adaptive rate limiting."""
        if self.adaptive:
            self.error_count += 1
            self._adjust_rate_if_needed()

    def _adjust_rate_if_needed(self):
        """Adjust rate based on success/error ratio."""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_interval:
            return

        total_calls = self.success_count + self.error_count
        if total_calls < 10:  # Need minimum sample size
            return

        error_rate = self.error_count / total_calls

        if error_rate > 0.1:  # More than 10% errors
            # Reduce rate by 20%
            self.rate *= 0.8
            logger.info(f"Rate limit reduced to {self.rate:.2f} req/s due to high error rate")
        elif error_rate < 0.02:  # Less than 2% errors
            # Increase rate by 10%
            self.rate *= 1.1
            logger.info(f"Rate limit increased to {self.rate:.2f} req/s due to low error rate")

        # Reset counters
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = now


class CircuitBreaker:
    """Circuit breaker pattern for API failure protection."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = asyncio.Lock()

    async def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        async with self.lock:
            if self.state == "OPEN":
                # Check if timeout has passed
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker moved to HALF_OPEN state")
                    return False
                return True
            return False

    async def record_success(self):
        """Record a successful operation."""
        async with self.lock:
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED after successful operation")

    async def record_failure(self):
        """Record a failed operation."""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    self.state = "OPEN"
                    logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")


class ErrorClassifier:
    """Classify different types of errors for better handling."""

    @staticmethod
    def classify_error(error: Exception) -> str:
        """Classify an error into a category."""
        error_str = str(error).lower()

        if "rate limit" in error_str or "429" in error_str:
            return "RATE_LIMIT"
        elif "timeout" in error_str or isinstance(error, asyncio.TimeoutError):
            return "TIMEOUT"
        elif "connection" in error_str or "network" in error_str:
            return "NETWORK"
        elif "json" in error_str or "parse" in error_str:
            return "PARSE_ERROR"
        elif "api" in error_str:
            return "API_ERROR"
        else:
            return "UNKNOWN"


class ParallelProgressTracker:
    """Enhanced progress tracking for parallel processing."""

    def __init__(self, total_words: int):
        self.total_words = total_words
        self.processed = 0
        self.skipped = 0
        self.errors = 0
        self.start_time = time.time()
        self.last_update = time.time()
        self.lock = asyncio.Lock()

        # Performance metrics
        self.throughput_history = []
        self.error_rate_history = []

    async def update(self, processed: int = 0, skipped: int = 0, errors: int = 0):
        """Update progress counters."""
        async with self.lock:
            self.processed += processed
            self.skipped += skipped
            self.errors += errors

            now = time.time()
            if now - self.last_update >= 10:  # Update every 10 seconds
                self._calculate_metrics()
                self._log_progress()
                self.last_update = now

    def _calculate_metrics(self):
        """Calculate performance metrics."""
        elapsed = time.time() - self.start_time
        total_completed = self.processed + self.skipped + self.errors

        if elapsed > 0:
            current_throughput = total_completed / elapsed
            self.throughput_history.append(current_throughput)

            if total_completed > 0:
                error_rate = self.errors / total_completed
                self.error_rate_history.append(error_rate)

    def _log_progress(self):
        """Log current progress and metrics."""
        total_completed = self.processed + self.skipped + self.errors
        progress_percent = (total_completed / self.total_words) * 100

        elapsed = time.time() - self.start_time
        if len(self.throughput_history) > 0:
            avg_throughput = sum(self.throughput_history) / len(self.throughput_history)
            remaining_words = self.total_words - total_completed
            eta_seconds = remaining_words / avg_throughput if avg_throughput > 0 else 0
            eta_minutes = eta_seconds / 60

            logger.info(
                f"Progress: {progress_percent:.1f}% ({total_completed}/{self.total_words}) | "
                f"Processed: {self.processed} | Skipped: {self.skipped} | Errors: {self.errors} | "
                f"Throughput: {avg_throughput:.1f} words/s | ETA: {eta_minutes:.1f} min"
            )


class PerformanceMonitor:
    """Comprehensive performance monitoring for parallel translation."""

    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "api_latency": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "db_writes": 0,
            "db_latency": [],
            "error_counts": defaultdict(int),
            "throughput_samples": [],
        }
        self.lock = asyncio.Lock()

    async def record_api_call(self, latency: float):
        """Record API call metrics."""
        async with self.lock:
            self.metrics["api_calls"] += 1
            self.metrics["api_latency"].append(latency)

    async def record_cache_hit(self):
        """Record cache hit."""
        async with self.lock:
            self.metrics["cache_hits"] += 1

    async def record_cache_miss(self):
        """Record cache miss."""
        async with self.lock:
            self.metrics["cache_misses"] += 1

    async def record_error(self, error_type: str):
        """Record error by type."""
        async with self.lock:
            self.metrics["error_counts"][error_type] += 1

    def get_summary(self) -> Dict:
        """Get performance summary."""
        api_latency = self.metrics["api_latency"]
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]

        return {
            "api_calls": self.metrics["api_calls"],
            "avg_api_latency": (sum(api_latency) / len(api_latency) if api_latency else 0),
            "cache_hit_rate": (self.metrics["cache_hits"] / cache_total if cache_total > 0 else 0),
            "total_errors": sum(self.metrics["error_counts"].values()),
            "error_breakdown": dict(self.metrics["error_counts"]),
        }


def setup_logging(script_dir):
    """Setup logging with correct paths."""
    log_file = script_dir / "reports" / "database_population.log"
    log_file.parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            # Use a custom StreamHandler with encoding error handling
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Configure all loggers to handle Unicode properly
    for handler in logging.root.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            # Set error handling for Unicode characters
            handler.stream.reconfigure(errors="backslashreplace")
