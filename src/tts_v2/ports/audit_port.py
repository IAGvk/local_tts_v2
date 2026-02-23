"""AuditPort — contract for compliance event logging."""

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class AuditPort(Protocol):
    """Record a synthesis audit event.

    Implementations:
        NoOpAuditAdapter    — discards events, for testing
        FileAuditAdapter    — appends JSONL records to a file
        SplunkAuditAdapter  — ships events to Splunk/SIEM (future)
    """

    def log_synthesis(self, event: Dict[str, Any]) -> None:
        """Record a synthesis event.

        Expected event keys (all optional — adapters should handle missing keys):
            persona       (str)   agent persona used
            speaker_id    (str)   backend speaker ID
            text_len      (int)   character count of normalised text
            duration_s    (float) audio duration in seconds
            rtf           (float) real-time factor (elapsed / duration)
            output_path   (str)   where the file was written, if applicable
            ts            (float) unix timestamp (added by adapter if absent)

        Args:
            event: Audit event dictionary.
        """
        ...
