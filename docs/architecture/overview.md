# Architecture Overview

`local_tts_v2` uses the **Hexagonal (Ports & Adapters)** pattern described by Alistair Cockburn (2005). The core idea: the business domain sits at the centre; all external dependencies (TTS models, file systems, audit sinks) attach at the perimeter via swappable adapters.

---

## C4 Level 1 — System Context

```mermaid
C4Context
    title System Context: local_tts_v2

    Person(dev, "Engineer / Script", "Calls service.speak()")
    Person(ivr, "IVR Platform", "Streams audio to telephony")

    System(tts, "local_tts_v2", "Synthesises BFSI speech from text")

    System_Ext(coqui, "Coqui VITS Model", "Pre-trained neural TTS (local .pth)")
    System_Ext(fs, "File System", "Writes .wav output files")
    System_Ext(audit, "Audit Log", "JSONL file or future SIEM")

    Rel(dev, tts, "service.speak(text, persona)")
    Rel(ivr, tts, "service.speak() → AudioChunk")
    Rel(tts, coqui, "CoquiSynthesizerAdapter")
    Rel(tts, fs, "FileSinkAdapter")
    Rel(tts, audit, "FileAuditAdapter")
```

---

## C4 Level 2 — Container / Package Decomposition

```mermaid
graph TB
    subgraph repo["local_tts_v2 (src/tts_v2/)"]
        direction TB

        subgraph domain["domain/"]
            V["voice.py\nSpeaker · AGENT_REGISTRY"]
            A["audio.py\nAudioChunk · SynthesisRequest\nSynthesisResult"]
        end

        subgraph ports["ports/"]
            P1["synthesizer_port.py"]
            P2["normalizer_port.py"]
            P3["audio_sink_port.py"]
            P4["audit_port.py"]
            P5["vocoder_port.py"]
        end

        subgraph service["service/"]
            SVC["tts_service.py\nTTSService"]
        end

        subgraph shared["shared/"]
            DU["device_utils.py"]
            AU["audio_utils.py"]
        end

        subgraph norm["text_normalization/"]
            NF["number_formatter.py"]
            AB["abbreviation_handler.py"]
            DP["domain_phrases.py"]
            SH["synthetic_hooks.py"]
        end

        subgraph adapters["adapters/"]
            COQ["synthesizer/coqui_adapter.py"]
            MOCK["synthesizer/mock_adapter.py"]
            PASS["vocoder/passthrough_adapter.py"]
            BFSI["normalizer/bfsi_normalizer_adapter.py"]
            FILE["audio_sink/file_sink_adapter.py"]
            NOOP["audit/noop_audit_adapter.py"]
            FAUD["audit/file_audit_adapter.py"]
        end
    end

    SVC -->|"reads"| domain
    SVC -->|"depends on"| ports
    adapters -->|"implements"| ports
    adapters -->|"uses"| shared
    BFSI -->|"uses"| norm
```

---

## The Hexagonal Rule

!!! danger "The Rule — enforced in code via docstring"
    **`service/tts_service.py` must NEVER import from:**
    `torch`, `torchaudio`, `TTS`, `transformers`, `soundfile`, `num2words`,
    or any module inside `adapters/`.

    Imports allowed: `domain.*`, `ports.*`, `logging`, `typing`, stdlib only.

This rule means:

- You can run every unit test without a GPU, without model weights, and without `torch` installed.
- Swapping the TTS backend is a one-file change in `adapters/synthesizer/`.
- The service is trivially testable with `MockSynthesizerAdapter`.

---

## Dependency flow

```mermaid
graph LR
    AD["adapters/"] -->|"implements"| PO["ports/"]
    SV["service/"] -->|"calls via port"| PO
    SV -->|"reads"| DO["domain/"]
    AD -->|"reads"| DO
    SH["shared/"] -.->|"utilities (no domain logic)"| AD

    style SV fill:#4a90d9,color:#fff
    style DO fill:#2ecc71,color:#fff
    style PO fill:#f39c12,color:#fff
    style AD fill:#9b59b6,color:#fff
```

**Arrows point inward only.** `domain/` has no imports from anywhere else in the package. `ports/` imports from `domain/` only. `service/` imports from `domain/` and `ports/`. `adapters/` import from `ports/`, `domain/`, and `shared/`.

---

## Call flow: `service.speak()`

```mermaid
sequenceDiagram
    participant C as Caller
    participant S as TTSService
    participant N as NormalizerPort
    participant D as domain.voice
    participant T as SynthesizerPort
    participant K as AudioSinkPort
    participant A as AuditPort

    C->>S: speak(text, persona, output_path)
    S->>S: validate (empty text → ValueError)
    S->>N: normalize(text)
    N-->>S: normalised_text
    S->>D: get_speaker(persona)
    D-->>S: Speaker value object
    S->>T: synthesize(SynthesisRequest)
    T-->>S: AudioChunk
    alt output_path provided
        S->>K: write(chunk, output_path)
        K-->>S: resolved_path
    end
    S->>A: log_synthesis(event_dict)
    S-->>C: SynthesisResult(audio_chunk|None, output_path|None, rtf, duration_s)
```
