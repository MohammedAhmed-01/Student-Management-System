from __future__ import annotations

from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.monitoring.metrics import metrics_collector
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = perf_counter()
        client = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (perf_counter() - start) * 1000.0
            metrics_collector.record_request(
                method=method,
                path=path,
                status_code=500,
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            logger.exception(
                "request_failed",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                    "client": client,
                    "error": str(exc),
                },
            )
            raise

        duration_ms = (perf_counter() - start) * 1000.0
        rounded_duration = round(duration_ms, 2)

        metrics_collector.record_request(
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=rounded_duration,
        )

        logger.info(
            "request_completed",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": rounded_duration,
                "client": client,
            },
        )

        response.headers["X-Response-Time-ms"] = str(rounded_duration)
        return response
