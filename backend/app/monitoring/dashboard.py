from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.monitoring.metrics import metrics_collector

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/metrics")
def get_metrics() -> dict[str, object]:
    return metrics_collector.snapshot()


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard() -> str:
    snapshot = metrics_collector.snapshot()
    endpoints = snapshot["endpoints"]
    rows = ""

    for endpoint, values in endpoints.items():
        rows += (
            "<tr>"
            f"<td>{endpoint}</td>"
            f"<td>{values['request_count']}</td>"
            f"<td>{values['average_duration_ms']}</td>"
            f"<td>{values['error_rate']}%</td>"
            "</tr>"
        )

    if not rows:
        rows = "<tr><td colspan='4'>No traffic yet</td></tr>"

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Monitoring Dashboard</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2937; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
    h1 {{ margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Monitoring Dashboard</h1>

  <div class=\"card\">
    <p><strong>Total Requests:</strong> {snapshot['total_requests']}</p>
    <p><strong>Total Errors:</strong> {snapshot['total_errors']}</p>
    <p><strong>Overall Error Rate:</strong> {snapshot['overall_error_rate']}%</p>
    <p><strong>System Health:</strong> {snapshot['system_health']}</p>
  </div>

  <div class=\"card\">
    <h2>Endpoint Metrics</h2>
    <table>
      <thead>
        <tr>
          <th>Endpoint</th>
          <th>Requests</th>
          <th>Avg Response Time (ms)</th>
          <th>Error Rate</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>

  <script>
    setTimeout(function () {{ window.location.reload(); }}, 10000);
  </script>
</body>
</html>
"""
