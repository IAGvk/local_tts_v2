"""SynthesizerPort — contract for any TTS backend.

Implementations live in adapters/synthesizer/.
The service layer only imports this protocol, never a concrete adapter.
"""

from typing import List, Protocol, runtime_checkable

from ..domain.audio import AudioChunk, SynthesisRequest


@runtime_checkable
class SynthesizerPort(Protocol):
    """Convert a SynthesisRequest into an AudioChunk.

    Implementations:
        CoquiSynthesizerAdapter  — wraps Coqui VITS (current default)
        MockSynthesizerAdapter   — returns silence, for unit tests
        FishSpeechAdapter        — future
        F5TTSAdapter             — future
    """

    def synthesize(self, request: SynthesisRequest) -> AudioChunk:
        """Synthesise speech from the normalised text in ``request``.

        Args:
            request: A fully-normalised SynthesisRequest.

        Returns:
            AudioChunk containing the synthesised waveform.

        Raises:
            RuntimeError: On synthesis failure.
        """
        ...

    def get_speakers(self) -> List[str]:
        """Return backend-specific speaker IDs available for this adapter."""
        ...
