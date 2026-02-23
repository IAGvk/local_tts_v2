# Changelog

All notable changes to `local_tts_v2` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Planned
- F5-TTS adapter (`F5SynthesizerAdapter`) for expressive BFSI voices
- FishSpeech adapter with multi-lingual Hindi/English code-switching
- REST API entrypoint (FastAPI) as a driving adapter
- Redis-backed `AuditPort` adapter for distributed audit trails
- Prometheus metrics adapter

---

## [2.0.0] — 2026-02-23

### Added
- **Hexagonal (Ports & Adapters) architecture** — complete rewrite from v1 layered architecture
- `Domain` layer: `Speaker` value object (frozen dataclass), `AudioChunk`, `SynthesisRequest`, `SynthesisResult`
- `Ports` layer: 5 `@runtime_checkable` Protocol interfaces — `SynthesizerPort`, `VocoderPort`, `NormalizerPort`, `AudioSinkPort`, `AuditPort`
- `TTSService`: pure orchestration with zero framework imports; constructor-injected ports
- `CoquiSynthesizerAdapter`: Coqui VITS backend with MPS/CUDA/CPU device resolution
- `MockSynthesizerAdapter`: silence generator for tests — no GPU required
- `PassthroughVocoderAdapter`: identity vocoder (end-to-end synthesis path)
- `BFSINormalizerAdapter`: chains abbreviation expansion → number formatting
- `FileSinkAdapter`: writes `.wav` via `soundfile`
- `NoOpAuditAdapter` + `FileAuditAdapter` (JSONL append log)
- BFSI agent registry with 4 personas: `professional_male`, `friendly_female`, `neutral_male`, `professional_female`
- Text normalisation ported from v1: OTP masking fix, money formatting, domain phrase expansion
- 20 pytest tests — all pass in 0.07 s with no GPU
- MkDocs Material documentation site

### Changed
- Replaced v1 layered classes with hexagonal protocol injection
- `apply_transformers_shim()` moved to `shared.device_utils` (no longer duplicated)

### Fixed
- OTP number masking — `_OTP_RE` now correct: 6-digit sequences are masked before `num2words` expansion
- `SynthesisRequest` import corrected in `domain/__init__.py` (was pointing to `voice.py`)

---

## [1.x] — local_tts (v1)

See [`local_tts/`](../local_tts/) for the layered architecture predecessor.

[Unreleased]: https://github.com/your-org/local_tts_v2/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/your-org/local_tts_v2/releases/tag/v2.0.0
