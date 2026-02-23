"""Domain: speaker identities and agent persona registry.

IMPORTANT: This module has NO external imports (no torch, no coqui, no numpy).
It is pure Python business knowledge — safe to import anywhere including tests.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Speaker:
    """Immutable value object representing a voice persona.

    Decoupled from any specific TTS backend — ``speaker_id`` is the
    backend-specific handle (e.g. VCTK 'p225' for Coqui), but the
    domain only cares about the persona.
    """

    persona: str       # e.g. "professional_male"
    speaker_id: str    # backend-specific identifier, e.g. "p225"
    agent_name: str    # human-readable label
    description: str   # compliance / usage guidance


# ---------------------------------------------------------------------------
# BFSI agent registry
# Maps persona names → Speaker value objects.
# Speaker IDs here reference VCTK speakers in Coqui's pretrained VITS model.
# When swapping to FishSpeech / F5-TTS, update speaker_id only — persona keys
# stay the same so the service layer never needs to change.
# ---------------------------------------------------------------------------
AGENT_REGISTRY: Dict[str, Speaker] = {
    "professional_male": Speaker(
        persona="professional_male",
        speaker_id="p225",
        agent_name="Professional Banking Officer",
        description="Formal, authoritative. Suitable for account updates and compliance notices.",
    ),
    "friendly_female": Speaker(
        persona="friendly_female",
        speaker_id="p226",
        agent_name="Friendly Customer Service",
        description="Warm, approachable. Suitable for general enquiries and support.",
    ),
    "neutral_male": Speaker(
        persona="neutral_male",
        speaker_id="p227",
        agent_name="Neutral System Voice",
        description="Clear, neutral. Suitable for standard announcements.",
    ),
    "professional_female": Speaker(
        persona="professional_female",
        speaker_id="p228",
        agent_name="Professional Financial Advisor",
        description="Confident, knowledgeable. Suitable for investment and advisory content.",
    ),
}

DEFAULT_PERSONA = "neutral_male"


def get_speaker(persona: str, fallback: Optional[str] = None) -> Speaker:
    """Resolve a persona name to a Speaker value object.

    Args:
        persona:  Agent persona key (e.g. 'professional_male').
        fallback: Persona to use if ``persona`` is not registered.
                  Defaults to DEFAULT_PERSONA.

    Returns:
        Speaker value object.

    Raises:
        ValueError: If neither persona nor fallback are registered.
    """
    if persona in AGENT_REGISTRY:
        speaker = AGENT_REGISTRY[persona]
        logger.debug(f"Resolved persona '{persona}' → speaker '{speaker.speaker_id}'")
        return speaker

    effective_fallback = fallback or DEFAULT_PERSONA
    if effective_fallback in AGENT_REGISTRY:
        speaker = AGENT_REGISTRY[effective_fallback]
        logger.warning(
            f"Persona '{persona}' not found. "
            f"Falling back to '{effective_fallback}' → '{speaker.speaker_id}'"
        )
        return speaker

    raise ValueError(
        f"Persona '{persona}' not found and fallback '{effective_fallback}' "
        f"is also unregistered. Available: {list_personas()}"
    )


def list_personas() -> List[str]:
    """Return all registered persona keys."""
    return list(AGENT_REGISTRY.keys())


def register_persona(
    persona: str,
    speaker_id: str,
    agent_name: str,
    description: str,
) -> None:
    """Register a new agent persona at runtime.

    Useful for custom voices, fine-tuned speakers, or new TTS backends.

    Args:
        persona:     Unique key (e.g. 'australian_specialist').
        speaker_id:  Backend-specific ID (e.g. 'p230' for Coqui VCTK).
        agent_name:  Human-readable name.
        description: Usage guidance for compliance logging.

    Example::

        register_persona(
            persona="australian_specialist",
            speaker_id="p230",
            agent_name="Australian Banking Specialist",
            description="Local AU accent, suitable for domestic retail banking.",
        )
    """
    AGENT_REGISTRY[persona] = Speaker(
        persona=persona,
        speaker_id=speaker_id,
        agent_name=agent_name,
        description=description,
    )
    logger.info(f"Registered persona '{persona}' → speaker '{speaker_id}' ({agent_name})")
