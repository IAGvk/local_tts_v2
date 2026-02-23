# ADR-003: Chained BFSI Text Normalisation Pipeline

- **Status:** Accepted
- **Date:** 2026-02-23
- **Authors:** BFSI AI Team

---

## Context and Problem Statement

Raw text from BFSI contact-centre systems contains domain-specific patterns that neural TTS models handle poorly or incorrectly:

| Raw input | TTS without normalisation | Correct output |
|-----------|--------------------------|----------------|
| `"OTP is 482916"` | "four hundred eighty two thousand nine hundred sixteen" | "four eight two nine one six" |
| `"EMI of ₹12,500"` | "twelve thousand five hundred" (rupee symbol skipped) | "EMI of twelve thousand five hundred rupees" |
| `"KYC pending"` | "ki-ick pending" (acronym mispronounced) | "Know Your Customer pending" |
| `"A/c no. 00123456"` | "a slash c no zero zero one two three four five six" | "account number zero zero one two three four five six" |

The normalisation must run **before** synthesis and be **pluggable** (different verticals may need different rules).

---

## Decision Drivers

* **OTP masking**: 6-digit sequences must be digit-by-digit, not as a full number.
* **Currency**: `₹`, `Rs.`, `INR` all need expansion to "rupees".
* **Domain abbreviations**: BFSI-specific acronyms (`KYC`, `EMI`, `NPA`, `NACH`) must expand correctly.
* **Pluggability**: A future retail adapter might need different rules — the `NormalizerPort` lets us swap.
* **Testability**: Normalisation logic must be testable without any TTS model.

---

## Considered Options

* **Option A — Custom chained normaliser (current implementation)**
* **Option B — `num2words` + custom regex post-processing**
* **Option C — LLM-based pre-processing (GPT-4 / Gemma)**

---

## Decision Outcome

Chosen option: **Option A — custom chained normaliser** using `BFSINormalizerAdapter`, which calls:

1. `expand_abbreviations(text)` — abbreviation dictionary lookup
2. `expand_numbers_in_text(text)` — number formatter with OTP-aware regex

### Consequences

* **Good**: Fully deterministic and testable — no LLM latency or cost.
* **Good**: OTP masking implemented as a special-case regex (`_OTP_RE = r'\b\d{4,8}\b'`) applied *before* `num2words` — the critical v1 bug fix.
* **Good**: New BFSI terms added in `domain_phrases.py` without touching normaliser logic.
* **Bad**: Hand-crafted rules — new numeric patterns need explicit test cases.
* **Bad**: Hindi/English code-switched text not covered — deferred to FishSpeech migration.

---

## OTP bug history (v1 → v2)

The v1 `NumberFormatter` applied `num2words` first, then tried to mask OTPs — by then `482916` had already become `"four hundred eighty two thousand..."` and the OTP regex found nothing.

**v2 fix** in `number_formatter.py`:
```python
# Step 1: mask OTPs BEFORE num2words expansion
text = _OTP_RE.sub(lambda m: _spell_digits(m.group()), text)
# Step 2: then expand remaining numbers
text = _NUM_RE.sub(lambda m: _convert_number(m.group()), text)
```

Test coverage in `test_tts_service.py::TestNormalisationIsApplied::test_otp_text_is_normalised`.

---

## Pros and Cons of the Options

### Option A — Custom chained normaliser

* **Pro**: Zero latency, zero external API calls.
* **Pro**: Rules are code-reviewed and version-controlled.
* **Con**: Requires manual maintenance as new BFSI terms emerge.

### Option B — `num2words` only

* **Pro**: Library-maintained number handling.
* **Con**: No OTP awareness, no domain abbreviations, no currency symbols.

### Option C — LLM pre-processing

* **Pro**: Handles arbitrary text without rule maintenance.
* **Con**: Adds 200-500 ms latency per utterance — unacceptable for real-time IVR.
* **Con**: Non-deterministic — same input may produce different outputs across calls.
* **Con**: Data privacy: raw financial text would leave the boundary.
