"""NoOpAuditAdapter — discards all audit events. Use in unit tests."""

from typing import Any, Dict


class NoOpAuditAdapter:
    """Implements AuditPort by doing nothing.

    Use this in tests and local experiments where you don't need
    a persistent audit trail.
    """

    def log_synthesis(self, event: Dict[str, Any]) -> None:
        pass  # intentionally silent

    def __repr__(self) -> str:
        return "NoOpAuditAdapter()"
