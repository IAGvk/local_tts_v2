# Getting Started

This guide takes you from zero to a synthesised `.wav` file in under 5 minutes.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Tested on 3.13 |
| espeak-ng | any | `brew install espeak-ng` (macOS) |
| torch | ≥ 2.0 | CPU-only works; GPU optional |

---

## 1. Install

```bash
# Clone the repo
git clone https://github.com/your-org/local_tts_v2.git
cd local_tts_v2

# Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# Install the package (editable)
pip install -e .
```

---

## 2. Wire the service

The service takes four injected adapters — swap any one without touching business logic:

```python
from tts_v2.service.tts_service import TTSService
from tts_v2.adapters.synthesizer.coqui_adapter import CoquiSynthesizerAdapter
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
from tts_v2.adapters.audio_sink.file_sink_adapter import FileSinkAdapter
from tts_v2.adapters.audit.noop_audit_adapter import NoOpAuditAdapter

service = TTSService(
    synthesizer=CoquiSynthesizerAdapter(use_gpu=True),  # (1)
    normalizer=BFSINormalizerAdapter(),                 # (2)
    audio_sink=FileSinkAdapter(),                       # (3)
    audit=NoOpAuditAdapter(),                           # (4)
)
```

1. GPU resolves as: MPS → CUDA → CPU automatically.
2. Expands OTPs, currency, BFSI abbreviations before synthesis.
3. Writes `.wav` files to the path you specify in `speak()`.
4. Replace with `FileAuditAdapter("audit.jsonl")` in production.

---

## 3. Synthesise

```python
result = service.speak(
    text="Your OTP for net banking is 482916. Please do not share this with anyone.",
    persona="professional_male",
    output_path="outputs/otp_alert.wav",
)

print(f"Saved to: {result.output_path}")
print(f"RTF: {result.rtf:.3f}")          # Real-Time Factor
print(f"Duration: {result.duration_s:.2f}s")
```

The text normaliser will automatically mask the OTP (`four eight two nine one six`) before synthesis.

---

## 4. Run without saving to disk

Omit `output_path` and inspect the raw `AudioChunk`:

```python
result = service.speak(
    text="Welcome to HDFC Bank. How may I assist you today?",
    persona="friendly_female",
)

chunk = result.audio_chunk   # numpy float32 array
print(chunk.samples.shape, chunk.sample_rate)
```

---

## 5. BFSI personas

Four personas are registered by default:

| Persona key | Description | Speaker ID (VCTK) |
|---|---|---|
| `professional_male` | Formal, authoritative | p225 |
| `friendly_female` | Warm, approachable | p226 |
| `neutral_male` | Neutral IVR tone | p227 |
| `professional_female` | Clear, measured | p228 |

Add custom personas in `domain/voice.py`. See [Adding a BFSI Persona](guides/adding-a-persona.md).

---

## 6. Run the test suite

```bash
pytest tests/ -v
# → 20 passed in 0.07s  (no GPU needed)
```

---

## 7. Browse the live docs

```bash
pip install -r requirements-docs.txt
mkdocs serve
# → Serving on http://127.0.0.1:8000
```

---

## Next steps

- [Architecture Overview](architecture/overview.md) — understand the hexagonal structure
- [Adding a TTS Adapter](guides/adding-a-tts-adapter.md) — swap to F5-TTS
- [API Reference](api/service.md) — full `TTSService` signature
