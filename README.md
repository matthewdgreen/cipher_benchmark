# Classical Cipher Benchmark

A standardized benchmark dataset for evaluating AI-assisted classical cipher analysis tools. The benchmark pairs historical cipher manuscript images with verified transcriptions and known plaintext, enabling reproducible evaluation across three task tracks:

- **Track A — Image to Transcription**: Given a page image, produce a symbol-level transcription (HTR for cipher manuscripts)
- **Track B — Transcription to Plaintext**: Given a normalized transcription, recover the plaintext (automated decipherment)
- **Track C — Image to Plaintext**: Given a page image, recover the plaintext (end-to-end)

## Current Status

**MVP in progress.** Three sources loaded (638 page-level records). Additional sources under investigation.

| Source | Records | Cipher Type | Tracks | Status |
|--------|---------|-------------|--------|--------|
| Copiale cipher | 101 | Homophonic substitution | A, B, C | Complete |
| Borg cipher (MSS Borg.lat.898) | 397 | Monoalphabetic substitution | A, B, C | Complete |
| DECODE/Gallica (BnF manuscripts) | 140 | Nomenclator, homophonic | A only | Images downloaded; transcription pending |
| ICDAR 2024 | — | Various | — | Data staged; redistribution TBD |

## Quick Start

Each benchmark record is one manuscript page with four associated files:

```
benchmark/images/copiale_p050.png                    # Page scan (Copiale)
benchmark/transcriptions/copiale_p050.diplomatic.txt # Transcription (source notation)
benchmark/transcriptions/copiale_p050.canonical.txt  # Transcription (normalized S### tokens)
benchmark/plaintext/copiale_p050.txt                 # Deciphered plaintext

benchmark/images/borg_0010r.jpg                      # Page scan (Borg, folio 10 recto)
benchmark/transcriptions/borg_0010r.diplomatic.txt   # Character-level cipher transcription
benchmark/transcriptions/borg_0010r.canonical.txt    # Canonical S### tokens (| = word boundary)
benchmark/plaintext/borg_0010r.txt                   # Deciphered Latin plaintext
```

Records are listed in `benchmark/manifest/records.jsonl` (one JSON object per line) and validated against `benchmark/manifest/schema.json`.

## Documentation

- **[Benchmark Guide](benchmark/docs/benchmark_guide.md)** — Full dataset documentation: schema, rights classes, transcription layers, sources, and file formats
- **[Normalization Rules](benchmark/docs/normalization_rules.md)** — How diplomatic transcriptions are converted to canonical form
- **[Source Audit](source_audit.md)** — Assessment of candidate data sources, APIs, and rights

## Repository Structure

```
benchmark/           # The benchmark dataset
  manifest/          #   Record manifest and schema
  images/            #   Page images (PNG/JPG)
  transcriptions/    #   Diplomatic + canonical transcriptions
  plaintext/         #   Deciphered plaintext
  metadata/          #   Symbol maps
  docs/              #   Documentation
  splits/            #   Train/dev/test splits (planned)
  evaluation/        #   Scoring scripts (planned)
scripts/             # Data processing and curation scripts
data_staging/        # Raw source data (not tracked in git)
source_audit.md      # Source investigation notes
```

## Rights

Records carry a `rights_class` field (`open`, `linked_only`, or `hold_for_review`) reflecting the redistribution status of each record's image, transcription, and plaintext layers. See the [Benchmark Guide](benchmark/docs/benchmark_guide.md#5-rights-classes) for details.

This repository is currently private. Public release is contingent on resolving image redistribution rights with source data holders.
