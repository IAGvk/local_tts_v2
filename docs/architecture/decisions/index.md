# Architecture Decision Records

This directory contains the **Architecture Decision Records (ADRs)** for `local_tts_v2`, following the [MADR](https://adr.github.io/madr/) (Markdown Architectural Decision Records) format.

ADRs capture **why** a decision was made, not just what was decided. They are the primary document for knowledge transfer and ownership handover.

---

## Decision log

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](001-hexagonal-architecture.md) | Hexagonal (Ports & Adapters) Architecture | Accepted | 2026-02-23 |
| [ADR-002](002-coqui-adapter-strategy.md) | Coqui VITS as Primary TTS Backend | Accepted | 2026-02-23 |
| [ADR-003](003-bfsi-text-normalisation.md) | Chained BFSI Text Normalisation Pipeline | Accepted | 2026-02-23 |

---

## ADR status lifecycle

```
proposed → accepted → deprecated
                    ↘ superseded by ADR-XXX
```

## How to write a new ADR

1. Copy the template below to `docs/architecture/decisions/NNN-short-title.md`
2. Fill in all sections — especially **Decision Drivers** and **Pros and Cons**
3. Add a row to the table above
4. Submit as a PR — ADRs are reviewed like code

### Template

```markdown
# ADR-NNN: Title

- **Status:** proposed
- **Date:** YYYY-MM-DD
- **Authors:** @handle

## Context and Problem Statement

What is the problem or architectural question that led to this decision?

## Decision Drivers

* Driver 1
* Driver 2

## Considered Options

* Option A
* Option B

## Decision Outcome

Chosen option: **Option A**, because ...

### Consequences

* Good: ...
* Bad: ...

## Pros and Cons of the Options

### Option A
* Pro: ...
* Con: ...

### Option B
* Pro: ...
* Con: ...
```
