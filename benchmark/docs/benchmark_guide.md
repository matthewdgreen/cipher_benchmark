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

The benchmark operates at **record level**: one record typically corresponds to one manuscript page. Records are the atomic storage unit — every record has its own image, transcription, and plaintext files.

However, records are not necessarily the unit of evaluation. For decipherment tasks (Tracks B and C), the amount of ciphertext available dramatically affects difficulty. A system given 101 pages of the same cipher has far more statistical signal than one given a single page. Test definitions (Section 4a) handle this by separating what a system is *scored on* from what it is *given*.

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

## 4a. Test Definitions

A **test** is the unit of evaluation: it specifies what a system receives as input, what it is scored on, and which track applies. Tests are defined in `splits/` and reference records by ID.

### Structure

Each test has three components:

| Component | Description |
|-----------|-------------|
| **Target** | The record(s) whose output is scored. This is what the system must produce. |
| **Context** | Additional record(s) the system may use as auxiliary input. These are in the same cipher system as the target but are not scored. |
| **Track** | Which task track applies (A, B, or C). |

### Why Separate Target from Context?

The amount of available ciphertext is a primary driver of decipherment difficulty. For a 136-symbol homophonic substitution cipher like the Copiale:

- **1 page** (~600–700 tokens): Very difficult. Sparse frequency data, many symbols seen only a few times.
- **10 pages** (~7,000 tokens): Feasible for statistical methods. Most symbol frequencies are stable.
- **101 pages** (~70,000 tokens): Comparatively straightforward. Rich statistical signal.

By separating target from context, the benchmark can evaluate the same system at multiple difficulty levels using the same underlying records. The scoring unit stays consistent (one page of plaintext) while the input varies.

### Track-Specific Behavior

- **Track A** (image→transcription): Context is generally not applicable — each page is transcribed independently. The target is a single page image; context may optionally include sample transcriptions from other pages (for few-shot prompting), but this should be noted in the test definition.
- **Track B** (transcription→plaintext): The target is one or more canonical transcriptions to decrypt. Context provides additional ciphertext in the same cipher system. The system is scored only on the target pages' plaintext.
- **Track C** (image→plaintext): Same as Track B, but images are provided instead of transcriptions. Context images give the system more material to work with.

### Test Definition Format

Test definitions are stored as JSON in `splits/`. Format will be finalized when evaluation tooling is built, but the minimum structure is:

```json
{
  "test_id": "copiale_single_p050",
  "track": "transcription2plaintext",
  "cipher_system": "copiale",
  "target_records": ["copiale_p050"],
  "context_records": [],
  "description": "Decrypt page 50 with no additional context"
}
```

```json
{
  "test_id": "copiale_full_p050",
  "track": "transcription2plaintext",
  "cipher_system": "copiale",
  "target_records": ["copiale_p050"],
  "context_records": ["copiale_p001", "copiale_p002", "...", "copiale_p105"],
  "description": "Decrypt page 50 given all other pages as context"
}
```

### Flexibility

This structure imposes no fixed assumptions about:

- **Granularity**: A record can represent a page, a partial page, or a multi-page unit, depending on what the source material requires.
- **Context size**: A test can have zero context records (hardest) or many (easiest).
- **Target size**: A test can score on one record or multiple. For sources with very short pages, it may make sense to score on several pages jointly.
- **Cross-document context**: Context records could come from a different document that uses the same cipher system (e.g., two letters encrypted with the same nomenclator).

Predefined test suites (e.g., "single-page difficulty", "10-page difficulty", "full-document") will be provided as standard splits for comparable benchmarking.

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

### Borg Cipher (MSS Borg.lat.898)

- **Records:** 397 folios (of 408; pages without cipher content or missing images excluded)
- **Cipher type:** Monoalphabetic substitution
- **Symbol set:** 77 distinct characters (alphabetic, numerical, diacritical); 34 core cipher symbols
- **Plaintext language:** Latin (medical/pharmaceutical text)
- **Date:** 17th century
- **Provenance:** Biblioteca Apostolica Vaticana, MSS Borg.lat.898. 408-folio manuscript.
- **Solution:** Aldarrab, Knight, Megyesi. "The Borg Cipher." DECRYPT project, Stockholm University.
- **Transcription:** Character-level. Each cipher character maps to an S### token; words delimited by `|` in canonical form.
- **Rights status:** `linked_only` — images from Vatican Library IIIF (personal use or study only). Transcriptions and plaintext from Stockholm University research.
- **Tracks supported:** A (image2transcription), B (transcription2plaintext), C (image2plaintext)
- **Notes:** 31 pages contain mixed cleartext passages (marked with `<CLEARTEXT>` in diplomatic transcription). Plaintext is corrected Latin from Urban Örneholm's interpretation.

*(Additional sources — DECODE database records, British Library manuscripts, HCPortal, ICDAR competition data — are under investigation. See `source_audit.md` in the repository root.)*

---

## 10. File Formats

| File type | Format | Encoding | Notes |
|-----------|--------|----------|-------|
| Images | PNG or JPG | — | One file per page; variable resolution. Copiale: PNG. Borg: JPG (1200px wide from IIIF). |
| Diplomatic transcription | Plain text | UTF-8 | Space-separated tokens; blank lines = line breaks |
| Canonical transcription | Plain text | UTF-8 | Space-separated S### tokens; same line structure as diplomatic |
| Plaintext | Plain text | UTF-8 | Deciphered text; logogram markers preserved as `*token*` |
| Manifest | JSONL | UTF-8 | One JSON object per line |
| Symbol maps | JSON | UTF-8 | See Section 8 |

---

## 11. Planned Additions

- **Predefined test suites** (`splits/`): Standard test definitions at multiple difficulty levels (single-page, 10-page, full-document). See Section 4a for the test definition format.
- **Evaluation scripts** (`evaluation/`): Scoring code for each track (symbol error rate for Track A, plaintext accuracy for Tracks B and C).
- **Additional sources**: DECODE database records, British Library cipher manuscripts, HCPortal material, ICDAR 2024 competition data. See `source_audit.md` for current status.
- **Difficulty annotations**: Per-record difficulty estimates based on cipher complexity, symbol count, and solution method.
