# Classical Cipher Benchmark

A standardized benchmark dataset for evaluating AI-assisted classical cipher analysis tools. The benchmark pairs historical cipher manuscript images with verified transcriptions and known plaintext, enabling reproducible evaluation across three task tracks:

- **Track A — Image to Transcription**: Given a page image, produce a symbol-level transcription (HTR for cipher manuscripts)
- **Track B — Transcription to Plaintext**: Given a normalized transcription, recover the plaintext (automated decipherment)
- **Track C — Image to Plaintext**: Given a page image, recover the plaintext (end-to-end)

## Current Status

**MVP in progress.** Main manifest: 896 records across historical, DECODE/Gallica, synthetic, and tool-bundled parity sources. A parallel **unsolved-benchmark area** has also been seeded for open-ended evaluation on famous unsolved ciphers (Voynich, etc.). Additional sources under investigation.

### Main benchmark (`benchmark/manifest/records.jsonl`, 896 records)

| Source | Records | Cipher Type | Tracks | Status |
|--------|---------|-------------|--------|--------|
| Copiale cipher | 101 | Homophonic substitution | A, B, C | Complete |
| Borg cipher (MSS Borg.lat.898) | 397 | Monoalphabetic substitution | A, B, C | Complete |
| DECODE/Gallica (BnF manuscripts) | 155 | Nomenclator, homophonic | A only | Images downloaded; transcription pending |
| Multilingual synthetic substitution (de/en/fr/it × WB/no-WB) | 240 | Simple substitution | B only | Complete; flagged `synthetic: true` |
| External tool built-ins | 3 | Reference ciphers | B only | Parity smoke records |
| ICDAR 2024 | — | Various | — | Data staged; redistribution TBD |

### Unsolved area (`benchmark/unsolved/manifest/records.jsonl`)

A separate area for historical ciphers with **no widely accepted solution**, organized for tool evaluation without ground-truth scoring. See [`benchmark/unsolved/README.md`](benchmark/unsolved/README.md) for scope rules, the relaxed schema, and the evaluation model (including Track D: `image2hypothesis`).

| Source | Status | Notes |
|--------|--------|-------|
| Voynich Manuscript (Beinecke MS 408) | Intake script ready | `scripts/create_voynich_intake.py` pulls ~211 folios via Beinecke IIIF |
| DECODE undecrypted subset | Planned | Blocked on DECODE login |
| Rohonc Codex | Planned | Rights TBD |
| Famous short (Zodiac, Kryptos K4, Dorabella, D'Agapeyeff, Beale 1 & 3, etc.) | Planned | Challenge set, one record per cipher |

## Quick Start

Each benchmark record is one manuscript page. Files are organized by source:

```
benchmark/sources/copiale/
  images/copiale_p050.png                    # Page scan
  transcriptions/copiale_p050.diplomatic.txt # Transcription (source notation)
  transcriptions/copiale_p050.canonical.txt  # Transcription (normalized S### tokens)
  plaintext/copiale_p050.txt                 # Deciphered plaintext
  metadata/copiale_symbol_map.json           # Cipher symbol mapping

benchmark/sources/borg/
  images/borg_0010r.jpg                      # Page scan (folio 10 recto)
  transcriptions/borg_0010r.diplomatic.txt   # Character-level cipher transcription
  transcriptions/borg_0010r.canonical.txt    # Canonical S### tokens (| = word boundary)
  plaintext/borg_0010r.txt                   # Deciphered Latin plaintext

benchmark/sources/decode_gallica/
  images/decode_2686_f209.jpg                # Gallica IIIF scan (Track A only)
```

Records are listed in `benchmark/manifest/records.jsonl` (one JSON object per line) and validated against `benchmark/manifest/schema.json`.

## Documentation

- **[Benchmark Guide](benchmark/docs/benchmark_guide.md)** — Full dataset documentation: schema, rights classes, transcription layers, sources, and file formats
- **[Unsolved Area README](benchmark/unsolved/README.md)** — Scope and evaluation model for unsolved ciphers, including Track D (`image2hypothesis`)
- **[Normalization Rules](benchmark/docs/normalization_rules.md)** — How diplomatic transcriptions are converted to canonical form
- **[Source Audit](source_audit.md)** — Assessment of candidate data sources, APIs, and rights
- **[AGENTS.md](AGENTS.md)** — Project context for automated sessions (Codex, Claude)

## Repository Structure

```
benchmark/                    # The main benchmark dataset (solved / scorable)
  sources/                    #   Per-source data directories
    copiale/                  #     Copiale cipher (101 pages, Tracks A/B/C)
      images/                 #       Page scans
      transcriptions/         #       Diplomatic + canonical transcriptions
      plaintext/              #       Deciphered plaintext
      metadata/               #       Symbol maps
    borg/                     #     Borg cipher (397 folios, Tracks A/B/C)
      images/ transcriptions/ plaintext/ metadata/
    decode_gallica/           #     BnF manuscripts via Gallica (155 pages, Track A)
      images/
    *_ss_synth*/              #     Synthetic multilingual substitution (Track B)
      transcriptions/ plaintext/ keys/
    tool_builtins/            #     Reference ciphers bundled with external tools
      transcriptions/ plaintext/ metadata/
  manifest/
    schema.json               #     JSON Schema for validation
    records.jsonl             #     Record manifest
  splits/                     #   Predefined test suite definitions
  docs/                       #   Documentation
  evaluation/                 #   Scoring scripts (planned)
  unsolved/                   # Parallel area for unsolved ciphers
    manifest/
      schema.json             #   Relaxed schema (aligned with main)
      records.jsonl
    sources/
      voynich/                #   Beinecke MS 408 intake
        images/ transcriptions/ metadata/
    README.md                 #   Scope + evaluation model
scripts/                      # Data processing and curation scripts
  create_*.py                 #   Intake pipelines (decode_gallica, voynich)
  backfill_*.py               #   Idempotent schema-migration helpers
data_staging/                 # Raw source data (not tracked in git)
source_audit.md               # Source investigation notes
AGENTS.md                     # Project context for automated sessions
```

## Rights

Records carry a **required** `rights_class` field (`open`, `linked_only`, or `hold_for_review`) reflecting the redistribution status of each record's image, transcription, and plaintext layers. See the [Benchmark Guide](benchmark/docs/benchmark_guide.md#5-rights-classes) for details.

This repository is currently private. Public release is contingent on resolving image redistribution rights with source data holders.

## Schema

The record schema (`benchmark/manifest/schema.json`) is JSON Schema draft 2020-12 with `additionalProperties: false`. As of 2026-04-23 the following fields are required on every record: `id`, `source`, `status`, `task_tracks`, `rights_class`. Non-synthetic records must additionally carry at least one of `source_url` / `source_record_id` (enforced via conditional `allOf`). Synthetic records are flagged with `synthetic: true` and carry a `generation_config` object capturing generator identity and params. See the [Benchmark Guide](benchmark/docs/benchmark_guide.md#3-record-schema) for the field-by-field reference.

The unsolved area uses a parallel relaxed schema (`benchmark/unsolved/manifest/schema.json`) that requires `partial_solution_evidence` instead of full ground-truth layers and admits Track D (`image2hypothesis`).

Idempotent migration scripts for any future schema tightening live under `scripts/backfill_*.py` and `scripts/coerce_*.py`.
