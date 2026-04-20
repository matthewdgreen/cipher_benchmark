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
- Manifest: `benchmark/manifest/records.jsonl`
- Schema: `benchmark/manifest/schema.json`
- Splits: `benchmark/splits/*.jsonl`
- Source docs: `benchmark/docs/`
- Raw/staging data: `data_staging/`

As of April 20, 2026, the manifest contains 896 records:

- Borg: 397
- Copiale: 101
- DECODE/Gallica: 155
- Multilingual synthetic simple substitution: 240
- Tool-bundled parity records: 3

Tool-bundled coverage is intentionally still partial. The benchmark currently
has only three imported Zenith smoke records (`goldbug`, `horacemann`,
`zodiac408`). The downloaded tool corpora contain more material:

- Zenith source checkout includes 11 cipher JSON resources: `goldbug`,
  `hamptonfull`, `horacemann`, `jameshampton1`, `kryptos1`, `kryptos2`,
  `kryptos3`, `kryptos4`, `zodiac340-original`, `zodiac340-transformed`,
  and `zodiac408`.
- zkdecrypto-lite includes 24 bundled `cipher/*.txt` resources.

Future curation should inventory these files before importing them. Add solved
and scorable records to parity splits; add unsolved, transformed, unsupported,
or special-family ciphers only with explicit diagnostic metadata.

## Working Rules

- Treat `benchmark/manifest/records.jsonl` as the source of truth for counts.
- Keep benchmark curation separate from Decipher solver code.
- Prefer adding explicit metadata over inferring intent from file names.
- Do not mark external-tool corpus coverage as complete merely because the
  `tool_builtins` source exists; track which bundled files have actually been
  imported.
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
