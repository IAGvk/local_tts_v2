# Ownership Transfer Checklist

This checklist formalises the handover of `local_tts_v2` from the outgoing owner to the incoming owner. It follows the spirit of IEEE Std 1219 (Software Maintenance) and CMMI Level 2 knowledge transfer practices.

**Date of transfer:** _______________  
**Outgoing owner:** _______________  
**Incoming owner:** _______________  
**Witnessed by:** _______________

---

## Section 1 — Repository access

- [ ] Incoming owner has push access to the main branch
- [ ] Incoming owner has access to all CI/CD pipelines (GitHub Actions)
- [ ] Incoming owner has access to GitHub Pages deployment environment
- [ ] All secrets / environment variables documented and transferred (see §6)
- [ ] Branch protection rules reviewed and documented

---

## Section 2 — Development environment

- [ ] Incoming owner can clone and `pip install -e .` successfully
- [ ] `pytest tests/ -v` passes (20/20) on incoming owner's machine
- [ ] `mkdocs serve` runs and all pages render correctly
- [ ] `espeak-ng` installed on incoming owner's machine
- [ ] Coqui model cache (`~/.local/share/tts/`) present on development machine
- [ ] GPU/MPS device verified with `resolve_device()` returning expected device

---

## Section 3 — Architecture walkthrough (live session)

The outgoing owner must walk through each item with the incoming owner present. Tick only after live confirmation.

- [ ] **Hexagonal rule explained**: why `service/` has zero framework imports (ADR-001)
- [ ] **Port Protocol contracts**: walked through all 5 ports in `ports/`
- [ ] **Adapter pattern**: demonstrated adding a mock adapter in a live coding session
- [ ] **BFSI agent registry**: explained `AGENT_REGISTRY`, `DEFAULT_PERSONA`, fallback behaviour
- [ ] **Text normalisation chain**: traced OTP flow from raw text → `expand_abbreviations` → `expand_numbers_in_text` → synthesizer
- [ ] **Device resolution**: explained `apply_transformers_shim()` and why it exists (MPS isin bug)
- [ ] **Audit trail**: shown `FileAuditAdapter` output and explained what is/is not logged (PII exclusion)
- [ ] **Test fixtures**: walked through `conftest.py`, `NullSinkAdapter`, `MockSynthesizerAdapter`

---

## Section 4 — ADR review

All Architecture Decision Records reviewed and questions resolved:

- [ ] [ADR-001: Hexagonal Architecture](../architecture/decisions/001-hexagonal-architecture.md) — incoming owner understands the trade-offs and "why not layered"
- [ ] [ADR-002: Coqui Adapter Strategy](../architecture/decisions/002-coqui-adapter-strategy.md) — incoming owner knows the planned migration to F5-TTS / FishSpeech
- [ ] [ADR-003: BFSI Text Normalisation](../architecture/decisions/003-bfsi-text-normalisation.md) — incoming owner understands the OTP bug history and the fix

---

## Section 5 — Operational knowledge

- [ ] Incoming owner has read the [Runbook](../operations/runbook.md) end-to-end
- [ ] Model cache location documented: _______________
- [ ] Audit log location in production documented: _______________
- [ ] Log rotation policy documented and configured: _______________
- [ ] Known issues and workarounds transferred (see §7)
- [ ] On-call escalation path updated to incoming owner's contact

---

## Section 6 — Secrets and configuration

| Secret / Config | Location | Transferred to incoming owner |
|-----------------|----------|-------------------------------|
| (none — fully offline system) | N/A | N/A |
| Production model weights path | _______________ | ☐ |
| Audit log destination | _______________ | ☐ |
| Any CI secrets (e.g. GitHub token) | GitHub Secrets | ☐ |

---

## Section 7 — Known issues and technical debt

| Issue | Severity | Workaround | Owner |
|-------|----------|-----------|-------|
| `TTS.vocoder.api` removed in new Coqui | Low | `PassthroughVocoderAdapter` (end-to-end synthesis) | BFSI AI Team |
| Hindi/English code-switching not supported | Medium | Deferred to FishSpeech adapter (planned Q4) | BFSI AI Team |
| No REST API entrypoint | Low | Use `TTSService` directly in scripts/notebooks | BFSI AI Team |
| Audit JSONL rotates indefinitely | Low | Manual cron job needed for log rotation | _____ |

---

## Section 8 — Roadmap handover

Incoming owner confirms awareness of planned work:

- [ ] F5-TTS adapter (Q3 2026) — see [ADR-002](../architecture/decisions/002-coqui-adapter-strategy.md)
- [ ] FishSpeech adapter for Hindi/English code-switching (Q4 2026)
- [ ] REST API entrypoint (FastAPI driving adapter)
- [ ] Redis-backed `AuditPort` for distributed deployments

---

## Section 9 — Sign-off

By signing below, both parties confirm that all checked items above have been completed satisfactorily.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Outgoing owner | | | |
| Incoming owner | | | |
| Witness | | | |

---

!!! note "This document"
    Keep a completed copy of this checklist as a PDF or printed document alongside the project's compliance artefacts. The Git history of this file itself serves as a record of previous handovers.
