"""VocoderPort — contract for mel-to-waveform conversion.

For end-to-end models (VITS, F5-TTS, FishSpeech) that produce a waveform
directly, use PassthroughVocoderAdapter which satisfies this port by
returning the input unchanged.

For two-stage models (Tacotron2, FastSpeech2), use HiFiGANAdapter.
"""

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class VocoderPort(Protocol):
    """Convert a mel-spectrogram (or pass through a raw waveform).

    Implementations:
        PassthroughVocoderAdapter  — for end-to-end models (VITS etc.)
        HiFiGANAdapter             — for two-stage Tacotron2/FastSpeech2 (future)
    """

    def vocode(self, mel: np.ndarray) -> np.ndarray:
        """Convert mel-spectrogram to waveform.

        For passthrough adapters, ``mel`` is already a waveform and is
        returned unchanged.

        Args:
            mel: Mel-spectrogram array (n_mels × T) or raw waveform.

        Returns:
            Waveform as float32 numpy array (mono).
        """
        ...

    def is_passthrough(self) -> bool:
        """Return True if this adapter bypasses vocoding (end-to-end model)."""
        ...
