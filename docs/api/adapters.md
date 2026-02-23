# Adapters API

Concrete implementations of the port Protocols. All framework imports (`torch`, `TTS`, `soundfile`) live exclusively in these classes.

---

## Synthesizer adapters

::: tts_v2.adapters.synthesizer.coqui_adapter.CoquiSynthesizerAdapter

::: tts_v2.adapters.synthesizer.mock_adapter.MockSynthesizerAdapter

---

## Vocoder adapters

::: tts_v2.adapters.vocoder.passthrough_adapter.PassthroughVocoderAdapter

---

## Normalizer adapters

::: tts_v2.adapters.normalizer.bfsi_normalizer_adapter.BFSINormalizerAdapter

---

## Audio sink adapters

::: tts_v2.adapters.audio_sink.file_sink_adapter.FileSinkAdapter

---

## Audit adapters

::: tts_v2.adapters.audit.noop_audit_adapter.NoOpAuditAdapter

::: tts_v2.adapters.audit.file_audit_adapter.FileAuditAdapter
