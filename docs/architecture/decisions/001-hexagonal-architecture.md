# ADR-001: Hexagonal (Ports & Adapters) Architecture

- **Status:** Accepted
- **Date:** 2026-02-23
- **Authors:** BFSI AI Team
- **Supersedes:** v1 layered architecture in `local_tts/`

---

## Context and Problem Statement

The v1 codebase (`local_tts/`) used a **layered architecture**: `tts_core/` contained `AcousticModel`, `VocoderModel`, and utility functions that imported directly from `torch`, `TTS`, and `soundfile`. Adding a new TTS backend (e.g. FishSpeech) required forking `acoustic_model.py`. Running any unit test required loading a ~250 MB GPU model, making CI slow and fragile.

The team needed an architecture where:
1. TTS backends can be swapped without touching business logic.
2. Tests run in < 1 second without GPU or model weights.
3. New engineers can understand the system without tracing framework call chains.
4. Compliance auditing is pluggable (today JSONL, tomorrow SIEM).

---

## Decision Drivers

* **Model replaceability**: Coqui VITS will likely be replaced by F5-TTS or FishSpeech within 12 months.
* **Testability**: Synthesis test suites must run in CI (no GPU runner available).
* **BFSI compliance**: All synthesis events must be loggable/auditable — the audit sink must be replaceable (JSONL → Kafka → SIEM) without touching synthesis logic.
* **Onboarding**: New engineers should be able to contribute an adapter without understanding the full Coqui API.

---

## Considered Options

* **Option A — Hexagonal (Ports & Adapters)**
* **Option B — Strategy Pattern in a Layered Architecture**
* **Option C — Plugin system via `importlib` entry_points**

---

## Decision Outcome

Chosen option: **Option A — Hexagonal Architecture**, because it enforces the dependency inversion rule structurally (via directory layout and import guards in docstrings) rather than relying on developer discipline.

### Consequences

* **Good**: `TTSService` has zero framework imports — any test that imports it runs instantly.
* **Good**: Swapping the TTS backend is a single new file in `adapters/synthesizer/`.
* **Good**: All ports are `typing.Protocol` — no inheritance required from adapters.
* **Bad**: Slightly more boilerplate for new contributors unfamiliar with the pattern.
* **Bad**: `domain/__init__.py` re-export surface must be kept clean (caught one bug: `SynthesisRequest` was mistakenly imported from `voice.py`).

---

## Pros and Cons of the Options

### Option A — Hexagonal Architecture

* **Pro**: The "no framework imports in service/" rule is enforced structurally.
* **Pro**: `MockSynthesizerAdapter` makes 20 tests run in 0.07 s — no GPU.
* **Pro**: Ports are `Protocol`-typed — adapters are structurally compatible, not nominally coupled.
* **Con**: Pattern is unfamiliar to engineers coming from Django/Flask/v1 layered code.

### Option B — Strategy Pattern in Layered Architecture

* **Pro**: Simpler to explain to Django-background engineers.
* **Con**: `torch` import still leaks into the service layer through the strategy interface unless carefully managed.
* **Con**: Tests still require the strategy classes to be importable, meaning `torch` must be installed.

### Option C — Plugin system via entry_points

* **Pro**: True late-binding — adapters can be distributed as separate packages.
* **Con**: Over-engineered for an internal BFSI tool at this stage.
* **Con**: Entry-point registration adds operational complexity with no benefit until the system is distributed.
