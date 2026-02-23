# Onboarding Guide

Welcome to `local_tts_v2`. This guide gets a new engineer productive in one day.

---

## Day 0 — Before your first session

Ask the outgoing owner to send you:

- [ ] Access to the Git repository
- [ ] The `~/.local/share/tts/` model cache (or instructions to download)
- [ ] Any `.env` / config files not committed to git
- [ ] Access to the audit log location if production is running

---

## Day 1 — Morning: codebase orientation (2 hours)

### 1. Clone and install

```bash
git clone https://github.com/your-org/local_tts_v2.git
cd local_tts_v2
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Run the tests — they pass with no GPU

```bash
pytest tests/ -v
# → 20 passed in 0.07s
```

This is your first confidence signal. If anything fails, see [Troubleshooting](../operations/troubleshooting.md).

### 3. Read the architecture in order

1. [Architecture Overview](../architecture/overview.md) — 10 minutes. Understand the hexagonal diagram.
2. [Domain Layer](../architecture/domain.md) — 5 minutes. `Speaker`, `AudioChunk`, `SynthesisRequest`.
3. [Ports](../architecture/ports.md) — 5 minutes. The 5 Protocol interfaces.
4. Open `src/tts_v2/service/tts_service.py` and read the `speak()` method — ~50 lines, no framework imports.

### 4. The one rule to internalise

> **`service/tts_service.py` must never import from `torch`, `TTS`, `soundfile`, or `adapters/`.**  
> If you find yourself adding such an import, put the logic in an adapter instead.

---

## Day 1 — Afternoon: hands-on (2 hours)

### 5. Run the notebook

Open `notebooks/quick_test_v2.ipynb` in Jupyter and run all cells. This exercises the full pipeline with the real Coqui model. Expected output: 3 `.wav` files in `outputs/`.

### 6. Make a change and prove it works

Add a new BFSI persona following [Adding a BFSI Persona](../guides/adding-a-persona.md). Run `pytest` — `TestDomainIntegrity` will automatically validate your new entry.

### 7. Read the ADRs

Read all three ADRs in [Architecture Decisions](../architecture/decisions/index.md). They explain *why* the codebase looks the way it does — especially:

- Why `TTSService` has zero framework imports (ADR-001)
- Why we use Coqui and the MPS shim (ADR-002)
- Why OTP masking happens before `num2words` (ADR-003, the v1 bug history)

---

## Key mental models

### "Ports & Adapters" in one sentence

The service layer talks to interfaces (`ports/`). Real implementations (`adapters/`) plug in at runtime. Tests plug in mocks. Neither the service nor the tests ever know which one they got.

### How to find any piece of code

| Question | Where to look |
|----------|--------------|
| "What is a Speaker?" | `src/tts_v2/domain/voice.py` |
| "How does synthesis work end-to-end?" | `src/tts_v2/service/tts_service.py` → `speak()` |
| "Where does torch live?" | `src/tts_v2/adapters/synthesizer/coqui_adapter.py` only |
| "How is ₹12,500 normalised?" | `src/tts_v2/text_normalization/number_formatter.py` |
| "Why was this architectural decision made?" | `docs/architecture/decisions/` |

### The dependency rule (visualised)

```
domain/     ← no imports from anywhere in the package
  ↑
ports/      ← imports from domain/ only
  ↑           ↑
service/    adapters/    ← both import ports/ and domain/
```

Arrows = "depends on". Nothing in `domain/` depends on anything outside `domain/`.

---

## Glossary

| Term | Meaning in this codebase |
|------|-------------------------|
| **Persona** | A named voice identity (e.g. `"professional_male"`) with a backend speaker ID |
| **Speaker** | The domain value object holding persona + `speaker_id` + description |
| **Port** | A `typing.Protocol` that defines what an adapter must implement |
| **Adapter** | A concrete class that implements a Port (lives in `adapters/`) |
| **AudioChunk** | A synthesised audio segment: numpy float32 array + sample rate |
| **RTF** | Real-Time Factor — synthesis time ÷ audio duration. RTF < 1.0 = faster than real-time |
| **OTP masking** | Converting `"482916"` → `"four eight two nine one six"` (digit-by-digit) |
| **MPS shim** | `apply_transformers_shim()` — patches `torch.Tensor.isin` for Apple Silicon |
| **BFSI** | Banking, Financial Services and Insurance — the domain this system is built for |

---

## Who to ask

| Topic | Contact |
|-------|---------|
| Architecture / ADR decisions | See `git log --follow docs/architecture/decisions/` for authors |
| Coqui model weights location | See [Runbook §2](../operations/runbook.md) |
| BFSI domain rules | See [Ownership Transfer](ownership-transfer.md) |
