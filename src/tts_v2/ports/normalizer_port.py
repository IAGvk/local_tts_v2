"""NormalizerPort — contract for text normalisation before synthesis."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class NormalizerPort(Protocol):
    """Transform raw input text into TTS-ready spoken form.

    Implementations:
        BFSINormalizerAdapter  — abbreviations + numbers + OTP (current)
        IdentityNormalizerAdapter — pass-through, for testing
    """

    def normalize(self, text: str) -> str:
        """Return a normalised version of ``text``.

        Examples of transformations:
            "KYC" → "Know Your Customer"
            "$1,234.50" → "one thousand two hundred and thirty-four dollars and fifty cents"
            "482913" → "four eight two nine one three"

        Args:
            text: Raw input string.

        Returns:
            Normalised string, ready for the synthesizer.
        """
        ...
