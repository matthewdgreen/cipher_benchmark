# Boys' Life 1931 Hood Treasure Hunt Ciphers — Source Note

## Context

Four cipher puzzles appeared as full-page paid advertisements by the **Hood
Rubber Company** (Watertown, Mass.) in the April, May, June, and July 1931
issues of *Boys' Life* magazine. Each advertisement invited readers to solve
the cipher, which "tells where to look for buried treasure," and enter a
contest by mailing their solution and a short paragraph to Hood.

The advertisement series was titled the **Hood Treasure Hunt**. All four ads
are structurally identical: the cipher is displayed at the top of the page, a
prize list is given (two best answers win major prizes; 50 next-best win minor
prizes), and the five Hood Points are listed as a key constraint:

1. **COMFORT TOE** — comfort fit
2. **STURDY UPPERS** — leather upper stock
3. **SURE-FOOTED SOLES** — vulcanised rubber outsoles
4. **HYGIENIC INSOLE** — cushion insole
5. **FIRM ARCH SUPPORT** — arch reinforcement

Rules (paraphrased from the ads):

1. Solve the cipher message (it describes where to look for a hidden
   treasure). Hood mailed a free booklet, *Secret Writing*, explaining several
   cipher systems including the one used.
2. The message contains two or more "key words" appearing in one of the five
   Hood Points. Identify which Hood Point.
3. Write a paragraph (≤ 100 words) explaining why that Hood Point makes Hood
   canvas shoes a good value.
4. Mail solution + paragraph + name/address/age to Hood Rubber Co., Watertown,
   Mass. before the deadline.

Prizes for each month were announced two to four months later:
- April → October 1931 issue prize-winners page
- May, June, July → similar later issues

The October 1931 issue confirms prize winners were awarded but does **not**
publish the plaintext solutions. The *Secret Writing* booklet distributed by
Hood is not known to survive in any public archive.

## Cipher Types

| Issue  | Type            | Chars | Grid       | AZdecrypt folder |
|--------|-----------------|------:|------------|------------------|
| April  | Transposition   |    90 | 5 × 18     | Transposition/   |
| May    | Substitution    |    83 | 5 rows     | Substitution/    |
| June   | Transposition   |   100 | 5 × 20     | Transposition/   |
| July   | Substitution    |   156 | 6 rows     | Substitution/    |

The April and June ciphers display the same letters as the plaintext, just
transposed. The May cipher uses standard uppercase Latin letters as cipher
symbols. The July cipher uses a mixed symbol set (digits and punctuation)
identical to or closely related to Poe's Gold Bug (1843) cipher alphabet.

## Transcription Sources

The ciphertexts come from AZdecrypt's bundled cipher files:
- `Ciphers/Transposition/Boys' Life April 1931 page 31.txt`
- `Ciphers/Substitution/Boys' Life May 1931 page 35.txt`
- `Ciphers/Transposition/Boys' Life June 1931 page 35.txt`
- `Ciphers/Substitution/Boys' Life July 1931 page 29.txt`

These were cross-checked against the actual magazine pages obtained via
Internet Archive scans (archive.org identifiers below). The magazine pages
display the same characters in 9- or 10-character groups; the AZdecrypt
grouping matches the magazine content.

AZdecrypt places these in its **Substitution/** and **Transposition/**
folders (not its **Unsolved/** folder), implying community solutions exist,
but no independent plaintext sources have been located.

## Archive.org Sources

| Issue | Identifier | Magazine page |
|-------|-----------|--------------|
| April 1931 | `sim_boys-life_1931-04_21_4` | 31 |
| May 1931   | `sim_boys-life_1931-05_21_5` | 35 |
| June 1931  | `sim_boys-life_1931-06_21_6` | 35 |
| July 1931  | `sim_boys-life_1931-07_21_7` | 29 |

## Rights

*Boys' Life* was published by the Boy Scouts of America. The 1931 issues are
well past the US copyright term. The Hood Rubber Company advertisements are
similarly public domain. `rights_class: open`.

## Solution Constraints

For all four ciphers the plaintext must satisfy:
- It describes a treasure location.
- It contains ≥ 2 keywords matching one of the five Hood Points.

Letter feasibility analysis for the transposition ciphers (same multiset of
letters in cipher and plaintext):
- **April**: letters present include all needed for "SURE FOOTED SOLES"; the
  letter M is absent from the ciphertext, ruling out "FIRM", "COMFORT", and
  "HYGIENIC".
- **June**: letters present are consistent with "COMFORT TOE" and
  "SURE FOOTED SOLES"; M is present, so all points are feasible.
