"""Structured error tracking and observability diagnostic hub."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ErrorDiagnosticReport:
    """Standardized error diagnostic envelope."""

    error_code: str
    error_type: str
    message: str
    timestamp: str
    context: Dict[str, Any]


class ErrorTracker:
    """Observability hook for tracking exceptions and recording telemetry failures."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger("error_tracker")
        self._incident_log: List[ErrorDiagnosticReport] = []

    def capture_exception(
        self, error: Exception, error_code: str, context: Optional[Dict[str, Any]] = None
    ) -> ErrorDiagnosticReport:
        """Records an exception incident and emits structured log data."""
        ctx = context or {}
        report = ErrorDiagnosticReport(
            error_code=error_code,
            error_type=type(error).__name__,
            message=str(error),
            timestamp=datetime.now(timezone.utc).isoformat(),
            context=ctx,
        )
        self._incident_log.append(report)
        self.logger.error(
            "Captured exception [%s]: %s",
            error_code,
            str(error),
            extra={"diagnostic_report": report.__dict__},
        )
        return report

    @property
    def total_incidents(self) -> int:
        """Returns total recorded failure incidents."""
        return len(self._incident_log)

    def get_latest_incidents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent incident reports formatted as dictionaries."""
        return [
            {
                "code": rep.error_code,
                "type": rep.error_type,
                "message": rep.message,
                "timestamp": rep.timestamp,
            }
            for rep in self._incident_log[-limit:]
        ]


# Global error tracker instance
global_error_tracker = ErrorTracker()
