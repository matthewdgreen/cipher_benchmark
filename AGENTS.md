# Cipher Benchmark — AGENTS.md

Project context for Codex sessions working in this repository.

## What This Is

A benchmark dataset for evaluating classical-cipher research tools across:

- Track A: image to transcription
- Track B: transcription to plaintext
- Track C: image to plaintext

The sibling `../decipher` repository contains solver code, agent tools, external
baseline harnesses, and validation scripts. This repository contains benchmark
data, curation scripts, manifests, splits, images, transcriptions, and plaintext.

## Current Shape

- Main dataset root: `benchmark/`
- Main manifest: `benchmark/manifest/records.jsonl`
- Main schema: `benchmark/manifest/schema.json`
- Splits: `benchmark/splits/*.jsonl`
- Source docs: `benchmark/docs/`
- **Unsolved area:** `benchmark/unsolved/` (parallel, relaxed schema; see
  `benchmark/unsolved/README.md` for scope and evaluation model).
- Raw/staging data: `data_staging/`

As of April 28, 2026, the main manifest contains 898 records:

- Borg: 397
- Copiale: 101
- DECODE/Gallica: 155
- Multilingual synthetic simple substitution: 240 (all flagged `synthetic: true`)
- Tool-bundled parity records: 3
- Curated Zodiac records: 2

The unsolved area currently contains seed Voynich folios, Zodiac diagnostic
variants, and Scorpion S1/S5 records. It also has a Voynich intake script ready
(`scripts/create_voynich_intake.py`, ~211 folios). Records produced there live
in `benchmark/unsolved/manifest/records.jsonl` and validate against a separate
schema.

Scorpion S1/S5 are documentation-rich exploratory records under
`benchmark/unsolved/sources/scorpion/`. They include local copies of the public
cipher images, a released-letter excerpt as an associated document, tentative
v0.2 diplomatic/canonical transcriptions supplied from a preliminary
family-label pass, and a split at
`benchmark/unsolved/splits/scorpion_tests.jsonl`. There is also a separate
synthetic hypothesis split at `benchmark/unsolved/splits/scorpion_synthetic_tests.jsonl`
that concatenates S1+S5 under a shared global v0.2 family-label alphabet.
Treat those transcriptions as usable for initial solver experiments only; do
not make final benchmark claims until a vetted glyph-ID pass reconciles the
public source's reported symbol counts.

Tool-bundled coverage is intentionally still partial. The benchmark currently
has three imported Zenith smoke records (`goldbug`, `horacemann`,
`zodiac408`) plus a separate curated Zodiac source with global glyph IDs for
Z408/Z340. The downloaded tool corpora contain more material:

- Zenith source checkout includes 11 cipher JSON resources: `goldbug`,
  `hamptonfull`, `horacemann`, `jameshampton1`, `kryptos1`, `kryptos2`,
  `kryptos3`, `kryptos4`, `zodiac340-original`, `zodiac340-transformed`,
  and `zodiac408`.
- zkdecrypto-lite includes 24 bundled `cipher/*.txt` resources.

Future curation should inventory these files before importing them. Add solved
and scorable records to parity splits; add unsolved, transformed, unsupported,
or special-family ciphers only with explicit diagnostic metadata — or, for
genuinely unsolved items, route to `benchmark/unsolved/` instead of the main
manifest.

## Schema (as of 2026-04-23)

The main schema has been tightened through a rollout labeled S1–S7
(commits `a80adee` → `d0c56f8` on 2026-04-23). Current invariants:

- **Required fields:** `id`, `source`, `status`, `task_tracks`, `rights_class`.
- **Conditional:** non-synthetic records must carry at least one of
  `source_url` / `source_record_id` (`allOf`/`if`/`then`).
- **Synthetic provenance:** records may set `synthetic: true` and carry a
  `generation_config` object (`{generator, seed, params}`). All 240 existing
  synthetic records are flagged.
- **Manuscript page normalization:** `manuscript_page` is `type: string` only
  (integer pages serialize as `"42"`, folio notation as `"f3r"`).
- **Image provenance:** optional `image_provenance` object captures IIIF
  service URL, requested width, folio offset, fetch date. Prefer populating
  this over baking provenance into free-text `curation_notes`.
- **Date bounds:** optional `date_earliest_year` / `date_latest_year` integers
  complement the free-text `date_or_century` for filtering.

Idempotent migration helpers:

- `scripts/backfill_synthetic_flag.py` — marks records from `*_synth` sources
- `scripts/backfill_rights_class.py` — refuses to guess for non-synthetic
  records; safe to re-run
- `scripts/coerce_manuscript_page_to_string.py` — one-way int→str coercion

When adding a new source, the ordering is: (a) run any intake script under
`scripts/create_*.py`, (b) run the backfills if the importer didn't set the
required fields, (c) run the validator.

## Working Rules

- Treat `benchmark/manifest/records.jsonl` as the source of truth for counts
  in the main benchmark; `benchmark/unsolved/manifest/records.jsonl` is
  parallel and separately owned.
- Keep benchmark curation separate from Decipher solver code.
- Prefer adding explicit metadata over inferring intent from file names.
- Do not mark external-tool corpus coverage as complete merely because the
  `tool_builtins` source exists; track which bundled files have actually been
  imported.
- Do not route unsolved historical ciphers into the main manifest — use the
  unsolved area. The main schema assumes scorable ground truth is available
  or in progress.
- For Scorpion specifically, keep the current v0.2 family-label transcriptions
  marked as tentative. They may over-merge visually distinct glyphs and should
  be replaced or supplemented by a vetted global glyph-ID transcription before
  any headline evaluation.
- Run Decipher's validator after manifest/schema/split changes:

```bash
cd ../decipher
PYTHONPATH=src .venv/bin/python scripts/validate_benchmark.py \
  ../cipher_benchmark/benchmark
```

## Agentic Parity Metadata

Parity-focused split definitions may include optional fields beyond the basic
split schema:

- `parity_family`
- `recommended_agent_tool`
- `baseline_solvers`
- `expected_baseline_status`
- `expected_min_char_accuracy`
- `known_cipher_type`
- `word_boundaries`

These fields document what non-agentic capability a clean task is testing and
what first-class agent tool should be used.

## Agentic Advantage Metadata

Agentic-advantage splits should include an explicit hypothesis, for example:

- `agentic_hypothesis`
- `stressors`
- `baseline_expected_failure_mode`

Only use these after parity has been checked. The aim is to identify cases where
context, OCR/transcription repair, diagnosis, branching, cribs, or manuscript
metadata let the agent outperform native non-agentic solvers.

## Context Layers And Associated Documents

Benchmark records may carry tiered `context_layers` for controlled
context-aware evaluation:

- `minimal`: archival/provenance facts only, no cipher-type or plaintext hints.
- `standard`: language, cipher-family, symbol, length, and transcription facts.
- `historical`: stronger non-solution background, such as manuscript genre,
  author/source family, or surrounding historical events.

Each layer must disclose whether it contains a solution, plaintext hint, or
cipher-type hint. Long companion material should not be pasted into
`context_layers`; put it in `associated_documents` with a concise summary and
file/source references. Solver tooling can later expose these documents through
explicit policies or on-demand agent tools.

Use `related_records` for links to same-manuscript, same-author,
same-key-family, or known-solution neighbors. Solution-bearing related records
must only be exposed under an explicit related-solution policy.
