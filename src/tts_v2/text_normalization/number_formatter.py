"""Number, currency, and OTP formatting for Australian English TTS.

Provides:
- Currency amounts (AU dollars, USD)
- OTP/reference numbers (digit-by-digit)
- Numeric amounts with decimal support
- Compliance-grade deterministic formatting
"""

import logging
import re
from typing import Optional, Tuple

from num2words import num2words

logger = logging.getLogger(__name__)

# Regex for currency amounts
_CURRENCY_RE = re.compile(r"\$\s?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)")
# Regex for plain numeric amounts
_NUMBER_RE = re.compile(r"\b([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\b")
# Regex for OTP/reference codes (sequences of 4+ digits or alphanumeric)
_OTP_RE = re.compile(r"\b([0-9]{4,}|[A-Z0-9]{4,})\b")


def format_money(amount: float, currency: str = "AUD") -> str:
    """Convert numeric amount to Australian English spoken form with currency.

    Args:
        amount: Numeric amount to convert
        currency: Currency code (AUD, USD). Default AUD.

    Returns:
        Spoken form with currency (e.g., 'twelve hundred and five dollars')

    Example:
        >>> format_money(1205.50)
        'one thousand two hundred and five dollars and fifty cents'
    """
    amount_rounded = round(float(amount), 2)
    whole = int(amount_rounded)
    cents = int(round((amount_rounded - whole) * 100))

    spoken_whole = num2words(whole, to="cardinal", lang="en")

    logger.info(f"format_money: {currency} {amount_rounded} → whole={whole}, cents={cents}")

    if currency.upper() == "AUD":
        unit = "dollar" if whole == 1 else "dollars"
        if cents == 0:
            return f"{spoken_whole} {unit}"
        spoken_cents = num2words(cents, to="cardinal", lang="en")
        cent_unit = "cent" if cents == 1 else "cents"
        return f"{spoken_whole} {unit} and {spoken_cents} {cent_unit}"

    if currency.upper() == "USD":
        unit = "US dollar" if whole == 1 else "US dollars"
        if cents == 0:
            result = f"{spoken_whole} {unit}"
        else:
            spoken_cents = num2words(cents, to="cardinal", lang="en")
            cent_unit = "cent" if cents == 1 else "cents"
            result = f"{spoken_whole} {unit} and {spoken_cents} {cent_unit}"
        logger.info(f"format_money result: '{result}'")
        return result

    if cents == 0:
        result = f"{spoken_whole} {currency}"
    else:
        spoken_cents = num2words(cents, to="cardinal", lang="en")
        result = f"{spoken_whole} {currency} and {spoken_cents} cents"
    logger.info(f"format_money result: '{result}'")
    return result


def format_otp(otp: str) -> str:
    """Format OTP or reference number as individual spoken digits.

    Args:
        otp: OTP string (digits or alphanumeric)

    Returns:
        Space-separated spoken digits (e.g., 'four eight two nine one three')

    Example:
        >>> format_otp('482913')
        'four eight two nine one three'
    """
    if not otp:
        raise ValueError("OTP cannot be empty")

    spoken_parts = []
    for char in otp.upper():
        if char.isdigit():
            spoken_parts.append(num2words(int(char), to="cardinal", lang="en"))
        elif char.isalpha():
            spoken_parts.append(f"letter {char.lower()}")
        else:
            logger.warning(f"Skipping non-alphanumeric character in OTP: {char}")

    result = " ".join(spoken_parts)
    logger.info(f"format_otp: '{otp}' → '{result}'")
    return result


def _expand_decimal_part(dec_str: str) -> str:
    """Convert decimal digits to spoken form with 'point' prefix."""
    digits_spoken = " ".join(num2words(int(d), to="cardinal", lang="en") for d in dec_str)
    return f"point {digits_spoken}"


def expand_numbers_in_text(text: str, preserve_otps: bool = True) -> str:
    """Expand numeric amounts in text to spoken forms.

    Handles:
    - Currency amounts: $1,234.50 -> 'one thousand two hundred and thirty-four dollars and fifty cents'
    - OTP/reference codes: 482913 -> 'four eight two nine one three'
    - Plain numbers: 1205 -> 'one thousand two hundred and five'
    - Decimals: 123.45 -> 'one hundred and twenty-three point four five'

    Args:
        text: Input text with numeric amounts
        preserve_otps: If True, expand 4+ digit sequences digit-by-digit (OTP mode).
                       If False, convert as cardinal numbers.

    Returns:
        Text with expanded numbers
    """

    def replace_currency(m: re.Match) -> str:
        amount_str = m.group(1).replace(",", "")
        try:
            return format_money(float(amount_str))
        except Exception as e:
            logger.warning(f"Failed to convert currency {amount_str}: {e}")
            return m.group(0)

    def replace_otp_match(m: re.Match) -> str:
        num_str = m.group(1)
        if num_str.isdigit():
            expanded = format_otp(num_str)
            logger.info(f"expand_numbers_in_text: OTP '{num_str}' → '{expanded}'")
            return expanded
        return m.group(0)

    def replace_number(m: re.Match) -> str:
        num_str = m.group(1).replace(",", "")
        try:
            if "." in num_str:
                whole, dec = num_str.split(".")
                spoken_whole = num2words(int(whole), to="cardinal", lang="en")
                return f"{spoken_whole} {_expand_decimal_part(dec)}"
            else:
                return num2words(int(num_str), to="cardinal", lang="en")
        except Exception as e:
            logger.warning(f"Failed to convert number {num_str}: {e}")
            return m.group(0)

    # Replace in order: currencies first, then OTP/reference codes, then plain numbers
    original = text
    text = _CURRENCY_RE.sub(replace_currency, text)
    if preserve_otps:
        text = _OTP_RE.sub(replace_otp_match, text)
    text = _NUMBER_RE.sub(replace_number, text)

    if text != original:
        logger.info(f"expand_numbers_in_text: '{original}' → '{text}'")
    else:
        logger.info("expand_numbers_in_text: no numeric tokens found")
    return text


def normalize_phone_number(phone: str, country_code: str = "AU") -> str:
    """Format phone number for TTS reading.

    Args:
        phone: Phone number string
        country_code: Country code (AU, US, etc.)

    Returns:
        Spoken form of phone number

    Example:
        >>> normalize_phone_number("+61412345678")
        'plus six one four one two three four five six seven eight'
    """
    digits = re.sub(r"[-\s().]", "", phone)

    if country_code.upper() == "AU":
        if digits.startswith("+61"):
            digits = digits[3:]
        elif digits.startswith("61"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = digits[1:]

    result = " ".join(num2words(int(d), to="cardinal", lang="en") for d in digits if d.isdigit())
    logger.info(f"normalize_phone_number: '{phone}' → '{result}'")
    return result
