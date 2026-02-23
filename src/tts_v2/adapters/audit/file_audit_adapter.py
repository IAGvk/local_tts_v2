"""FileAuditAdapter — appends compliance events as JSONL records."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class FileAuditAdapter:
    """Implements AuditPort by writing newline-delimited JSON to a file.

    Each synthesis event is a single JSON object on its own line, making
    the log easy to tail, grep, or ship to a SIEM.

    Args:
        log_path: Path to the audit log file (created if absent).

    Example audit record::

        {
          "ts": 1740200000.123,
          "persona": "professional_female",
          "speaker_id": "p228",
          "text_len": 67,
          "duration_s": 2.84,
          "elapsed_s": 3.12,
          "rtf": 1.099,
          "output_path": "/Users/.../outputs/otp_notice.wav"
        }
    """

    def __init__(self, log_path: str = "outputs/audit.jsonl") -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileAuditAdapter: writing to {self._path}")

    def log_synthesis(self, event: Dict[str, Any]) -> None:
        record = {"ts": round(time.time(), 3), **event}
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"[audit] {record}")

    def __repr__(self) -> str:
        return f"FileAuditAdapter(log_path={str(self._path)!r})"
