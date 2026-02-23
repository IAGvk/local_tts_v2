"""BFSI domain-specific phrase detection and classification."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_DOMAIN_PHRASES: Dict[str, List[str]] = {
    "fraud_alerts": [
        "fraud alert", "suspicious activity", "suspicious transaction",
        "unauthorised access", "account compromised", "unusual activity detected",
        "potential fraud", "fraudulent transaction",
    ],
    "account_actions": [
        "account locked", "account closed", "account suspended",
        "account frozen", "account cancelled", "account deactivated", "account restricted",
    ],
    "compliance_notices": [
        "please confirm", "verify your identity", "update your details",
        "review your account", "check your balance", "confirm your address", "update your contact",
    ],
    "transaction_terms": [
        "chargeback", "refund", "reversal", "pending transaction",
        "declined", "failed transaction", "cancelled transaction",
    ],
    "security_terms": [
        "account number", "card number", "one time password",
        "security code", "pin code", "password reset", "two factor authentication",
    ],
    "product_names": [
        "savings account", "transaction account", "home loan", "personal loan",
        "credit card", "debit card", "investment account", "superannuation",
    ],
    "regulatory_phrases": [
        "this call may be recorded", "for quality and compliance",
        "privacy notice", "terms and conditions", "financial advice",
        "product disclosure", "financial services guide",
    ],
}

_ALL_PHRASES: List[str] = [p for phrases in _DOMAIN_PHRASES.values() for p in phrases]


def find_domain_phrases(text: str) -> List[str]:
    """Find domain-specific phrases present in text."""
    if not text or not isinstance(text, str):
        return []
    lower = text.lower()
    found = [p for p in _ALL_PHRASES if p in lower]
    logger.debug(f"Found {len(found)} domain phrases")
    return found


def find_phrases_by_category(text: str, category: str) -> List[str]:
    """Find phrases in a specific category."""
    if category not in _DOMAIN_PHRASES:
        raise ValueError(f"Category '{category}' not found. Available: {list(_DOMAIN_PHRASES)}")
    if not text or not isinstance(text, str):
        return []
    lower = text.lower()
    return [p for p in _DOMAIN_PHRASES[category] if p in lower]


def classify_phrase(phrase: str) -> Optional[str]:
    """Return category name for a known phrase, or None."""
    phrase_lower = phrase.lower()
    for category, phrases in _DOMAIN_PHRASES.items():
        if phrase_lower in phrases:
            return category
    return None


def add_domain_phrase(category: str, phrase: str) -> None:
    """Register a new domain phrase at runtime."""
    if category not in _DOMAIN_PHRASES:
        raise ValueError(f"Category '{category}' not found.")
    phrase_lower = phrase.lower()
    if phrase_lower not in _DOMAIN_PHRASES[category]:
        _DOMAIN_PHRASES[category].append(phrase_lower)
        _ALL_PHRASES.append(phrase_lower)
        logger.info(f"Registered domain phrase: '{phrase_lower}' → '{category}'")


def list_categories() -> List[str]:
    return list(_DOMAIN_PHRASES.keys())
