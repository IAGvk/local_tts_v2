"""FileSinkAdapter — writes AudioChunk to a WAV file."""

import logging

from ...domain.audio import AudioChunk
from ...shared.audio_utils import save_wav

logger = logging.getLogger(__name__)


class FileSinkAdapter:
    """Implements AudioSinkPort by writing a WAV file to disk."""

    def write(self, chunk: AudioChunk, destination: str) -> str:
        """Write AudioChunk samples to a WAV file.

        Args:
            chunk:       AudioChunk to write.
            destination: File path (parent dirs created automatically).

        Returns:
            Resolved absolute file path as string.
        """
        save_wav(chunk.samples, destination, chunk.sample_rate)
        from pathlib import Path
        return str(Path(destination).resolve())

    def __repr__(self) -> str:
        return "FileSinkAdapter()"
