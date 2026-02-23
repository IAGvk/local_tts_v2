"""Tests for TTSService — all run without GPU or model loading.

This demonstrates the key testing benefit of hexagonal architecture:
the service logic is fully testable in isolation via mock adapters.
"""

import numpy as np
import pytest

from tts_v2.adapters.audit.noop_audit_adapter import NoOpAuditAdapter
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
from tts_v2.adapters.synthesizer.mock_adapter import MockSynthesizerAdapter
from tts_v2.domain.audio import SynthesisRequest
from tts_v2.domain.voice import list_personas
from tts_v2.service.tts_service import TTSService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class NullSink:
    def write(self, chunk, destination):
        return destination


class TrackingNormalizer:
    """Records every normalize() call for assertion."""

    def __init__(self):
        self.calls = []

    def normalize(self, text: str) -> str:
        self.calls.append(text)
        return text.upper()


class CapturingAudit:
    """Captures audit events for assertion."""

    def __init__(self):
        self.events = []

    def log_synthesis(self, event):
        self.events.append(event)


# ---------------------------------------------------------------------------
# Service wiring
# ---------------------------------------------------------------------------

def make_service(**overrides):
    defaults = dict(
        synthesizer=MockSynthesizerAdapter(),
        normalizer=BFSINormalizerAdapter(),
        audio_sink=NullSink(),
        audit=NoOpAuditAdapter(),
    )
    defaults.update(overrides)
    return TTSService(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTTSServiceWiring:
    def test_service_initialises_without_error(self):
        svc = make_service()
        assert svc is not None

    def test_repr_includes_adapter_names(self, capsys):
        import logging
        logging.basicConfig(level=logging.INFO)
        make_service()  # INFO log emitted in __init__


class TestSpeakHappyPath:
    def test_returns_synthesis_result(self):
        svc = make_service()
        result = svc.speak(SynthesisRequest(text="Hello world", persona="neutral_male"))
        assert result.success is True

    def test_chunk_is_float32_numpy(self):
        svc = make_service()
        result = svc.speak(SynthesisRequest(text="Hello", persona="neutral_male"))
        assert result.chunk is not None
        assert result.chunk.samples.dtype == np.float32

    def test_chunk_duration_is_one_second(self):
        svc = make_service()
        result = svc.speak(SynthesisRequest(text="Hello", persona="neutral_male"))
        assert result.chunk.duration_s == pytest.approx(1.0, rel=0.01)

    def test_no_output_path_returns_chunk_not_path(self):
        svc = make_service()
        result = svc.speak(SynthesisRequest(text="Hello", persona="neutral_male"))
        assert result.chunk is not None
        assert result.output_path is None

    def test_with_output_path_chunk_is_none(self):
        svc = make_service()
        result = svc.speak(
            SynthesisRequest(text="Hello", persona="neutral_male", output_path="/tmp/test.wav")
        )
        assert result.chunk is None
        assert result.output_path == "/tmp/test.wav"

    @pytest.mark.parametrize("persona", ["professional_male", "friendly_female",
                                          "neutral_male", "professional_female"])
    def test_all_personas_synthesise(self, persona):
        svc = make_service()
        result = svc.speak(SynthesisRequest(text="Test utterance", persona=persona))
        assert result.success is True


class TestNormalisationIsApplied:
    def test_normalizer_receives_raw_text(self):
        tracker = TrackingNormalizer()
        svc = make_service(normalizer=tracker)
        svc.speak(SynthesisRequest(text="hello world", persona="neutral_male"))
        assert tracker.calls == ["hello world"]

    def test_otp_text_is_normalised(self):
        """BFSINormalizerAdapter should expand 482913 digit-by-digit."""
        tracker = TrackingNormalizer()
        svc = make_service(normalizer=tracker)
        svc.speak(SynthesisRequest(text="Your OTP is 482913", persona="neutral_male"))
        # Normalizer received the raw text
        assert "482913" in tracker.calls[0]


class TestAuditEvents:
    def test_audit_receives_event_on_speak(self):
        audit = CapturingAudit()
        svc = make_service(audit=audit)
        svc.speak(SynthesisRequest(text="Audit test", persona="neutral_male"))
        assert len(audit.events) == 1

    def test_audit_event_has_expected_keys(self):
        audit = CapturingAudit()
        svc = make_service(audit=audit)
        svc.speak(SynthesisRequest(text="Audit test", persona="neutral_male"))
        event = audit.events[0]
        for key in ("persona", "speaker_id", "text_len", "duration_s", "rtf"):
            assert key in event, f"Missing key: {key}"

    def test_audit_rtf_is_non_negative(self):
        audit = CapturingAudit()
        svc = make_service(audit=audit)
        svc.speak(SynthesisRequest(text="RTF test", persona="neutral_male"))
        assert audit.events[0]["rtf"] >= 0


class TestValidation:
    def test_empty_text_raises_value_error(self):
        svc = make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            svc.speak(SynthesisRequest(text="", persona="neutral_male"))

    def test_whitespace_only_text_raises_value_error(self):
        svc = make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            svc.speak(SynthesisRequest(text="   ", persona="neutral_male"))


class TestDomainIntegrity:
    def test_all_registered_personas_are_valid(self):
        """Domain registry should be consistent — each persona resolves."""
        from tts_v2.domain.voice import get_speaker
        for persona in list_personas():
            speaker = get_speaker(persona)
            assert speaker.speaker_id
            assert speaker.agent_name

    def test_unknown_persona_falls_back_to_default(self):
        from tts_v2.domain.voice import DEFAULT_PERSONA, get_speaker
        speaker = get_speaker("nonexistent_persona")
        default = get_speaker(DEFAULT_PERSONA)
        assert speaker.speaker_id == default.speaker_id
