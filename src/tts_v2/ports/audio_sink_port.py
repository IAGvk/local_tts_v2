"""AudioSinkPort — contract for writing synthesised audio."""

from typing import Protocol, runtime_checkable

from ..domain.audio import AudioChunk


@runtime_checkable
class AudioSinkPort(Protocol):
    """Write an AudioChunk to a destination.

    Implementations:
        FileSinkAdapter    — writes WAV to disk
        StreamSinkAdapter  — writes PCM to a socket/IVR stream (future)
        NullSinkAdapter    — discards audio, for unit tests
    """

    def write(self, chunk: AudioChunk, destination: str) -> str:
        """Persist or stream the audio chunk.

        Args:
            chunk:       The synthesised AudioChunk.
            destination: Adapter-specific destination string.
                         For FileSinkAdapter this is a file path.
                         For StreamSinkAdapter this is a connection ID.

        Returns:
            Resolved destination string (absolute path, stream ID, etc.).
        """
        ...
