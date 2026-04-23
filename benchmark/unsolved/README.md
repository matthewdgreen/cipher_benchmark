# Unsolved Cipher Area

A parallel benchmark area for historical ciphers that have **no widely accepted
solution**. Unlike the main benchmark (where records have verified plaintext
and can be scored automatically), records here are organized for tool
evaluation without ground-truth scoring.

## Why this area exists

LLM-enabled cipher tools will inevitably be pointed at famous unsolved ciphers
(Voynich, Zodiac Z13/Z32, Kryptos K4, etc.). Rather than leave each tool to
re-scrape and re-preprocess these corpora ad hoc, this area gives a
standardized intake with:

  * Canonical images (from the authoritative source archive, at fixed
    resolution)
  * Canonical transcriptions where a community-standard one exists
    (e.g. EVA/ZL for Voynich)
  * Metadata flagging what partial evidence *does* exist
    (`partial_solution_evidence` field)
  * A per-source README explaining rights, provenance, and known caveats

This makes it possible to report results like "tool X produced candidate
transcription Y for Voynich folio f1r" in a form other researchers can
reproduce and compare.

## Evaluation model

Three modes, depending on what signal is available:

  1. **Scored against adjacent solved records.** If a tool does well on the
     solved subset of a corpus (e.g. DECODE-solved letters from a given
     correspondent), we can report its performance on the unsolved subset
     of the same corpus as a consistency proxy — but we explicitly do NOT
     claim it tells us whether the output is correct.

  2. **Scored against partial evidence.** When
     `partial_solution_evidence = interlineation_visible` or
     `partial_plaintext_published`, we score the tool's output against that
     partial signal — a legitimate quantitative eval even without full
     ground truth.

  3. **Track D: `image2hypothesis`.** Open-ended. Tool produces a candidate
     transcription, partial decryption, statistical characterization, or
     structural hypothesis; result is archived with provenance. No
     automated score. Intended for human rubric review or community
     assessment.

## Scope rules

Include:
  * Documents with no widely accepted solution (`status: unsolved`)
  * Documents with one or more disputed claimed solutions (`status: disputed`)
  * Documents partially solved with remaining unsolved sections (`status: partial`)

Exclude:
  * Documents whose authenticity as ciphers is widely rejected
    (e.g. the more speculative Bacon-Shakespeare claims)
  * Fictional / art-project ciphers with no pretense of concealing plaintext
    (Codex Seraphinianus)
  * Recent puzzle / ARG ciphers (Cicada 3301) — different genre,
    different evaluation
  * Lost documents known only from reconstructions (Oak Island 90-foot stone)

## Source tiers (planned)

**Tier 1 (bulk corpora):**
  * `voynich/` — Beinecke MS 408, ~240 pages. (This PR: intake started.)
  * `decode_undecrypted/` — filtered DECODE records marked `undecrypted`,
    ~1,200 candidates. Blocked on DECODE login.
  * `rohonc/` — Hungarian Academy of Sciences, ~450 pages. Rights pending.

**Tier 2 (famous short ciphers — challenge set):**
  * `famous_short/` — Zodiac Z13/Z32, Kryptos K4, Dorabella, D'Agapeyeff,
    Beale 1 & 3, Somerton Man, Ricky McCormick, Scorpion S1–S5,
    Shugborough, Feynman #2/#3, Paul Rubin, Henry Debosnys.
    One record per cipher.

## Layout

```
benchmark/unsolved/
  manifest/
    schema.json          # this area's schema (relaxed)
    records.jsonl        # unsolved records, parallel to main records.jsonl
  sources/
    voynich/
      images/            # IIIF-fetched page images
      transcriptions/    # EVA/ZL transcriptions
      metadata/          # per-folio metadata
      README.md          # corpus-specific notes
    decode_undecrypted/
    rohonc/
    famous_short/
```
