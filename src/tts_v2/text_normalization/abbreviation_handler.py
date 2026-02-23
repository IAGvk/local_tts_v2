"""BFSI-specific abbreviation expansion for TTS normalization."""

import logging
import re
from typing import Dict, Match

logger = logging.getLogger(__name__)

_ABBREVIATIONS: Dict[str, str] = {
    "KYC": "Know Your Customer",
    "AML": "Anti-Money Laundering",
    "KYB": "Know Your Business",
    "PEP": "Politically Exposed Person",
    "CDD": "Customer Due Diligence",
    "EDD": "Enhanced Due Diligence",
    "IFSC": "Indian Financial System Code",
    "SWIFT": "Society for Worldwide Interbank Financial Telecommunication",
    "IBAN": "International Bank Account Number",
    "BSB": "Bank State Branch",
    "ABN": "Australian Business Number",
    "ACN": "Australian Company Number",
    "TFN": "Tax File Number",
    "NAB": "National Australia Bank",
    "ANZ": "Australia and New Zealand Banking Group",
    "RBA": "Reserve Bank of Australia",
    "ASIC": "Australian Securities and Investments Commission",
    "AUSTRAC": "Australian Transaction Reports and Analysis Centre",
    "OTP": "One Time Password",
    "PIN": "Personal Identification Number",
    "CVV": "Card Verification Value",
    "BPAY": "Bill Payment Service",
    "EFTPOS": "Electronic Funds Transfer at Point of Sale",
    "ATM": "Automated Teller Machine",
    "EFT": "Electronic Funds Transfer",
    "RTGS": "Real Time Gross Settlement",
    "TTS": "Text To Speech",
    "IVR": "Interactive Voice Response",
    "SMS": "Short Message Service",
    "API": "Application Programming Interface",
    "SLA": "Service Level Agreement",
    "KPI": "Key Performance Indicator",
    "USD": "US dollars",
    "AUD": "Australian dollars",
    "FX": "Foreign Exchange",
    "APR": "Annual Percentage Rate",
    "p.a.": "per annum",
    "p/a": "per annum",
    "AU": "Australia",
    "AU/NZ": "Australia and New Zealand",
    "V": "versus",
    "vs": "versus",
    "i.e.": "that is",
    "e.g.": "for example",
}

_ABBREVIATIONS_CI: Dict[str, str] = {k.upper(): v for k, v in _ABBREVIATIONS.items()}


def expand_abbreviations(text: str) -> str:
    """Replace known BFSI abbreviations with their expanded forms."""
    if not text or not isinstance(text, str):
        logger.warning("Input text is empty or not a string")
        return text

    def repl(m: Match) -> str:
        original = m.group(0)
        replacement = _ABBREVIATIONS_CI.get(original.upper())
        if not replacement:
            return original
        if original.isupper():
            out = replacement.upper()
        elif original.islower():
            out = replacement.lower()
        elif original.istitle() or (len(original) > 0 and original[0].isupper()):
            out = replacement.title()
        else:
            out = replacement
        logger.info(f"expand_abbreviations: '{original}' → '{out}'")
        return out

    if not _ABBREVIATIONS:
        logger.warning("Abbreviation dictionary is empty")
        return text

    keys_sorted = sorted(_ABBREVIATIONS.keys(), key=len, reverse=True)
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in keys_sorted) + r")\b",
        flags=re.IGNORECASE,
    )
    result = pattern.sub(repl, text)
    logger.info(f"expand_abbreviations: done (input {len(text)} chars → output {len(result)} chars)")
    return result


def add_abbreviation(short: str, expanded: str) -> None:
    """Register a new abbreviation at runtime."""
    _ABBREVIATIONS[short.upper()] = expanded
    _ABBREVIATIONS_CI[short.upper()] = expanded
    logger.info(f"Registered abbreviation: {short} -> {expanded}")


def get_abbreviations() -> Dict[str, str]:
    """Return current abbreviation dictionary for inspection."""
    return _ABBREVIATIONS.copy()
