# Adding a BFSI Persona

A **persona** is a named voice identity with a backend-specific speaker ID. Adding one requires changes to a single file.

---

## All you need to change: `domain/voice.py`

Open `src/tts_v2/domain/voice.py` and add an entry to `AGENT_REGISTRY`:

```python
AGENT_REGISTRY: Dict[str, Speaker] = {
    # --- existing personas ---
    "professional_male": Speaker(
        persona="professional_male",
        speaker_id="p225",
        agent_name="Professional Banking Officer",
        description="Formal, authoritative. For account updates and compliance notices.",
    ),

    # --- add your new persona here ---
    "collections_male": Speaker(
        persona="collections_male",
        speaker_id="p243",               # (1)
        agent_name="Collections Recovery Agent",
        description="Firm but empathetic. For overdue payment reminders. "
                    "Do not use for new-customer onboarding flows.",
    ),
}
```

1. VCTK speaker IDs for Coqui: run `tts --list_models` and then `tts --model_name tts_models/en/vctk/vits --list_speaker_idxs` to browse available voices.

---

## Finding the right speaker ID

=== "Coqui VCTK"

    ```bash
    # List all 54 VCTK speakers
    source .venv/bin/activate
    python -c "
    from TTS.api import TTS
    tts = TTS(model_name='tts_models/en/vctk/vits', progress_bar=False)
    print(tts.speakers)
    "
    ```

=== "F5-TTS (future)"

    ```python
    from tts_v2.adapters.synthesizer.f5_adapter import F5SynthesizerAdapter
    adapter = F5SynthesizerAdapter(model_path="models/f5/")
    print(adapter.get_speakers())
    ```

---

## Verify with a quick synthesis

```python
from tts_v2.service.tts_service import TTSService
from tts_v2.adapters.synthesizer.coqui_adapter import CoquiSynthesizerAdapter
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
from tts_v2.adapters.audio_sink.file_sink_adapter import FileSinkAdapter
from tts_v2.adapters.audit.noop_audit_adapter import NoOpAuditAdapter

service = TTSService(
    synthesizer=CoquiSynthesizerAdapter(use_gpu=True),
    normalizer=BFSINormalizerAdapter(),
    audio_sink=FileSinkAdapter(),
    audit=NoOpAuditAdapter(),
)

result = service.speak(
    text="This is a reminder about your outstanding EMI of five thousand rupees.",
    persona="collections_male",           # ← your new persona
    output_path="outputs/collections_test.wav",
)
print(result.output_path, f"RTF={result.rtf:.2f}")
```

---

## Changing the default persona

Edit `DEFAULT_PERSONA` at the bottom of `voice.py`:

```python
DEFAULT_PERSONA = "neutral_male"   # fallback when unknown persona is passed
```

`TTSService` falls back to this when `get_speaker()` receives an unrecognised key — it logs a warning but does not raise.

---

## Checklist

- [ ] New `Speaker(...)` entry in `AGENT_REGISTRY` with a unique `persona` key
- [ ] `speaker_id` validated against the model's speaker list
- [ ] `description` field includes compliance/usage guidance (required for BFSI audit)
- [ ] Synthesis smoke test run and output reviewed
- [ ] `CHANGELOG.md` updated (personas are user-facing features)
- [ ] `TestDomainIntegrity::test_all_registered_personas_are_valid` passes (runs automatically in pytest)
