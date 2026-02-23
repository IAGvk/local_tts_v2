"""Shared device resolution and Coqui/transformers compatibility shim.

USAGE: Import only from adapters. Never import this from domain, ports,
or the service layer — that would couple the core to infrastructure.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def apply_transformers_shim() -> None:
    """Patch transformers.pytorch_utils for Coqui compatibility.

    Coqui TTS imports ``isin_mps_friendly`` from transformers.pytorch_utils.
    transformers >= 4.45 removed this symbol. We restore it using torch.isin,
    which has had Mac MPS support since PyTorch 2.0.

    Call this once at the top of any adapter that imports Coqui:

        apply_transformers_shim()
        from TTS.api import TTS  # safe now
    """
    try:
        import transformers.pytorch_utils as _pu
        if not hasattr(_pu, "isin_mps_friendly"):
            import torch

            def _isin_mps_friendly(elements, test_elements):
                return torch.isin(elements, test_elements)

            _pu.isin_mps_friendly = _isin_mps_friendly
            logger.debug("Applied isin_mps_friendly shim (Coqui / transformers compatibility).")
    except Exception:
        # Non-fatal: shim only needed in specific version combinations.
        pass


def resolve_device(preferred: Optional[str] = None, use_gpu: bool = True) -> str:
    """Resolve the best available compute device.

    Priority:
      1. ``preferred`` if explicitly given
      2. Apple MPS  — if available and use_gpu=True  (Mac M1/M2/M3)
      3. CUDA       — if available and use_gpu=True  (Linux/Windows GPU)
      4. CPU        — fallback

    NOTE: Coqui's ``gpu=True`` flag only enables CUDA, not MPS.
    Adapters should always pass ``gpu=False`` to Coqui and call
    ``model.tts.to(device)`` themselves after loading.

    Args:
        preferred: Force a specific device ('cpu', 'cuda', 'mps').
        use_gpu:   Whether GPU acceleration is desired.

    Returns:
        Device string, e.g. 'mps', 'cuda', or 'cpu'.
    """
    import torch

    if preferred:
        logger.info(f"Device: using explicitly requested '{preferred}'")
        return preferred

    if not use_gpu:
        logger.info("Device: GPU disabled by caller, using CPU")
        return "cpu"

    if torch.backends.mps.is_available():
        logger.info("Device: Apple MPS (Metal) — Mac Silicon GPU")
        return "mps"

    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        logger.info(f"Device: CUDA — {name}")
        return "cuda"

    logger.info("Device: no GPU found, using CPU")
    return "cpu"
