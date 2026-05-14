from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from threading import Lock


@dataclass(slots=True)
class EndpointMetrics:
    request_count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0

    @property
    def average_duration_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round(self.total_duration_ms / self.request_count, 2)

    @property
    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round((self.error_count / self.request_count) * 100.0, 2)


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = Lock()
        self._total_requests = 0
        self._total_errors = 0
        self._endpoint_metrics: dict[str, EndpointMetrics] = {}
        self._recent_errors: deque[dict[str, object]] = deque(maxlen=25)

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        error_message: str | None = None,
    ) -> None:
        key = f"{method.upper()} {path}"
        rounded_duration = round(duration_ms, 2)
        is_error = status_code >= 500

        with self._lock:
            self._total_requests += 1
            if is_error:
                self._total_errors += 1

            endpoint = self._endpoint_metrics.setdefault(key, EndpointMetrics())
            endpoint.request_count += 1
            endpoint.total_duration_ms += rounded_duration
            if is_error:
                endpoint.error_count += 1
                self._recent_errors.appendleft(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "path": path,
                        "method": method.upper(),
                        "status_code": status_code,
                        "error": error_message or "Unhandled server error",
                    }
                )

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            overall_error_rate = (
                0.0
                if self._total_requests == 0
                else round((self._total_errors / self._total_requests) * 100.0, 2)
            )

            endpoints: dict[str, dict[str, object]] = {}
            for key, value in self._endpoint_metrics.items():
                payload = asdict(value)
                payload["average_duration_ms"] = value.average_duration_ms
                payload["error_rate"] = value.error_rate
                endpoints[key] = payload

            system_health = "healthy"
            if overall_error_rate >= 10.0:
                system_health = "degraded"
            if overall_error_rate >= 30.0:
                system_health = "unhealthy"

            return {
                "total_requests": self._total_requests,
                "total_errors": self._total_errors,
                "overall_error_rate": overall_error_rate,
                "system_health": system_health,
                "endpoints": endpoints,
                "recent_errors": list(self._recent_errors),
            }


metrics_collector = MetricsCollector()
