"""Shared audio utilities — normalisation, save, resample, PCM conversion.

USAGE: Import only from adapters. Never import from domain, ports, or service.
"""

import logging
from pathlib import Path
from typing import Union

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


def save_wav(
    samples: np.ndarray,
    filepath: Union[str, Path],
    sample_rate: int = 22050,
) -> None:
    """Write a float32 waveform array to a WAV file.

    Normalises peak amplitude to ≤ 1.0 before writing to prevent clipping.

    Args:
        samples:     float32 mono waveform.
        filepath:    Destination path (parent dirs created automatically).
        sample_rate: Sample rate in Hz.

    Raises:
        ValueError: If waveform is empty.
        IOError:    If the file cannot be written.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    arr = np.asarray(samples, dtype=np.float32)
    if arr.size == 0:
        raise ValueError("Cannot save: waveform array is empty.")

    peak = np.abs(arr).max()
    if peak > 1.0:
        arr = arr / peak
        logger.warning(f"Waveform normalised to prevent clipping (peak was {peak:.3f})")

    sf.write(str(filepath), arr, sample_rate)
    logger.info(f"Saved WAV → {filepath} ({arr.shape[0] / sample_rate:.2f}s @ {sample_rate}Hz)")


def pcm_to_bytes(samples: np.ndarray) -> bytes:
    """Convert float32 samples to signed 16-bit PCM bytes.

    Args:
        samples: float32 array in range [-1.0, 1.0].

    Returns:
        Raw int16 PCM bytes (little-endian, mono).
    """
    return (samples * 32767).astype(np.int16).tobytes()


def resample(samples: np.ndarray, src_rate: int, tgt_rate: int) -> np.ndarray:
    """Resample audio to a different sample rate using torchaudio.

    Args:
        samples:  float32 mono waveform.
        src_rate: Source sample rate in Hz.
        tgt_rate: Target sample rate in Hz.

    Returns:
        Resampled float32 array.
    """
    if src_rate == tgt_rate:
        return samples

    try:
        import torch
        import torchaudio.functional as F  # noqa: PLC0415

        tensor = torch.from_numpy(samples).unsqueeze(0)
        resampled = F.resample(tensor, src_rate, tgt_rate)
        result = resampled.squeeze(0).numpy()
        logger.debug(f"Resampled {src_rate}Hz → {tgt_rate}Hz ({len(samples)} → {len(result)} samples)")
        return result.astype(np.float32)
    except Exception as exc:
        logger.warning(f"torchaudio resample failed: {exc}. Returning original.")
        return samples
