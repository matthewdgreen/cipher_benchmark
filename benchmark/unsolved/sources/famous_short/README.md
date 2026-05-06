# Famous Short Unsolved Ciphers

This source bucket holds compact, well-known unsolved or disputed ciphers that
are useful for qualitative agent tests and unknown-cipher diagnostics. Records
in this bucket should not be imported from bundled solver examples alone unless
the record is explicitly marked as a placeholder.

## Beale 1 and Beale 3

Imported records:

- `beale_1`
- `beale_3`

The canonical transcriptions are single-line whitespace-separated numeric
token streams. They intentionally contain no word-boundary markers.

Primary provenance is the public Beale Papers transcription hosted by The
Cipher Foundation, which describes its text as following the 1885 pamphlet
copy in the Internet Archive tradition. Local AZdecrypt bundled files were
used only as convenience cross-check material during import.

Beale cipher 2 is not included here as an unsolved target because it has a
traditional accepted solution using the Declaration of Independence as the key
text. Beale 1 and Beale 3 remain without widely accepted solutions.

## D'Agapeyeff

Imported record:

- `dagapeyeff_cipher`

The target transcription preserves the public five-digit grouping of the
challenge cipher from Alexander D'Agapeyeff's 1939 *Codes and Ciphers*. A
two-digit-pair transcription and related Polybius worked-example files are
stored as associated hypothesis/context material only. They are not ground
truth and should not be treated as solver-verified intermediate layers.

Rights are marked `hold_for_review` because the original source book is not
assumed to be public-domain. The record is intended for qualitative
unknown-cipher, numeric-code, fractionation, Polybius, null/error, and
diagnosis-only experiments.

## Feynman Challenge Ciphers #2 and #3

Feynman #2 and #3 have moved out of this unsolved source bucket and into the
main benchmark under `benchmark/sources/feynman/` as `solved_probable`
claimed-solution calibration records. The ordinary context tiers do not expose
the plaintext or solution-bearing method parameters.
