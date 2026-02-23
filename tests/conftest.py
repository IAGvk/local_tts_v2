"""Shared test fixtures for tts_v2."""

import pytest

from tts_v2.adapters.audit.noop_audit_adapter import NoOpAuditAdapter
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
from tts_v2.adapters.synthesizer.mock_adapter import MockSynthesizerAdapter
from tts_v2.service.tts_service import TTSService


class NullSinkAdapter:
    """AudioSinkPort stub: records the last write call without touching disk."""

    def __init__(self):
        self.last_destination = None

    def write(self, chunk, destination: str) -> str:
        self.last_destination = destination
        return destination


@pytest.fixture
def null_sink():
    return NullSinkAdapter()


@pytest.fixture
def mock_service(null_sink):
    """A fully wired TTSService using mock/null adapters — no GPU needed."""
    return TTSService(
        synthesizer=MockSynthesizerAdapter(),
        normalizer=BFSINormalizerAdapter(),
        audio_sink=null_sink,
        audit=NoOpAuditAdapter(),
    )
