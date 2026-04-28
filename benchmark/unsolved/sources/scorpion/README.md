# Scorpion Ciphers

This unsolved-source packet records the two publicly released Scorpion
ciphertexts, usually identified as S1 and S5, plus the accompanying released
letter text that appears in curated public sources.

## Source Status

Primary public source:

- The Cipher Foundation, "Scorpion Ciphers":
  https://cipherfoundation.org/modern-ciphers/scorpion-ciphers/

Secondary public commentary/source mirror:

- Cipher Mysteries, "Scorpion Ciphers":
  https://ciphermysteries.com/other-ciphers/scorpion-ciphers

Official-source lead:

- FBI FOIA log entry for "Scorpion Ciphers and Letters", FOIA number 1507727,
  opened 2021-10-28. The actual released packet was not located in the public
  Vault during initial curation.

The public page states that only two ciphertexts and a handful of pages of text
have been released. It identifies S1 as a 10 x 7 grid with 53 unique symbols
among 70 cells, and S5 as a 12 x 15 grid with 155 unique symbols among 180
cells.

## Curation Notes

The benchmark currently stores source URLs, structured metadata, local copies
of the two linked public images, and the released accompanying letter text.
Image/text redistribution rights remain unverified, so the records stay
`linked_only`.

The directory also includes a ChatGPT-assisted transcription v0.2 in CSV, JSON,
and Markdown form. From that, we derive two layers:

- `*_position_ids_v0_2.diplomatic.txt`: one unique position ID per cell,
  useful for audit and grid-order reference only.
- `*_family_v0_2.canonical.txt`: repeated S-tokens derived from the
  exploratory `family_label_v0_1` field, suitable for initial Decipher
  experiments.
- `scorpion_s1_s5_shared_family_hypothesis_v0_2.canonical.txt`: a synthetic,
  hypothesis-only S1+S5 composite using a single global v0.2 family-label
  alphabet. Shared tentative family labels receive the same S-token across S1
  and S5. This is not an original document and should only be used to test a
  possible shared-key/shared-alphabet hypothesis.

Important caveat: the family-label layer over-merges visual variants relative
to the public unique-symbol counts. S1 is reported as 53 unique symbols but
the v0.2 family layer has 48. S5 is reported as 155 unique symbols but the
v0.2 family layer has 121. The synthetic S1+S5 composite has 250 tokens and
148 global v0.2 family-label symbols, including 21 tentative labels shared by
both component ciphertexts. Use all of this for exploratory solver runs only;
a future glyph-normalization pass should create a proper Scorpion glyph ID map
from the source images before any benchmark claim.
