# Troubleshooting

---

## Import errors

### `ModuleNotFoundError: No module named 'tts_v2'`

The package is not installed in the active environment.

```bash
# Install editable
pip install -e /path/to/local_tts_v2

# Verify
python -c "import tts_v2; print(tts_v2.__version__)"
```

---

### `ModuleNotFoundError: No module named 'TTS'`

Coqui TTS is not installed. The package is an optional dependency (only `CoquiSynthesizerAdapter` needs it).

```bash
pip install coqui-tts
```

If you only need tests/normalisation (no synthesis), use `MockSynthesizerAdapter` instead.

---

### `RuntimeError: espeak not found`

`espeak-ng` is not installed. Coqui phonemizer requires it.

```bash
# macOS
brew install espeak-ng

# Ubuntu/Debian
sudo apt install espeak-ng

# Verify
espeak-ng --version
```

---

## Synthesis quality

### OTP being read as a full number

The text normaliser is not running, or the OTP regex is not matching.

```python
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
n = BFSINormalizerAdapter()
print(n.normalize("Your OTP is 482916"))
# Should print: "Your OTP is four eight two nine one six"
```

If the output is wrong, check `number_formatter.py` — `_OTP_RE` must be applied **before** `_NUM_RE`.

---

### Currency symbol dropped (`₹` ignored)

The `₹` (Unicode U+20B9) must be in the abbreviation/currency lookup table in `number_formatter.py`. Add it if missing:

```python
_CURRENCY_MAP = {
    "₹": "rupees",
    "Rs.": "rupees",
    "INR": "rupees",
    # ...
}
```

---

### Robotic or unnatural synthesis

- Try a different VCTK speaker ID in `AGENT_REGISTRY` (all 54 are available).
- Verify the text is fully normalised — raw numbers and abbreviations degrade quality.
- Check `result.rtf` — RTF > 0.5 on CPU is normal; for real-time use, enable GPU.

---

## Device / GPU issues

### `RuntimeError: isin is not currently supported on the MPS backend`

The `apply_transformers_shim()` was not called before Coqui imported `transformers`. This should be automatic in `CoquiSynthesizerAdapter.__init__`, but can happen if you import `TTS` directly before the adapter.

**Fix:** Always instantiate `CoquiSynthesizerAdapter` (not `TTS` directly) — it applies the shim first.

---

### Synthesis runs on CPU despite `use_gpu=True`

Check `resolve_device()` output:

```python
from tts_v2.shared.device_utils import resolve_device
print(resolve_device(preferred=None, use_gpu=True))
# Prints: "mps", "cuda", or "cpu"
```

If it prints `cpu` unexpectedly:
- **MPS**: `import torch; print(torch.backends.mps.is_available())` — requires macOS 12.3+, Xcode CLT
- **CUDA**: `import torch; print(torch.cuda.is_available())` — check driver version

---

## Documentation site

### `mkdocs build` fails with `ModuleNotFoundError`

`mkdocstrings` can't import the package to read docstrings.

```bash
# Install the package first (no-deps is fine for docs build)
pip install -e . --no-deps
pip install -r requirements-docs.txt
mkdocs build
```

### Mermaid diagrams not rendering

Mermaid is rendered client-side by Material theme. Check that JavaScript is not blocked in your browser. In the static `site/` build, diagrams render fine.

---

## Tests

### `pytest: command not found`

```bash
pip install pytest
# or use the full path:
/path/to/.venv/bin/python -m pytest tests/ -v
```

### Tests fail after adding a new persona

Run `TestDomainIntegrity::test_all_registered_personas_are_valid` specifically:

```bash
pytest tests/test_tts_service.py::TestDomainIntegrity -v
```

This test iterates all `AGENT_REGISTRY` entries and calls `synthesize()` via `MockSynthesizerAdapter` — catches missing fields or malformed `Speaker` objects.
