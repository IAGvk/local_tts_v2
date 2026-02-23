# Operational Runbook

**Service:** `local_tts_v2`  
**Owner:** BFSI AI Team  
**Escalation:** See [Ownership Transfer Checklist](../kt/ownership-transfer.md)

---

## 1. Service health check

```bash
# Quick smoke test — no GPU needed
cd /path/to/local_tts_v2
source .venv/bin/activate
python -m pytest tests/ -v --tb=short
# Expected: 20 passed
```

```bash
# Integration check — synthesise a test utterance (requires GPU/CPU + Coqui weights)
python -c "
from tts_v2.service.tts_service import TTSService
from tts_v2.adapters.synthesizer.coqui_adapter import CoquiSynthesizerAdapter
from tts_v2.adapters.normalizer.bfsi_normalizer_adapter import BFSINormalizerAdapter
from tts_v2.adapters.audio_sink.file_sink_adapter import FileSinkAdapter
from tts_v2.adapters.audit.noop_audit_adapter import NoOpAuditAdapter

svc = TTSService(CoquiSynthesizerAdapter(use_gpu=False), BFSINormalizerAdapter(), FileSinkAdapter(), NoOpAuditAdapter())
r = svc.speak('Health check passed.', persona='neutral_male', output_path='/tmp/health_check.wav')
print('OK — RTF:', round(r.rtf, 3))
"
```

---

## 2. First-run model download

On first execution, Coqui downloads model weights (~250 MB) to `~/.local/share/tts/`. Subsequent runs are offline.

```bash
# Pre-warm the model cache (run once per machine / container build)
python -c "from TTS.api import TTS; TTS('tts_models/en/vctk/vits', progress_bar=True)"
```

For air-gapped deployments, copy `~/.local/share/tts/` from a seeded machine.

---

## 3. Device troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `RuntimeError: isin is not currently supported on the MPS backend` | `apply_transformers_shim()` not called before Coqui import | Ensure `CoquiSynthesizerAdapter.__init__` calls it |
| `CUDA out of memory` | Batch size too large | Set `use_gpu=False` or reduce utterance length |
| Very slow synthesis (RTF > 2.0) | Running on CPU with no MPS/CUDA | Check `result.rtf`; enable GPU if available |
| `espeak not found` | `espeak-ng` not installed | `brew install espeak-ng` (macOS) / `apt install espeak-ng` |

---

## 4. Audit log management

Production audit logs are written to `logs/synthesis_audit.jsonl` (JSONL format, one record per line).

```bash
# Count synthesis events today
grep "$(date +%Y-%m-%d)" logs/synthesis_audit.jsonl | wc -l

# Average RTF over last 100 events
python -c "
import json, statistics
lines = open('logs/synthesis_audit.jsonl').readlines()[-100:]
rtfs = [json.loads(l)['rtf'] for l in lines]
print(f'Mean RTF: {statistics.mean(rtfs):.3f}')
"

# Find slow synthesis events (RTF > 1.0)
python -c "
import json
for line in open('logs/synthesis_audit.jsonl'):
    e = json.loads(line)
    if e['rtf'] > 1.0:
        print(e['timestamp'], e['persona'], f\"RTF={e['rtf']:.2f}\")
"
```

!!! note "Log rotation"
    The `FileAuditAdapter` appends indefinitely. Set up logrotate or a cron job to archive logs older than 90 days per data retention policy.

---

## 5. Dependency updates

```bash
# Check for outdated packages
pip list --outdated

# Update docs dependencies only
pip install -r requirements-docs.txt --upgrade

# Rebuild docs after update
mkdocs build --strict
```

!!! warning "Coqui version pinning"
    `coqui-tts` minor version updates sometimes change model weight file formats. Test synthesis after any Coqui upgrade using the health check above before deploying.

---

## 6. Regenerate documentation

```bash
# Serve locally with live reload
mkdocs serve

# Build static site to site/
mkdocs build --strict

# Deploy to GitHub Pages manually
mkdocs gh-deploy --force
```

CI auto-deploys on every push to `main` via `.github/workflows/docs.yml`.

---

## 7. Running tests in CI (no GPU)

```bash
# Install only test + package deps (no torch, no coqui)
pip install -e . --no-deps
pip install pytest numpy

# Run unit tests
pytest tests/ -v
```

The `MockSynthesizerAdapter` path requires only `numpy`. No `torch`, no model weights.
