# Classical Cipher Benchmark

A standardized benchmark dataset for evaluating AI-assisted classical cipher analysis tools. The benchmark pairs historical cipher manuscript images with verified transcriptions and known plaintext, enabling reproducible evaluation across three task tracks:

- **Track A — Image to Transcription**: Given a page image, produce a symbol-level transcription (HTR for cipher manuscripts)
- **Track B — Transcription to Plaintext**: Given a normalized transcription, recover the plaintext (automated decipherment)
- **Track C — Image to Plaintext**: Given a page image, recover the plaintext (end-to-end)

## Current Status

**MVP in progress.** The Copiale cipher source is complete (101 page-level records). Additional sources (DECODE database, British Library manuscripts, HCPortal, ICDAR competition data) are under investigation.

| Source | Records | Status |
|--------|---------|--------|
| Copiale cipher | 101 | Complete |
| DECODE database | — | Metadata exported; content pending |
| British Library | — | Candidates identified; pending rights |
| HCPortal | — | Not yet started |
| ICDAR 2024 | — | Pending RRC access |

## Quick Start

Each benchmark record is one manuscript page with four associated files:

```
benchmark/images/copiale_p050.png                    # Page scan
benchmark/transcriptions/copiale_p050.diplomatic.txt # Transcription (source notation)
benchmark/transcriptions/copiale_p050.canonical.txt  # Transcription (normalized S### tokens)
benchmark/plaintext/copiale_p050.txt                 # Deciphered plaintext
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
  images/            #   Page images (PNG)
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
