# Track D: Image-to-Hypothesis Evaluation Rubric

Version 0.1 — 2026-07-19

Track D evaluates research outputs for unsolved or disputed ciphers where no
accepted plaintext exists. It does **not** convert plausibility into a claim of
solution. Submissions should be archived as falsifiable research artifacts,
not ranked by resemblance to a preferred decipherment.

## Required Submission Packet

1. Benchmark record ID and exact image/transcription inputs.
2. Tool/model version, configuration, random seeds, and elapsed runtime.
3. Claimed output type: transcription, structural diagnosis, cipher-family
   hypothesis, partial mapping, reading-order hypothesis, or candidate text.
4. Evidence derived from the target, separately identified external context,
   and any human intervention.
5. Machine-readable output where applicable: token sequence, key/mapping,
   transform pipeline, confidence per symbol/span, and rejected alternatives.
6. A falsification section stating what observation would weaken or reject the
   hypothesis.

## Scoring

Each dimension is scored 0–4. Report the six-dimensional vector and total out
of 24; do not report only the total.

| Dimension | 0 | 2 | 4 |
|---|---|---|---|
| Reproducibility | Inputs or procedure missing | Broad procedure reproducible with gaps | Exact inputs, versions, seeds, and outputs reproduce |
| Evidence discipline | Unsupported assertion or hidden evidence | Evidence present but provenance/roles partly mixed | Target-derived, contextual, and human evidence clearly separated |
| Internal consistency | Contradictory mapping/structure | Mostly consistent with unexplained exceptions | Constraints replay cleanly; exceptions explicitly modeled |
| Explanatory coverage | Isolated anecdote | Explains a meaningful subset | Explains the claimed scope with quantitative coverage and residuals |
| Robustness | Single unconstrained fit | Some alternatives/perturbations tested | Competing hypotheses, ablations, and sensitivity tests reported |
| Falsifiability | Cannot be tested | Some checkable predictions | Clear risky predictions and rejection criteria |

### Score interpretation

- 0–7: unsupported output; archive only if useful as a failure example.
- 8–13: exploratory lead requiring substantial corroboration.
- 14–18: reproducible research hypothesis worth independent testing.
- 19–24: strong methodological result; still not a decipherment without
  independent validating evidence.

## Optional Task-Specific Checks

### Transcription

- Grid/line geometry is preserved.
- Uncertain, damaged, and illegible glyphs remain marked as such.
- Repeated-glyph identity is audited against source images.
- Normalization is separated from diplomatic observation.
- Inter-annotator agreement or adjudication is reported when available.

### Structural or cipher-family hypothesis

- Null model and alternative families are compared.
- Statistics account for text length and transcription uncertainty.
- Reading order, tokenization, and symbol-merging choices are ablated.
- The hypothesis predicts behavior on held-out spans or related records.

### Candidate plaintext or partial key

- The complete mapping/transform replays from the published transcription.
- Unmapped and contradictory symbols are visible rather than silently fixed.
- Language fluency is not treated as independent proof when used for search.
- Cribs and contextual hints are disclosed.
- Candidate stability across seeds and nearby transcription variants is shown.

## Disqualifying Overclaims

A submission receives no aggregate Track D score if it exposes withheld target
ground truth, presents benchmark plaintext as solver evidence, fabricates
source provenance, or calls an unsolved cipher “solved” solely from subjective
readability. Preserve the artifact for audit and label the failure explicitly.

## Review Process

Two reviewers should score independently, then record both original vectors
and an adjudicated vector. Material disagreement (two or more points on any
dimension) requires a short written rationale. Reviewers should disclose prior
knowledge of famous targets because memorized solutions or claims can affect
judgment even when no accepted ground truth exists.
