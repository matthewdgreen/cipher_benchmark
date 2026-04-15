# Classical Cipher Benchmark: Dataset Guide

**Version:** 0.1
**Date:** 2026-04-15
**Status:** Draft — Copiale source complete; additional sources in progress

---

## 1. Overview

This benchmark provides standardized evaluation data for AI-assisted classical cipher analysis tools. Each record pairs a historical cipher manuscript page with its transcription and known plaintext, enabling reproducible evaluation across three task tracks.

### Task Tracks

| Track | Input | Output | What it tests |
|-------|-------|--------|---------------|
| **A: image2transcription** | Page image | Diplomatic transcription | HTR / symbol recognition on cipher manuscripts |
| **B: transcription2plaintext** | Canonical transcription | Plaintext | Automated decipherment / cryptanalysis |
| **C: image2plaintext** | Page image | Plaintext | End-to-end cipher breaking (A + B combined) |

### Unit of Analysis

The benchmark operates at **page level**: one record = one manuscript page. This provides a natural, well-defined unit with clear image boundaries and keeps records independent of document-level structure.

---

## 2. Directory Structure

```
benchmark/
  manifest/
    schema.json              # JSON Schema for record validation
    records.jsonl            # One JSON record per line, one per page
  images/                    # Page images (PNG)
  transcriptions/            # Two files per page:
    {id}.diplomatic.txt      #   Diplomatic transcription (source notation)
    {id}.canonical.txt       #   Canonical transcription (S### tokens)
  plaintext/                 # Deciphered plaintext, one file per page
  metadata/                  # Per-source symbol maps and auxiliary data
    {source}_symbol_map.json #   Diplomatic-to-canonical token mapping
  splits/                    # Train/dev/test split definitions (future)
  evaluation/                # Scoring scripts and baselines (future)
  docs/
    benchmark_guide.md       # This document
    normalization_rules.md   # Rules for producing canonical transcriptions
```

---

## 3. Record Schema

Each record in `manifest/records.jsonl` is a JSON object. The full schema is in `manifest/schema.json`; the fields are summarized here.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record ID (pattern: `[a-z0-9_]+`), e.g. `copiale_p050` |
| `source` | string | Source collection identifier, e.g. `copiale`, `decode`, `hcportal` |
| `source_record_id` | string | Identifier in the original source system |
| `rights_class` | string | Redistribution category (see Section 5) |
| `status` | string | Solution verification status (see Section 6) |
| `image_files` | array | Relative paths to page image files |
| `transcription_diplomatic_file` | string | Relative path to diplomatic transcription |
| `transcription_canonical_file` | string | Relative path to canonical transcription |
| `plaintext_file` | string | Relative path to plaintext |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_url` | string (URI) | URL to the source record or project |
| `task_tracks` | array | Which tracks this record supports (see Section 4) |
| `cipher_type` | array | Cipher family, e.g. `["homophonic_substitution"]` |
| `symbol_set` | array | Symbol types, e.g. `["alphabetic", "diacritical"]` |
| `symbol_count` | integer | Distinct cipher symbols on this page |
| `plaintext_language` | string | ISO 639-1 code, e.g. `de`, `fr`, `la` |
| `date_or_century` | string | Document date or period |
| `page_count` | integer | Always 1 for page-level records |
| `provenance` | string | Holding archive and location |
| `solution_reference` | string | Citation for the decipherment |
| `has_key` | boolean | Whether the cipher key is known |
| `has_inline_plaintext` | boolean | Whether the page mixes cipher and cleartext |
| `manuscript_page` | integer | Original page number in the manuscript |
| `curation_notes` | string | Free-text notes from curators |

---

## 4. Task Track Eligibility

Not every record supports every track. A record's `task_tracks` field lists which tracks it can be used for:

- **image2transcription**: Requires a page image and diplomatic transcription.
- **transcription2plaintext**: Requires a canonical transcription and plaintext.
- **image2plaintext**: Requires a page image and plaintext.

A record with all three data layers (image + transcription + plaintext) supports all three tracks.

---

## 5. Rights Classes

Each record has a `rights_class` that governs how it can be distributed. This reflects the combined rights status of three independent layers: the manuscript image, the transcription, and the plaintext/solution.

### Classes

| Class | Meaning | What is distributed | When to use |
|-------|---------|-------------------|-------------|
| **`open`** | All layers are freely redistributable | Full data: images, transcriptions, plaintext | All layers confirmed as public domain, open license (CC BY, CC0, etc.), or original work by the benchmark authors |
| **`linked_only`** | Some layers cannot be redistributed directly | Metadata + file pointers; users download source data themselves | Image or transcription rights are unclear, held by a third party, or under a restrictive license |
| **`hold_for_review`** | Rights status is unresolved | Record exists in the manifest but data files may not be included in public releases | Awaiting response from rights holders; complex or ambiguous licensing |

### Rights Layers

A single record involves up to three independent rights holders:

1. **Images**: Typically owned by the holding archive or library (e.g., British Library, BnF, Stockholm University). Digital reproductions may carry their own license separate from the underlying manuscript.
2. **Transcriptions**: Created by researchers. May be published under an academic license (e.g., CC BY-NC-SA via ACL Anthology) or be unpublished research data.
3. **Plaintext / solutions**: Published in academic papers. License depends on the venue (e.g., ACL pre-2016 papers are CC BY-NC-SA 3.0).

The `rights_class` reflects the *most restrictive* layer. If images are open but the transcription is unclear, the record is `linked_only`.

### Per-Source Rights Status

| Source | Images | Transcriptions | Plaintext | Current class | Path to `open` |
|--------|--------|---------------|-----------|---------------|-----------------|
| **Copiale** | Scans hosted by Stockholm Univ.; rights unclear (private collection) | Published in Knight/Megyesi/Schaefer 2011 (ACL, CC BY-NC-SA 3.0) | Same paper | `linked_only` | Awaiting response from Megyesi team on image redistribution rights |

*(Additional sources will be added as they are incorporated into the benchmark.)*

---

## 6. Solution Status

Each record has a `status` indicating how confident we are in the plaintext:

| Status | Meaning |
|--------|---------|
| **`solved_verified`** | Solution published in peer-reviewed work and independently verifiable |
| **`solved_probable`** | Solution exists but has not been independently verified |
| **`partial_solution`** | Parts of the cipher are solved; other parts remain unknown |
| **`unsolved`** | No known solution (included for Track A only — image-to-transcription) |

---

## 7. Transcription Layers

Every record has two transcription files. See `docs/normalization_rules.md` for full details.

### Diplomatic Transcription

A close rendering of the cipher text using the notation conventions of the original transcriber or scholarly edition. For the Copiale cipher, this means ASCII mnemonics like `grr`, `bar`, `tri` for handwritten glyphs.

Diplomatic transcriptions preserve:
- The transcriber's symbol labels
- Line breaks from the manuscript
- Catch-word markers (prefixed with `#`)
- Uncertainty markers (suffixed with `?`)

### Canonical Transcription

A normalized form where every distinct cipher symbol is remapped to an abstract token (`S001`, `S002`, ...) via a deterministic symbol map. This ensures evaluation metrics are not affected by transcription conventions.

Properties:
- One-to-one mapping from diplomatic tokens to S-tokens
- Tokens assigned in order of first appearance across the full document
- Global per cipher system (not per page) — `S007` means the same symbol on every page
- Symbol maps stored in `metadata/{source}_symbol_map.json`

### Why Both?

- **Track A** (image2transcription) is evaluated against the diplomatic transcription, since that is what a human transcriber produces.
- **Track B** (transcription2plaintext) uses the canonical transcription as input, so that systems are compared on decipherment ability, not on whether they happen to use the same symbol labels as the ground truth.

---

## 8. Symbol Maps

Each cipher system has a symbol map in `metadata/` that defines the diplomatic-to-canonical mapping.

```json
{
  "description": "Human-readable description",
  "source": "Citation for the transcription",
  "cipher_system": "Identifier for the cipher system",
  "total_symbols": 136,
  "mapping": {
    "L": "S001",
    "grr": "S007",
    "nee": "S077"
  },
  "logogram_glossary": {
    "nee": "master",
    "tri": "lodge"
  },
  "notes": "Free text"
}
```

The `logogram_glossary` documents symbols that represent whole words rather than letters. This is metadata only — logograms are treated as regular symbols in the canonical transcription.

---

## 9. Sources

### Copiale Cipher

- **Records:** 101 pages (of 105; pages 19, 33, 46, 100 missing from source transcription)
- **Cipher type:** Homophonic substitution + nomenclator
- **Symbol set:** 136 distinct symbols (alphabetic, diacritical, logographic)
- **Plaintext language:** German
- **Date:** Mid-18th century
- **Provenance:** Private collection; scans hosted by Stockholm University. A parallel manuscript exists at Niedersächsisches Landesarchiv, Wolfenbüttel.
- **Solution:** Knight, Megyesi, Schaefer (2011). "The Copiale Cipher." ACL Workshop on Language Technology for Cultural Heritage, Social Sciences, and Humanities.
- **Rights status:** `linked_only` — image redistribution rights pending clarification from the DECRYPT team at Stockholm University.
- **Tracks supported:** A (image2transcription), B (transcription2plaintext), C (image2plaintext)

*(Additional sources — DECODE database records, British Library manuscripts, HCPortal, ICDAR competition data — are under investigation. See `source_audit.md` in the repository root.)*

---

## 10. File Formats

| File type | Format | Encoding | Notes |
|-----------|--------|----------|-------|
| Images | PNG | — | One file per page; variable resolution |
| Diplomatic transcription | Plain text | UTF-8 | Space-separated tokens; blank lines = line breaks |
| Canonical transcription | Plain text | UTF-8 | Space-separated S### tokens; same line structure as diplomatic |
| Plaintext | Plain text | UTF-8 | Deciphered text; logogram markers preserved as `*token*` |
| Manifest | JSONL | UTF-8 | One JSON object per line |
| Symbol maps | JSON | UTF-8 | See Section 8 |

---

## 11. Planned Additions

- **Train/dev/test splits** (`splits/`): Predefined splits for reproducible evaluation. Will stratify by source, cipher type, and difficulty.
- **Evaluation scripts** (`evaluation/`): Scoring code for each track (symbol error rate for Track A, plaintext accuracy for Tracks B and C).
- **Additional sources**: DECODE database records, British Library cipher manuscripts, HCPortal material, ICDAR 2024 competition data. See `source_audit.md` for current status.
- **Difficulty annotations**: Per-record difficulty estimates based on cipher complexity, symbol count, and solution method.
