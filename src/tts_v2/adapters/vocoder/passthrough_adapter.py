"""PassthroughVocoderAdapter — for end-to-end models that produce wav directly.

VITS, F5-TTS, and FishSpeech all output a waveform directly — there is no
separate mel-to-wav vocoder step. This adapter satisfies the VocoderPort
contract by returning its input unchanged.

When two-stage models (Tacotron2 + HiFiGAN) are added, create a
HiFiGANAdapter in this package instead.
"""

import numpy as np


class PassthroughVocoderAdapter:
    """VocoderPort implementation for end-to-end synthesizers.

    No model loading, no imports beyond numpy. Simply returns the input,
    allowing the TTSService to treat all model types uniformly.
    """

    def vocode(self, mel: np.ndarray) -> np.ndarray:
        """Pass through a waveform unchanged.

        For end-to-end models the 'mel' argument is already a waveform.
        """
        return mel

    def is_passthrough(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "PassthroughVocoderAdapter()"
