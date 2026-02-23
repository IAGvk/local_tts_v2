"""MockSynthesizerAdapter — returns silence, for unit tests.

No model loading, no GPU, no network. Runs in milliseconds.
This is why hexagonal architecture makes testing so easy.
"""

import logging
from typing import List

import numpy as np

from ...domain.audio import AudioChunk, SynthesisRequest

logger = logging.getLogger(__name__)

_SAMPLE_RATE = 22050
_DURATION_S = 1.0  # 1 second of silence per call


class MockSynthesizerAdapter:
    """Implements SynthesizerPort with deterministic silence.

    Use in any test that exercises the service layer without needing a GPU:

        service = TTSService(
            synthesizer=MockSynthesizerAdapter(),
            ...
        )
    """

    def synthesize(self, request: SynthesisRequest) -> AudioChunk:
        n_samples = int(_SAMPLE_RATE * _DURATION_S)
        logger.debug(f"[mock] synthesize called for persona='{request.persona}'")
        return AudioChunk(
            samples=np.zeros(n_samples, dtype=np.float32),
            sample_rate=_SAMPLE_RATE,
            speaker_id="mock",
        )

    def get_speakers(self) -> List[str]:
        return ["mock"]

    def __repr__(self) -> str:
        return "MockSynthesizerAdapter()"
