"""TTSService — pure orchestration layer.

ARCHITECTURE RULE: This file must NEVER import from:
  - torch, torchaudio, TTS, transformers, soundfile, num2words
  - Any adapter (adapters/*)
  - Any shared infrastructure (shared/*)

It only imports from:
  - tts_v2.domain.*  (value objects)
  - tts_v2.ports.*   (protocols)

If you need to add a framework dependency here, it belongs in an adapter instead.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from ..domain.audio import AudioChunk, SynthesisRequest, SynthesisResult
from ..domain.voice import get_speaker
from ..ports.audit_port import AuditPort
from ..ports.audio_sink_port import AudioSinkPort
from ..ports.normalizer_port import NormalizerPort
from ..ports.synthesizer_port import SynthesizerPort

logger = logging.getLogger(__name__)


class TTSService:
    """Orchestrates the full TTS pipeline via injected ports.

    Dependency injection makes every stage independently swappable and testable.
    The service itself has no knowledge of Coqui, PyTorch, HiFiGAN, or any
    filesystem API — those concerns live entirely in the adapters.

    Usage::

        from tts_v2.service.tts_service import TTSService
        from tts_v2.domain.audio import SynthesisRequest
        from tts_v2.adapters.synthesizer.coqui_adapter import CoquiSynthesizerAdapter
        from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
        from tts_v2.adapters.audio_sink.file_sink_adapter import FileSinkAdapter
        from tts_v2.adapters.audit.file_audit_adapter import FileAuditAdapter

        service = TTSService(
            synthesizer=CoquiSynthesizerAdapter(),
            normalizer=BFSINormalizerAdapter(),
            audio_sink=FileSinkAdapter(),
            audit=FileAuditAdapter("outputs/audit.jsonl"),
        )

        result = service.speak(
            SynthesisRequest(
                text="Your OTP is 482913. Please do not share it.",
                persona="professional_female",
                output_path="outputs/otp_notice.wav",
            )
        )

    Swapping backends (e.g. to FishSpeech) only requires changing the adapter
    passed to ``synthesizer=`` — the service, tests, and all other adapters
    remain untouched.
    """

    def __init__(
        self,
        synthesizer: SynthesizerPort,
        normalizer: NormalizerPort,
        audio_sink: AudioSinkPort,
        audit: AuditPort,
    ) -> None:
        """Inject all ports.

        Args:
            synthesizer: Backend that converts text → AudioChunk.
            normalizer:  Transforms raw text into TTS-ready spoken form.
            audio_sink:  Writes AudioChunk to a file, stream, or /dev/null.
            audit:       Records compliance events.
        """
        self._synth = synthesizer
        self._norm = normalizer
        self._sink = audio_sink
        self._audit = audit
        logger.info(
            f"TTSService ready | "
            f"synthesizer={type(synthesizer).__name__} | "
            f"normalizer={type(normalizer).__name__} | "
            f"sink={type(audio_sink).__name__} | "
            f"audit={type(audit).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speak(self, request: SynthesisRequest) -> SynthesisResult:
        """Execute the full pipeline for a single synthesis request.

        Pipeline stages:
          1. Normalise text (abbreviations, numbers, OTP)
          2. Resolve speaker via domain registry
          3. Synthesise speech via synthesizer port
          4. Write audio via audio_sink port (if output_path is set)
          5. Record audit event
          6. Return SynthesisResult

        Args:
            request: Synthesis job. ``text`` may be raw — normalisation
                     is applied in stage 1.

        Returns:
            SynthesisResult with chunk (in-memory) or output_path (file),
            plus timing metadata.

        Raises:
            RuntimeError: Propagated from synthesizer on failure.
            ValueError:   If text is empty.
        """
        if not request.text or not request.text.strip():
            raise ValueError("SynthesisRequest.text must not be empty")

        t_start = time.monotonic()

        # 1. Normalise
        normalised_text = self._norm.normalize(request.text)
        logger.info(f"[speak] normalised: '{request.text}' → '{normalised_text}'")

        # 2. Resolve speaker (validates persona exists in registry)
        speaker = get_speaker(request.persona)
        logger.info(f"[speak] persona='{request.persona}' → speaker='{speaker.speaker_id}'")

        # 3. Build a normalised request for the synthesizer
        norm_request = SynthesisRequest(
            text=normalised_text,
            persona=request.persona,
            output_path=request.output_path,
            metadata=request.metadata,
        )

        # 4. Synthesise
        try:
            chunk: AudioChunk = self._synth.synthesize(norm_request)
        except Exception as exc:
            logger.error(f"[speak] synthesis failed: {exc}")
            raise RuntimeError(f"Synthesis failed for persona='{request.persona}': {exc}") from exc

        logger.info(
            f"[speak] synthesised {chunk.duration_s:.2f}s "
            f"for {len(normalised_text)} chars"
        )

        # 5. Write to sink (file, stream, …)
        output_path: Optional[str] = None
        if request.output_path:
            output_path = self._sink.write(chunk, request.output_path)

        elapsed = time.monotonic() - t_start
        rtf = elapsed / chunk.duration_s if chunk.duration_s > 0 else 0.0

        # 6. Audit
        self._audit.log_synthesis({
            "persona": request.persona,
            "speaker_id": speaker.speaker_id,
            "text_raw": request.text,
            "text_len": len(normalised_text),
            "duration_s": round(chunk.duration_s, 3),
            "elapsed_s": round(elapsed, 3),
            "rtf": round(rtf, 4),
            "output_path": output_path,
            "metadata": request.metadata,
        })

        logger.info(f"[speak] done | duration={chunk.duration_s:.2f}s | RTF={rtf:.3f}")

        return SynthesisResult(
            request=request,
            chunk=chunk if not request.output_path else None,
            output_path=output_path,
            success=True,
        )
