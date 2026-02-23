"""Synthetic data augmentation hooks — metadata generation for dataset building."""

import hashlib
from typing import Dict, List, Optional


def _deterministic_filename(text: str) -> str:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"synthetic_{h}.wav"


def augment_synthetic(
    text_list: List[str],
    speaker_embedding: Optional[List[float]] = None,
    target_speaker: Optional[str] = None,
) -> List[Dict]:
    """Return structured synthesis metadata for downstream dataset generation.

    Does NOT generate audio. Provides the schema a synthesizer or dataset
    script would consume to produce a synthetic BFSI training corpus.

    Returns:
        List of dicts with keys: text, speaker_id, speaker_embedding,
        file_path, status.
    """
    return [
        {
            "text": text,
            "speaker_id": target_speaker or "synthetic",
            "speaker_embedding": speaker_embedding,
            "file_path": _deterministic_filename(text),
            "status": "pending_synthesis",
        }
        for text in text_list
    ]
