# Testing

---

## Philosophy

The test suite is built around one principle: **the core business logic must be testable without any GPU, model weights, or `torch` installation.**

This is enforced structurally by the hexagonal architecture — `TTSService` only imports from `domain.*` and `ports.*`, so `MockSynthesizerAdapter` (which returns silence) is a complete drop-in for production synthesis.

---

## Running the tests

```bash
# All tests — no GPU required
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/tts_v2 --cov-report=term-missing

# Single test class
pytest tests/test_tts_service.py::TestNormalisationIsApplied -v
```

Expected output: **20 passed in ~0.07 s**

---

## Test structure

```
tests/
├── conftest.py            # Fixtures: mock_service, NullSinkAdapter
└── test_tts_service.py    # 20 tests across 6 classes
```

### Test classes

| Class | What it tests |
|-------|--------------|
| `TestTTSServiceWiring` | Service initialises, `repr()` includes adapter names |
| `TestSpeakHappyPath` | Returns correct `SynthesisResult`, chunk is float32, duration correct |
| `TestNormalisationIsApplied` | Raw text is normalised; OTP masking works |
| `TestAuditEvents` | Audit receives event dict with expected keys and non-negative RTF |
| `TestValidation` | Empty and whitespace-only text raises `ValueError` |
| `TestDomainIntegrity` | All registry personas are valid; unknown persona falls back to default |

---

## Key fixtures (`conftest.py`)

### `mock_service`

```python
@pytest.fixture
def mock_service() -> TTSService:
    return TTSService(
        synthesizer=MockSynthesizerAdapter(),   # 1s silence, no GPU
        normalizer=BFSINormalizerAdapter(),     # real normaliser
        audio_sink=NullSinkAdapter(),           # records path, no disk write
        audit=NoOpAuditAdapter(),              # swallows events
    )
```

Notice that `BFSINormalizerAdapter` is **real** in tests — this means normalisation bugs are caught without needing a live TTS model.

### `NullSinkAdapter`

A local fixture (not a production adapter) that records the last `destination` passed to `write()` without touching the file system:

```python
class NullSinkAdapter:
    last_destination: Optional[str] = None

    def write(self, chunk: AudioChunk, destination: str) -> str:
        self.last_destination = destination
        return destination
```

---

## Writing a new test

```python
class TestMyNewFeature:
    def test_something(self, mock_service: TTSService) -> None:
        result = mock_service.speak(
            text="Your loan application has been approved.",
            persona="professional_female",
        )
        assert result.audio_chunk is not None
        assert result.audio_chunk.samples.dtype == np.float32
```

- Always use `mock_service` fixture — never instantiate `CoquiSynthesizerAdapter` in unit tests.
- Tests that require a real model go in `tests/integration/` (not yet created) and are skipped in CI.

---

## Testing a new adapter

When writing a new adapter (e.g. `F5SynthesizerAdapter`), add a structural check that doesn't require the model:

```python
def test_f5_adapter_has_required_methods():
    """Structural check — verifies Protocol compliance without instantiation."""
    assert callable(getattr(F5SynthesizerAdapter, "synthesize", None))
    assert callable(getattr(F5SynthesizerAdapter, "get_speakers", None))
```

For integration tests that load actual weights, use `pytest.mark.skipif`:

```python
@pytest.mark.skipif(
    not Path("models/f5-tts").exists(),
    reason="F5-TTS model weights not present",
)
def test_f5_produces_audio():
    ...
```

---

## CI notes

The GitHub Actions docs workflow (`pip install -e . --no-deps`) installs the package without heavy dependencies like `torch` or `coqui-tts`. The test suite works the same way because `MockSynthesizerAdapter` requires only `numpy`.

To run the full integration suite locally:

```bash
pytest tests/ -v -m "not skip"
```
