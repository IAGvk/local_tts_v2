# Ports

Ports are the **boundary of the hexagon**. They are `typing.Protocol` interfaces — structural (duck-typed), not nominal. Any object that satisfies the method signatures is a valid adapter, regardless of inheritance.

All ports are decorated with `@runtime_checkable` so you can use `isinstance(obj, SynthesizerPort)` in guards.

---

## SynthesizerPort

`src/tts_v2/ports/synthesizer_port.py`

```python
class SynthesizerPort(Protocol):
    def synthesize(self, request: SynthesisRequest) -> AudioChunk: ...
    def get_speakers(self) -> List[str]: ...
```

| Method | Contract |
|--------|----------|
| `synthesize(request)` | Must return an `AudioChunk` with `float32` samples. Raise `RuntimeError` on synthesis failure, not `None`. |
| `get_speakers()` | Returns backend-specific speaker IDs (e.g. VCTK `["p225", "p226", ...]`). Used for discovery only. |

**Current implementations:** `CoquiSynthesizerAdapter`, `MockSynthesizerAdapter`

---

## VocoderPort

`src/tts_v2/ports/vocoder_port.py`

```python
class VocoderPort(Protocol):
    def vocode(self, mel: np.ndarray) -> np.ndarray: ...
    def is_passthrough(self) -> bool: ...
```

| Method | Contract |
|--------|----------|
| `vocode(mel)` | Converts a mel-spectrogram `(n_mels, T)` to a waveform `(N,)`. |
| `is_passthrough()` | Returns `True` if no conversion occurs (current production path with end-to-end Coqui). |

!!! note "Current production path"
    `PassthroughVocoderAdapter.is_passthrough()` returns `True`. This port is reserved for a future standalone HiFiGAN or BigVGAN vocoder when mel-spectrogram outputs are needed separately (e.g. streaming pipelines).

**Current implementations:** `PassthroughVocoderAdapter`

---

## NormalizerPort

`src/tts_v2/ports/normalizer_port.py`

```python
class NormalizerPort(Protocol):
    def normalize(self, text: str) -> str: ...
```

| Method | Contract |
|--------|----------|
| `normalize(text)` | Returns a string safe for TTS synthesis — no raw numbers, no abbreviations, OTPs masked. Must be idempotent. |

**Current implementations:** `BFSINormalizerAdapter`

---

## AudioSinkPort

`src/tts_v2/ports/audio_sink_port.py`

```python
class AudioSinkPort(Protocol):
    def write(self, chunk: AudioChunk, destination: str) -> str: ...
```

| Method | Contract |
|--------|----------|
| `write(chunk, destination)` | Writes audio to `destination` and returns the **resolved absolute path**. Must not modify `chunk`. |

**Current implementations:** `FileSinkAdapter`, `NullSinkAdapter` (test fixture)

---

## AuditPort

`src/tts_v2/ports/audit_port.py`

```python
class AuditPort(Protocol):
    def log_synthesis(self, event: Dict[str, Any]) -> None: ...
```

| Method | Contract |
|--------|----------|
| `log_synthesis(event)` | Receives a dict with keys: `text_length`, `persona`, `duration_s`, `rtf`, `output_path`, `timestamp`. Must not raise. |

**Current implementations:** `NoOpAuditAdapter` (tests), `FileAuditAdapter` (production JSONL)

---

## Adding a new port

If you need a new integration point (e.g. a streaming output port, or a speech-rate controller):

1. Create `src/tts_v2/ports/my_new_port.py` — define a `Protocol` class.
2. Add the port as a constructor parameter to `TTSService.__init__()` (with a sensible default).
3. Create an adapter in `src/tts_v2/adapters/`.
4. Write tests with a `MockMyNewAdapter` in `conftest.py`.

See [Adding a TTS Adapter](../guides/adding-a-tts-adapter.md) for the full pattern.
