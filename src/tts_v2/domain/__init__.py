"""Domain layer: Speaker identities and audio value objects."""
from .voice import Speaker, get_speaker, list_personas, register_persona, AGENT_REGISTRY, DEFAULT_PERSONA
from .audio import AudioChunk, SynthesisRequest, SynthesisResult

__all__ = [
    "Speaker",
    "AudioChunk",
    "SynthesisRequest",
    "SynthesisResult",
    "get_speaker",
    "list_personas",
    "register_persona",
    "AGENT_REGISTRY",
    "DEFAULT_PERSONA",
]
