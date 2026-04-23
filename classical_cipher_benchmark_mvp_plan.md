# MVP Plan: Benchmark for AI-Enabled Classical Cipher Decoding Tools

> **Status (2026-04-23):** This document is the **original MVP specification**
> and is retained as a design record. Much of what it proposed is now live
> in the repository; several sections below are superseded by later
> documents:
>
> - **Schema** (Section 10): superseded by `benchmark/manifest/schema.json`
>   (with the S1–S7 hardening landed 2026-04-23, commits `a80adee` → `d0c56f8`).
> - **File layout** (Section 11): superseded by the "Repository Structure"
>   section of the top-level `README.md` and the "Directory Structure"
>   section of `benchmark/docs/benchmark_guide.md`.
> - **Immediate next steps** (Section 22): completed through the Voynich
>   intake and unsolved-area seeding.
> - **Unsolved challenge appendix** (Section 25): superseded by the live
>   `benchmark/unsolved/` area and its README.
>
> The `TODO.md` file is the current source of truth for outstanding work.

## 1. Purpose

Build an initial public benchmark for evaluating **classical cipher decoding tools**, especially AI-enabled systems, on **real-world historical material** rather than purely synthetic ciphertext.

The MVP should support three related tasks:

1. **Image → transcription**
2. **Transcription → plaintext/decrypt**
3. **Image → plaintext end-to-end**

The benchmark should emphasize:
- authentic historical cipher material
- solved examples first
- paired image and text inputs
- standardized, machine-readable outputs
- clear separation between redistributable data and linked-only data

---

## 2. MVP Goal

Produce a **small, defensible, well-documented benchmark set** that can be released quickly and expanded later.

### Target size for MVP
- **25–75 solved examples**
- drawn from **real historical sources**
- with at least:
  - one or more raw page images
  - a diplomatic transcription
  - a canonical normalized transcription
  - a verified plaintext/decrypt or equivalent solved ground truth
  - a machine-readable metadata record

This is intentionally modest. The goal is to prove that the benchmark format, curation rules, and evaluation approach are sound before attempting scale.

---

## 3. Non-Goals for the MVP

The MVP is **not** trying to:

- cover every classical cipher family
- solve licensing for every archive
- include all unsolved public challenges
- build a full OCR system
- build a full cryptanalysis framework
- settle a universal standard for historical transcription

Those belong to later releases.

---

## 4. Proposed Benchmark Structure

The benchmark should have **three tracks**, even if they share data.

### Track A: Image → Transcription
Input:
- scanned page image(s)

Output:
- diplomatic transcription
- canonical symbol transcription

Purpose:
- measure OCR / HTR / symbol-recognition performance on cipher manuscripts

### Track B: Transcription → Plaintext
Input:
- canonical or diplomatic transcription

Output:
- plaintext/decrypt
- optionally cipher type and key hypothesis

Purpose:
- measure cryptanalytic decoding independent of OCR

### Track C: Image → Plaintext
Input:
- scanned page image(s)

Output:
- plaintext/decrypt

Purpose:
- measure full end-to-end performance

---

## 5. Initial Source Strategy

Use a **two-layer sourcing model**.

### Primary real-world sources
- **DECRYPT / DECODE**
- **HCPortal**
- optionally a public subset from **ICDAR historical cipher handwriting data** for transcription-focused material

### Synthetic control source
- **NCID / ACA-style generated classical ciphers**

Synthetic data should **not** be mixed into the core real-world benchmark. It can be included as a separate control set for sanity checks or model pretesting.

---

## 6. Release Model

Create two releases from the start.

### Open Release
Contains only material that is clearly safe to redistribute:
- images
- transcriptions
- plaintext
- metadata
- evaluation scripts

### Linked Release
Contains a manifest of additional benchmark records that are valuable but not safely redistributable as bundled files:
- source record identifiers
- retrieval URLs or source references
- metadata
- expected task structure
- references to external ground truth where allowed

This prevents the project from stalling on rights issues while preserving future expansion.

---

## 7. Inclusion Rules for the MVP

A record is eligible for the core MVP if it satisfies all of the following:

1. **Authentic cipher document**
   - real historical or archival source material

2. **Solved status**
   - plaintext or equivalent decipherment exists and can be verified

3. **Image availability**
   - at least one usable page image exists

4. **Transcription availability**
   - either an existing transcription exists or one can be created reliably

5. **Benchmark legality**
   - the item can be included in the open release, or at minimum in the linked release

6. **Usable length**
   - enough text to make the task nontrivial

7. **Stable metadata**
   - source record can be cited and tracked over time

### Exclusion rules
Exclude items that are:
- unsolved, unless placed in a separate challenge appendix
- too fragmentary to evaluate fairly
- illegible beyond reasonable transcription effort
- impossible to redistribute or reference cleanly
- duplicates of the same text in multiple forms unless needed for comparison

---

## 8. Ground Truth Policy

Do **not** treat “has a key” as automatically solved.

A record counts as solved only if one of the following is true:

- plaintext is explicitly present in the source
- a linked scholarly source provides a decipherment
- the key and transcription allow a reproducible decryption that has been independently verified

Each record should receive one of these labels:

- `solved_verified`
- `solved_probable`
- `partial_solution`
- `unsolved`

Only `solved_verified` should enter the scored MVP benchmark.

---

## 9. Two Transcription Layers

The benchmark should preserve **two text representations** for every included record.

### 9.1 Diplomatic transcription
A close representation of the source, preserving as much of the historical form as practical:
- line breaks
- spaces
- punctuation
- uncertain characters
- mixed alphabets
- inline plaintext or cleartext markers where relevant

Purpose:
- preserve scholarly fidelity
- support high-quality OCR/transcription research

### 9.2 Canonical normalized transcription
A benchmark-oriented symbol stream in which each distinct cipher symbol class on a document is remapped to abstract stable tokens.

Example:
`S001 S014 S014 S203 S077 ...`

Purpose:
- make evaluation robust
- avoid dependence on arbitrary Unicode choices
- compare outputs across tools fairly

### Policy
The canonical transcription should be derived from the diplomatic one through a documented normalization process. Both versions should ship with the record.

---

## 10. Core Record Schema

Each benchmark item should be represented by a JSON record.

```json
{
  "id": "decode_r0360_p04",
  "source": "decode",
  "source_record_id": "360",
  "task_tracks": ["image2transcription", "transcription2plaintext", "image2plaintext"],
  "rights_class": "open",
  "status": "solved_verified",
  "cipher_type": ["homophonic_substitution", "nomenclator"],
  "symbol_set": ["numerical", "alphabetic"],
  "plaintext_language": "en",
  "image_files": ["images/decode_r0360_p04.png"],
  "transcription_diplomatic_file": "transcriptions/decode_r0360_p04.diplomatic.txt",
  "transcription_canonical_file": "transcriptions/decode_r0360_p04.canonical.txt",
  "plaintext_file": "plaintext/decode_r0360_p04.txt",
  "has_key": true,
  "has_inline_plaintext": false,
  "notes": "multiple alphabets; page-level record"
}
```

### Minimum required fields
- `id`
- `source`
- `source_record_id`
- `rights_class`
- `status`
- `image_files`
- `transcription_diplomatic_file`
- `transcription_canonical_file`
- `plaintext_file`

### Recommended fields
- `cipher_type`
- `symbol_set`
- `plaintext_language`
- `date_or_century`
- `page_count`
- `provenance`
- `solution_reference`
- `curation_notes`

---

## 11. File Layout

Suggested repository structure:

```text
benchmark/
  README.md
  LICENSE
  manifest/
    records.jsonl
    schema.json
  images/
  transcriptions/
  plaintext/
  metadata/
  splits/
    train.jsonl
    dev.jsonl
    test.jsonl
  evaluation/
    score_transcription.py
    score_plaintext.py
    score_end_to_end.py
  docs/
    curation_guidelines.md
    normalization_rules.md
    rights_policy.md
```

---

## 12. Curation Workflow

### Phase 0: Source audit
Before collecting candidates, audit each source to estimate realistic yield:
- for each source (DECRYPT, HCPortal, ICDAR, etc.), estimate how many records satisfy all 7 inclusion criteria
- characterize what each source actually provides (images? transcriptions? solutions? rights info?)
- identify API or bulk-access options
- document blockers and gaps per source
- produce a brief written audit summary per source

This prevents the schedule from being built on optimistic assumptions about data availability.

### Phase 1: Candidate discovery (funnel model)
Use a fail-fast funnel to avoid investing effort in records that will be dropped later:

```
Step 1: Does a usable image exist?          → No → drop
Step 2: Is it plausibly redistributable?     → No → move to linked-only
Step 3: Does a verified solution exist?      → No → drop (for MVP)
Step 4: Can solution be aligned to pages?    → No → drop or flag
Step 5: Full extraction + normalization
Step 6: QC review
```

Log all candidates (including rejected ones) in the candidate manifest with rejection reasons.

### Phase 2: Rights triage
For each candidate, classify as:
- `open`
- `linked_only`
- `hold_for_review`
- `exclude`

### Phase 3: Data extraction
For each accepted record:
- download or reference source images
- collect source transcription if available
- collect plaintext / decipherment evidence
- collect metadata and provenance

### Phase 4: Transcription normalization
- prepare diplomatic transcription
- assign symbol classes
- produce canonical token sequence
- document ambiguous characters

**Note:** This phase is harder than it looks for real historical ciphers. Symbol inventories vary wildly (10 symbols to 500+ in a nomenclator), documents mix cipher symbols with cleartext, symbol boundaries can be ambiguous (is `42` one symbol or two?), and different pages of the same cipher system may use visually distinct glyphs for the same code. The normalization rules document is arguably the hardest intellectual work in the MVP and should be stress-tested during the 10-record pilot.

### Phase 5: Ground truth verification
- verify plaintext against source evidence
- confirm that the transcription and plaintext correspond to the same page/text unit
- verify no accidental page mismatch or truncation

**Note on page alignment:** Scholarly decipherments are typically published at the document or letter level, not the page level. This creates alignment work:
- multi-page documents where the solution covers the whole thing but benchmarking is per-page
- partial solutions (first N pages solved, remainder unsolved)
- published plaintext that silently reorders or omits passages

Each record must document how the page-level alignment was established.

### Phase 6: Packaging
- assign stable benchmark id
- place files in repo structure
- generate manifest entry
- run validation checks

---

## 13. Unit of Evaluation

The benchmark should define the scoring unit explicitly.

### Recommended MVP unit
Use **page-level items**, with optional line segmentation metadata.

Why:
- pages are natural archival units
- easier to align with source images
- easier to package for OCR tasks
- still flexible enough for later line- or record-level evaluation

Later versions can add:
- line-level tasks
- record-level multi-page tasks
- symbol-box annotations

---

## 14. Quality Control Checklist

Every record must pass the following before entering the scored set:

- image opens correctly
- source metadata is recorded
- transcription matches the image
- plaintext matches the intended cipher text segment
- normalization is reproducible
- rights class is documented
- no duplicated record id
- no hidden dependence on unsupported archive access
- at least one human review completed

### Recommended review model
- one primary curator
- one secondary reviewer
- disagreement notes stored in `curation_notes`

---

## 15. Evaluation Design

### 15.1 Track A: Image → Transcription
Metrics:
- character error rate on diplomatic transcription
- token error rate on canonical transcription
- optional symbol-class F1

### 15.2 Track B: Transcription → Plaintext
Metrics:
- exact solve rate
- normalized character accuracy
- partial-solve score for near-correct decrypts

### 15.3 Track C: Image → Plaintext
Metrics:
- end-to-end exact solve rate
- normalized plaintext accuracy
- error attribution split:
  - OCR/transcription error
  - cryptanalysis/decoding error

### Important principle
Do not collapse all tracks into a single number. A tool with excellent OCR and poor decoding should not be indistinguishable from one with poor OCR and excellent decoding.

---

## 16. Recommended MVP Composition

Aim for diversity, not just convenience.

### Suggested distribution
- 8–15 easy or medium solved records
- 8–15 moderate records with mixed symbol systems
- 5–10 harder solved records
- 3–10 linked-only records reserved for a secondary evaluation pack

### Stratification variables
Try to cover variation in:
- cipher family
- symbol inventory
- manuscript quality
- plaintext language
- century or scribal style
- known-key vs solved-without-key
- presence of inline plaintext or cleartext
- short vs long texts

---

## 17. Benchmark Splits

For the MVP, keep splits simple.

### Recommended initial split
- **dev set**: 10–20 items
- **test set**: 15–40 items

A training split is optional for the first release. Many tools will be zero-shot or externally trained anyway.

If a training split is included, keep it separate and clearly mark:
- real-world training items
- synthetic training items

Never allow duplicates or near-duplicates across splits.

---

## 18. Tooling to Build Early

The first engineering tasks should be lightweight.

### Needed scripts
1. `validate_manifest.py`
   - verifies file presence and schema conformity

2. `normalize_symbols.py`
   - converts diplomatic transcription to canonical token form

3. `score_transcription.py`
   - computes transcription metrics

4. `score_plaintext.py`
   - computes decrypt metrics

5. `package_release.py`
   - prepares open and linked releases

### Nice-to-have
- visual inspection notebook
- record browser
- transcription diff viewer

---

## 19. Risks and Mitigations

### Risk 1: Rights complexity blocks release
**Mitigation:** maintain open and linked releases from day one

### Risk 2: Solved status is overstated
**Mitigation:** use explicit solution labels and require verification notes

### Risk 3: Normalization introduces curator bias
**Mitigation:** publish deterministic normalization rules and retain diplomatic text

### Risk 4: Benchmark is too easy
**Mitigation:** stratify by difficulty and include mixed symbol systems

### Risk 5: Benchmark is too small to be meaningful
**Mitigation:** frame the MVP as a format and curation proof-of-concept, not the final corpus

---

## 20. Proposed MVP Milestones

### Milestone 1: Specification
Deliverables:
- benchmark scope
- record schema
- inclusion rules
- rights policy
- evaluation plan

### Milestone 2: Candidate pool
Deliverables:
- 100–200 candidate records logged
- initial rights and solved-status triage

### Milestone 3: Curated core set
Deliverables:
- 25–75 scored records
- complete manifests
- transcriptions and plaintext aligned

### Milestone 4: Evaluation harness
Deliverables:
- scoring scripts
- validation scripts
- documentation

### Milestone 5: Public release
Deliverables:
- open release package
- linked release package
- README and benchmark paper draft skeleton

---

## 21. Suggested 6-Week MVP Schedule

### Week 1
- finalize schema
- define normalization rules
- define rights classes
- create candidate manifest template

### Week 2
- collect candidate records
- perform initial rights triage
- mark likely solved examples

### Week 3
- extract images and source text
- build diplomatic transcription pipeline
- start canonical normalization

### Week 4
- verify plaintext and solved status
- review difficult cases
- remove weak candidates

### Week 5
- finalize 25–75 item set
- implement scoring and validation scripts
- create dev/test splits

### Week 6
- package benchmark
- write README and documentation
- run pilot evaluation on a small set of tools

---

## 22. Immediate Next Steps

The next concrete actions should be:

1. **Source audit** (1–2 hours per source): Estimate realistic yield from DECRYPT, HCPortal, ICDAR. Characterize what each source actually provides and how to access it.
2. **Freeze the schema** (`schema.json`)
3. **Define candidate manifest format** (see Section 22a below)
4. **Write normalization rules draft** — even a rough version will expose edge cases. Treat this as a Week 1 priority.
5. **Pick 10 pilot candidates** biased toward diversity (different cipher types, sources, centuries)
6. **Run the full pipeline on those 10** — image → diplomatic → canonical → plaintext alignment → QC
7. **Retrospective**: What broke? What took longer than expected? Revise the plan.

That 10-record pilot is important. It will expose:
- rights problems
- page/transcription alignment issues
- normalization edge cases
- evaluation bugs

before the benchmark grows.

---

## 22a. Candidate Manifest Format

The candidate manifest (`candidate_manifest.csv`) tracks every candidate record through the collection funnel, including rejected records (with reasons).

### Required columns

| Field | Type | Purpose |
|---|---|---|
| `candidate_id` | string | Unique tracking ID |
| `source` | string | DECRYPT / HCPortal / ICDAR / other |
| `source_record_id` | string | ID or reference in the original source |
| `source_url` | string | URL to the source record |
| `image_available` | bool | Is at least one usable page image available? |
| `image_rights` | enum | `open` / `unclear` / `restricted` |
| `solution_available` | bool | Does a verified decipherment exist? |
| `solution_type` | enum | `plaintext_in_source` / `published_scholarly` / `key_only` / `none` |
| `solution_reference` | string | Citation or URL for the decipherment |
| `page_alignment` | enum | `aligned` / `needs_work` / `unclear` / `na` |
| `cipher_type` | string | Best guess at cipher family |
| `plaintext_language` | string | ISO 639 code |
| `funnel_status` | enum | `candidate` / `extracting` / `normalizing` / `reviewed` / `accepted` / `rejected` |
| `rejection_reason` | string | If dropped, why |
| `notes` | string | Free text |

### Usage
- Every record discovered during Phase 1 gets a row, even if immediately rejected
- Update `funnel_status` as the record progresses through the pipeline
- This manifest becomes the living dashboard for curation progress

---

## 23. Recommended First Deliverables

To start the project, produce these four documents/files:

1. `benchmark_spec.md`
2. `schema.json`
3. `candidate_manifest.csv`
4. `normalization_rules.md`

The present document can serve as the initial `benchmark_spec.md`.

---

## 24. Decision Summary

### Recommended MVP strategy
Build a **small, solved-first, page-level benchmark** with:
- real historical sources
- paired images and transcriptions
- canonicalized symbol streams
- verified plaintext
- separate open and linked releases
- three evaluation tracks

### Why this is the right MVP
It is:
- practical
- publishable
- extensible
- legally safer
- useful both to OCR researchers and cryptanalysis researchers

It also avoids the main failure mode: trying to solve scale, licensing, normalization, and evaluation all at once.

---

## 25. Optional Extension After MVP

Once the MVP is stable, add:
- unsolved challenge appendix
- line-level annotations
- symbol bounding boxes
- richer cipher-family labels
- multilingual plaintext normalization
- human baselines
- synthetic augmentation pack
- benchmark leaderboard and submission format

---

## 26. One-Sentence Project Pitch

**Build a small but rigorous benchmark of solved historical cipher documents, pairing manuscript images with standardized transcriptions and verified plaintext so that AI-enabled tools can be evaluated fairly on OCR, cryptanalysis, and end-to-end decoding.**
