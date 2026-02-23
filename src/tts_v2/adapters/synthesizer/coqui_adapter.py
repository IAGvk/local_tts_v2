"""CoquiSynthesizerAdapter — implements SynthesizerPort using Coqui VITS.

All Coqui/torch imports are scoped to this file.
"""

import logging
from typing import List, Optional

import numpy as np

from ...domain.audio import AudioChunk, SynthesisRequest
from ...domain.voice import get_speaker
from ...shared.device_utils import apply_transformers_shim, resolve_device

# Apply shim before Coqui import
apply_transformers_shim()

try:
    from TTS.api import TTS
    import torch
except ImportError as exc:
    raise RuntimeError(
        "Coqui TTS or PyTorch not installed. Run: pip install coqui-tts torch torchaudio"
    ) from exc

logger = logging.getLogger(__name__)


class CoquiSynthesizerAdapter:
    """Wraps Coqui TTS to implement SynthesizerPort.

    Handles:
    - MPS-safe loading (gpu=False + manual .to(device) post-load)
    - Multi-speaker VCTK VITS model (default)
    - Persona → speaker_id resolution via domain registry

    Swap this adapter for FishSpeechAdapter or F5TTSAdapter to change
    backends without touching the service layer.
    """

    def __init__(
        self,
        model_name: str = "tts_models/en/vctk/vits",
        use_gpu: bool = True,
        device: Optional[str] = None,
        sample_rate: int = 22050,
    ) -> None:
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.device = resolve_device(preferred=device, use_gpu=use_gpu)

        logger.info(f"Loading Coqui model '{model_name}' (cpu load → move to {self.device})")
        try:
            # Always load on CPU — Coqui's gpu=True only activates CUDA,
            # raises AssertionError on Mac MPS.
            self.model = TTS(model_name=model_name, progress_bar=False, gpu=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to load Coqui model '{model_name}': {exc}") from exc

        if self.device != "cpu":
            try:
                self.model.tts.to(self.device)
                logger.info(f"Model moved to {self.device}")
            except Exception as exc:
                logger.warning(f"Could not move to {self.device}: {exc}. Falling back to CPU.")
                self.device = "cpu"

        logger.info(f"CoquiSynthesizerAdapter ready | model={model_name} | device={self.device}")

    # ------------------------------------------------------------------
    # SynthesizerPort implementation
    # ------------------------------------------------------------------

    def synthesize(self, request: SynthesisRequest) -> AudioChunk:
        """Synthesise speech and return an AudioChunk."""
        speaker = get_speaker(request.persona)
        logger.info(
            f"[synthesize] persona='{request.persona}' | "
            f"speaker='{speaker.speaker_id}' | "
            f"text_len={len(request.text)}"
        )

        try:
            wav = self.model.tts(text=request.text, speaker=speaker.speaker_id)
        except Exception as exc:
            logger.error(f"[synthesize] Coqui synthesis failed: {exc}")
            raise RuntimeError(f"Coqui synthesis failed: {exc}") from exc

        samples = np.asarray(wav, dtype=np.float32)
        chunk = AudioChunk(
            samples=samples,
            sample_rate=self.sample_rate,
            speaker_id=speaker.speaker_id,
        )
        logger.info(f"[synthesize] produced {chunk.duration_s:.2f}s AudioChunk")
        return chunk

    def get_speakers(self) -> List[str]:
        """Return Coqui model's available speaker IDs."""
        return getattr(self.model, "speakers", None) or []

    def __repr__(self) -> str:
        return (
            f"CoquiSynthesizerAdapter(model={self.model_name!r}, device={self.device!r})"
        )
