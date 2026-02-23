"""BFSINormalizerAdapter — implements NormalizerPort with full BFSI pipeline."""

import logging

from ...text_normalization.abbreviation_handler import expand_abbreviations
from ...text_normalization.number_formatter import expand_numbers_in_text

logger = logging.getLogger(__name__)


class BFSINormalizerAdapter:
    """Chains abbreviation expansion + number/OTP formatting.

    Pipeline (in order):
      1. expand_abbreviations  — KYC → Know Your Customer, OTP → One Time Password
      2. expand_numbers_in_text — $1,234.50 → spoken form; 482913 → digit-by-digit

    This ordering matters: abbreviation expansion happens first so that
    "OTP 482913" becomes "One Time Password 482913" before the number
    pass converts "482913" to "four eight two nine one three".
    """

    def normalize(self, text: str) -> str:
        logger.info(f"[normalize] input: '{text}'")
        text = expand_abbreviations(text)
        text = expand_numbers_in_text(text)
        logger.info(f"[normalize] output: '{text}'")
        return text

    def __repr__(self) -> str:
        return "BFSINormalizerAdapter()"
