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
- **[Normalization Rules](benchmark/docs/normalization_rules.md)** — How diplomatic transcriptions are converted to canonical form
- **[Source Audit](source_audit.md)** — Assessment of candidate data sources, APIs, and rights

## Repository Structure

```
benchmark/                    # The benchmark dataset
  sources/                    #   Per-source data directories
    copiale/                  #     Copiale cipher (101 pages, Tracks A/B/C)
      images/                 #       Page scans
      transcriptions/         #       Diplomatic + canonical transcriptions
      plaintext/              #       Deciphered plaintext
      metadata/               #       Symbol maps
    borg/                     #     Borg cipher (397 folios, Tracks A/B/C)
      images/ transcriptions/ plaintext/ metadata/
    decode_gallica/           #     BnF manuscripts via Gallica (140 pages, Track A)
      images/
  manifest/                   #   Record manifest and schema
  splits/                     #   Predefined test suite definitions
  docs/                       #   Documentation
  evaluation/                 #   Scoring scripts (planned)
scripts/                      # Data processing and curation scripts
data_staging/                 # Raw source data (not tracked in git)
source_audit.md               # Source investigation notes
```

## Rights

Records carry a `rights_class` field (`open`, `linked_only`, or `hold_for_review`) reflecting the redistribution status of each record's image, transcription, and plaintext layers. See the [Benchmark Guide](benchmark/docs/benchmark_guide.md#5-rights-classes) for details.

This repository is currently private. Public release is contingent on resolving image redistribution rights with source data holders.
