# ADR-002: Coqui VITS as Primary TTS Backend

- **Status:** Accepted
- **Date:** 2026-02-23
- **Authors:** BFSI AI Team
- **Review date:** 2026-06-01 (reassess against F5-TTS / FishSpeech readiness)

---

## Context and Problem Statement

The primary synthesizer adapter must produce natural-sounding English speech for BFSI contact-centre automation. The system runs offline (no cloud TTS API calls) for data privacy compliance. We need to choose a specific model and vendor for the initial `SynthesizerPort` implementation.

---

## Decision Drivers

* **Offline / on-premise**: All audio is generated locally — no PII sent to cloud APIs (DPDPA requirement).
* **VCTK multi-speaker**: Multiple voices needed for different BFSI agent personas.
* **MPS support**: Apple Silicon M-series development machines must be usable.
* **Licence**: Model weights must be commercially usable.
* **Quality**: Intelligible speech for financial terms, numbers, and OTPs.

---

## Considered Options

* **Option A — Coqui TTS (VITS, `tts_models/en/vctk/vits`)**
* **Option B — ESPnet2 VITS**
* **Option C — F5-TTS / E2 TTS (flow-matching)**
* **Option D — Cloud TTS API (Google, Azure)**

---

## Decision Outcome

Chosen option: **Option A — Coqui VITS**, because it is the most mature offline Python TTS library with multi-speaker support, reasonable quality for BFSI utterances, and an active community. The hexagonal adapter pattern means this decision can be revisited independently of all other code.

### Consequences

* **Good**: `pip install coqui-tts` — single dependency, ~250 MB weights cached locally.
* **Good**: 54 VCTK speakers available via `speaker_id` — future persona expansion is easy.
* **Good**: Model runs on CPU, CUDA, and MPS (Apple Silicon) with the `apply_transformers_shim()` fix.
* **Bad**: Coqui `TTS.vocoder.api` was removed in recent versions — the standalone vocoder path is blocked. Documented in `PassthroughVocoderAdapter.is_passthrough()`.
* **Bad**: Coqui VITS quality is slightly robotic on Hindi/English code-switched text — FishSpeech is the planned replacement for that use case.

---

## MPS compatibility fix

Coqui uses `transformers` which calls `torch.Tensor.isin()` — a function that is not MPS-friendly. The `apply_transformers_shim()` function in `shared/device_utils.py` patches `torch.Tensor.isin` to fall back to CPU before any Coqui import.

This fix was validated on: MacBook Pro M2 Max (MPS), `torch >= 2.0`.

---

## Planned migration path

```
[2026 Q1] Coqui VITS (current)
     ↓
[2026 Q3] F5SynthesizerAdapter — expressive speech, emotion tags
     ↓
[2026 Q4] FishSpeechAdapter — Hindi/English code-switching
```

Each migration requires only a new file in `adapters/synthesizer/` and a `speaker_id` update in `AGENT_REGISTRY`. `TTSService` remains unchanged.
