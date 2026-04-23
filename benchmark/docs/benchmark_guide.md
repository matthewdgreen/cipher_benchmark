# Classical Cipher Benchmark: Dataset Guide

**Version:** 0.2
**Date:** 2026-04-23
**Status:** Draft — Borg/Copiale and multilingual synthetic Track B records loaded; DECODE/Gallica Track A records in progress; schema hardened via S1–S7 rollout; unsolved-benchmark area seeded with Voynich intake.

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
  sources/                   # Per-source data directories
    {source}/
      images/                #   Page images (PNG or JPG)
      transcriptions/        #   Two files per page:
        {id}.diplomatic.txt  #     Diplomatic transcription (source notation)
        {id}.canonical.txt   #     Canonical transcription (S### tokens)
      plaintext/             #   Deciphered plaintext, one file per page
      metadata/              #   Symbol maps and auxiliary data
        {source}_symbol_map.json
  splits/                    # Predefined test suite definitions
  evaluation/                # Scoring scripts and baselines (future)
  docs/
    benchmark_guide.md       # This document
    normalization_rules.md   # Rules for producing canonical transcriptions
```

File paths in `records.jsonl` are relative to `benchmark/` and include the source prefix, e.g. `sources/copiale/images/copiale_p050.png`.

---

## 3. Record Schema

Each record in `manifest/records.jsonl` is a JSON object. The full schema is in `manifest/schema.json`; the fields are summarized here.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record ID (pattern: `[a-z0-9_]+`), e.g. `copiale_p050` |
| `source` | string | Source collection identifier, e.g. `copiale`, `borg`, `decode_gallica`, `tool_builtins` |
| `status` | string | Solution verification status (see Section 6) |
| `task_tracks` | array | Which tracks this record supports (see Section 4) |
| `rights_class` | string | Redistribution category (see Section 5). Required as of schema S3 (2026-04-23) |

### Conditionally Required Fields

| Field | Required when | Description |
|-------|---------------|-------------|
| `source_url` or `source_record_id` | Non-synthetic records (S4) | At least one upstream-archive pointer. Synthetic records are exempt. |
| `image_files` | Track A or Track C | Relative paths to page image files |
| `transcription_diplomatic_file` | Track A | Relative path to diplomatic transcription |
| `transcription_canonical_file` | Track B | Relative path to canonical transcription |
| `plaintext_file` | Track B or Track C | Relative path to plaintext |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_url` | string (URI) | URL to the source record or project |
| `source_record_id` | string | Identifier in the original source system |
| `cipher_type` | array | Cipher family, e.g. `["homophonic_substitution"]` |
| `symbol_set` | array | Symbol types, e.g. `["alphabetic", "diacritical"]` |
| `symbol_count` | integer | Distinct cipher symbols on this page |
| `plaintext_language` | string | ISO 639-1 code, e.g. `de`, `fr`, `la` |
| `date_or_century` | string | Document date or period (free text) |
| `date_earliest_year` | integer | Earliest plausible composition year (S7) |
| `date_latest_year` | integer | Latest plausible composition year (S7) |
| `page_count` | integer | Always 1 for page-level records |
| `provenance` | string | Holding archive and location |
| `solution_reference` | string | Citation for the decipherment |
| `has_key` | boolean | Whether the cipher key is known |
| `has_inline_plaintext` | boolean | Whether the page mixes cipher and cleartext |
| `synthetic` | boolean | True for programmatically generated records (S2) |
| `generation_config` | object | Generator identity + params for synthetic records (S2) |
| `image_provenance` | object | IIIF service URL, requested width, folio offset, fetch date (S5) |
| `manuscript_page` | string | Original page or folio identifier; integer pages serialize as `"42"`, folio as `"f3r"` (S6, 2026-04-23) |
| `curation_notes` | string | Free-text notes from curators |
| `word_boundaries` | boolean | Whether canonical transcription preserves word boundaries |
| `token_count` | integer | Number of cipher tokens |
| `word_count` | integer | Approximate plaintext word count |
| `notes` | string | Short source- or generation-specific notes |

The schema sets `additionalProperties: false`, so undocumented fields are
rejected. Track-B-only generated records may omit image files and diplomatic
transcriptions.

### Synthetic records

Programmatically generated records carry `synthetic: true` and a
`generation_config` object documenting how to reproduce them:

```json
{
  "synthetic": true,
  "generation_config": {
    "generator": "synthetic_simple_substitution",
    "params": {
      "language": "de",
      "cipher_family": "simple_substitution",
      "word_boundaries": true,
      "source_tag": "de_ss_synth"
    }
  }
}
```

Consumers aggregating performance statistics should partition on `synthetic`
to avoid mixing generated and historical scores.

### Image provenance

For records whose images come from a live archive (Gallica IIIF, Beinecke
IIIF), prefer populating `image_provenance` over embedding provenance in
free-text `curation_notes`:

```json
{
  "image_provenance": {
    "iiif_service": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b10226245c",
    "requested_width": 1200,
    "fetched_at": "2026-04-18",
    "folio_offset": 548,
    "offset_source": "data_staging/gallica_folio_offsets.json"
  }
}
```

### Schema evolution

The schema was hardened across six commits on 2026-04-23. The rollout doc
`benchmark/manifest/schema_proposed_patch.md` documents the before/after of
each change (S1–S7). Idempotent migration scripts live in `scripts/`:

- `backfill_synthetic_flag.py` — tags records from `*_synth*` sources
- `backfill_rights_class.py` — sets `open` on flagged synthetics; refuses
  non-synthetic records, so new imports that forget the field fail loudly
- `coerce_manuscript_page_to_string.py` — int→str normalization

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
| **Copiale** | Scans hosted by Stockholm Univ. (reuse confirmed OK by Megyesi, 2026-04-18) | Published in Knight/Megyesi/Schaefer 2011 (ACL, CC BY-NC-SA 3.0) | Same paper | `open` | — |
| **Borg** | Vatican Library IIIF (personal/study use) | Stockholm University research | Stockholm University research | `linked_only` | Awaiting Vatican position on facsimile redistribution |
| **DECODE/Gallica** | Gallica IIIF (non-commercial reuse w/ attribution) | Pending DECODE access | Pending DECODE access | `open` for images | Resolve DECODE API access for transcription layers |
| **Synthetic (`*_ss_synth*`)** | n/a | Generated from Project Gutenberg PD texts | Generated | `open` | — |
| **tool_builtins** | n/a | Bundled with external solver tools | Bundled | `linked_only` | Audit per-tool license |

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
- **Rights status:** `open` — image reuse confirmed by Beáta Megyesi (DECRYPT, Stockholm University), 2026-04-18.
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

### DECODE / Gallica (BnF manuscripts)

- **Records:** 155 page records (Track A only pending DECODE transcription access)
- **Cipher type:** Varied — nomenclator, homophonic, polyalphabetic; see per-record `cipher_type`
- **Provenance:** Bibliothèque nationale de France, volumes in the Mélanges de Colbert / Baluze / Clairambault / Cinq cents de Colbert / Espagnol series
- **Images:** Gallica IIIF at 1200px. Per-volume folio-to-scan offsets for "bis" volumes are resolved in `data_staging/gallica_folio_offsets.json`; 2 volumes remain `hold_for_review` (Mel137bis, Mel142bis).
- **Intake script:** `scripts/create_decode_gallica_pilot.py`
- **Rights:** `open` (Gallica non-commercial reuse with attribution)

### Multilingual synthetic simple substitution

- **Records:** 240 (30 × {de, en, fr, it} × {word-boundary, no-word-boundary})
- **Cipher type:** Simple substitution
- **Source text:** Project Gutenberg public-domain corpora
- **Tracks supported:** B only (generated from plaintext; no manuscript image)
- **Flags:** `synthetic: true`, `generation_config` populated
- **Rights:** `open`

### Tool-bundled parity records

- **Records:** 3 (`goldbug`, `horacemann`, `zodiac408`) imported from the Zenith solver checkout
- **Purpose:** Parity smoke tests against external solver outputs
- **Pending import:** Additional Zenith/zkdecrypto-lite bundled ciphers (see `AGENTS.md`)

*(Additional sources — British Library manuscripts, HCPortal, ICDAR competition data — are under investigation. See `source_audit.md` in the repository root. For unsolved historical ciphers, see `benchmark/unsolved/README.md`.)*

---

## 10. File Formats

| File type | Format | Encoding | Notes |
|-----------|--------|----------|-------|
| Images | PNG or JPG | — | One file per page in `sources/{source}/images/`. Copiale: PNG. Borg/Gallica: JPG (1200px wide from IIIF). |
| Diplomatic transcription | Plain text | UTF-8 | Space-separated tokens; blank lines = line breaks |
| Canonical transcription | Plain text | UTF-8 | Space-separated S### tokens; same line structure as diplomatic |
| Plaintext | Plain text | UTF-8 | Deciphered text; logogram markers preserved as `*token*` |
| Manifest | JSONL | UTF-8 | One JSON object per line |
| Symbol maps | JSON | UTF-8 | See Section 8 |

---

## 11. Planned Additions

- **Predefined test suites** (`splits/`): Standard test definitions at multiple difficulty levels (single-page, 10-page, full-document). See Section 4a for the test definition format.
- **Evaluation scripts** (`evaluation/`): Scoring code for each track (symbol error rate for Track A, plaintext accuracy for Tracks B and C).
- **Additional sources**: DECODE database records (with plaintext/transcription once API access resolves), British Library cipher manuscripts, HCPortal material, ICDAR 2024 competition data. See `source_audit.md` for current status.
- **Difficulty annotations**: Per-record difficulty estimates based on cipher complexity, symbol count, and solution method.
- **Unsolved area expansion**: Voynich folios (intake script ready), DECODE undecrypted subset, Rohonc Codex, and a famous-short challenge set (Zodiac Z13/Z32, Kryptos K4, Dorabella, D'Agapeyeff, Beale 1 & 3, Somerton Man, etc.). See `benchmark/unsolved/README.md`.

## 12. Unsolved Area

A parallel area at `benchmark/unsolved/` holds ciphers with no widely
accepted solution. It uses its own relaxed schema
(`benchmark/unsolved/manifest/schema.json`) aligned with the main schema's
vocabulary but with:

- Required `partial_solution_evidence` field recording what signal exists
  short of ground truth (`interlineation_visible`, `partial_key_published`,
  etc.)
- `status` enum restricted to `unsolved` / `disputed` / `partial_solution`
- Optional `notable_attempts` array for citing inconclusive prior work
- Task-track enum extended with `image2hypothesis` (Track D) — open-ended
  analysis with no automated scoring

See `benchmark/unsolved/README.md` for the full evaluation model (scoring
against adjacent solved records, against partial evidence, or unscored
archive of candidate outputs).
