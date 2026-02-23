"""Domain: audio value objects for the TTS pipeline.

IMPORTANT: numpy is the only import here — it is the universal audio
representation and is treated as a primitive type, not a framework.
No torch, no coqui, no soundfile in this file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class AudioChunk:
    """Immutable-by-convention audio value object.

    Carries a float32 mono waveform together with its provenance metadata.
    Use ``to_pcm_bytes()`` for IVR / streaming output.
    """

    samples: np.ndarray   # float32, mono
    sample_rate: int       # Hz, typically 22050 or 24000
    speaker_id: str        # backend speaker ID used to produce this chunk

    @property
    def duration_s(self) -> float:
        """Duration in seconds."""
        return len(self.samples) / self.sample_rate

    def to_pcm_bytes(self) -> bytes:
        """Return raw 16-bit PCM bytes (signed, little-endian).

        Use for IVR streaming or any sink that expects raw PCM.
        """
        pcm = (self.samples * 32767).astype(np.int16)
        return pcm.tobytes()

    def __repr__(self) -> str:
        return (
            f"AudioChunk(speaker={self.speaker_id!r}, "
            f"duration={self.duration_s:.2f}s, "
            f"sample_rate={self.sample_rate})"
        )


@dataclass(frozen=True)
class SynthesisRequest:
    """Immutable value object describing a single synthesis job.

    Text arriving here is assumed to be pre-normalised. The TTSService
    normalises raw text before creating the request passed to the synthesizer.
    """

    text: str                                         # normalised, TTS-ready text
    persona: str                                      # agent persona key
    output_path: Optional[str] = None                 # if set, sink writes to this path
    metadata: Dict[str, Any] = field(default_factory=dict)  # compliance metadata


@dataclass
class SynthesisResult:
    """Mutable result object returned by TTSService.speak().

    ``chunk`` is populated when no output_path was requested (in-memory mode).
    ``output_path`` is populated when the audio_sink wrote a file.
    """

    request: SynthesisRequest
    chunk: Optional[AudioChunk]      # in-memory result
    output_path: Optional[str]       # file result
    success: bool
    error: Optional[str] = None

    @property
    def duration_s(self) -> float:
        """Convenience accessor — works for both in-memory and file results."""
        return self.chunk.duration_s if self.chunk else 0.0
