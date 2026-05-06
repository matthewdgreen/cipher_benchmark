# AZdecrypt Unsolved Corpus Intake

This is a working intake ledger for examples bundled in the local AZdecrypt
checkout at:

`../decipher/other_tools/azdecrypt-src/AZdecrypt/Ciphers/Unsolved`

The purpose is **not** to import AZdecrypt's copies blindly. Each candidate
should be worked in this order:

1. Identify the cipher and decide whether it is still unsolved, disputed,
   solved, partial, or out of scope.
2. Look for a better canonical source: archive scan, official agency page,
   creator/source publication, Cipher Foundation page, Cipher Mysteries page,
   Internet Archive scan, or other stable public corpus.
3. Check rights/redistribution. Prefer `source_url` + linked transcription when
   local redistribution is unclear.
4. Compare the canonical source against the AZdecrypt ciphertext. If they
   differ, preserve both with explicit provenance rather than silently merging.
5. Import to `benchmark/unsolved/manifest/records.jsonl` only after the record
   has source/status/rights notes. If no better source can be found, create a
   temporary placeholder record that clearly says the local transcription came
   from AZdecrypt and mark `rights_class: hold_for_review`.

The `AZdecrypt status` column means "the file appears in AZdecrypt's
`Unsolved` directory"; it is not an independently verified scholarly claim.

## Intake Status Legend

| Status | Meaning |
|---|---|
| `already_present` | A related record already exists in `benchmark/unsolved`; check whether AZdecrypt adds anything useful. |
| `source_found` | A better source/status reference has been found, but no record has been imported yet. |
| `needs_source_check` | Candidate is known from AZdecrypt but needs provenance/status research. |
| `placeholder_candidate` | If no better source appears, AZdecrypt may be usable only as a clearly marked temporary transcription. |
| `defer_or_exclude` | Likely too short, out of scope, or too provenance-weak for near-term import. |

## First-Pass Ledger

| AZdecrypt file | Length | Proposed ID | Intake status | Current status assessment | Better/canonical source lead | Rights / import note | Next action |
|---|---:|---|---|---|---|---|---|
| `1916 train station robbery cryptogram.txt` | 94 | `train_station_robbery_1916` | `needs_source_check` | Unknown; AZdecrypt labels unsolved. | Need source research. | Do not import from AZdecrypt until source is identified. | Search newspaper/archive origin and current status. |
| `Allen Benjy 2010 challenge.txt` | 708 | `allen_benjy_2010_challenge` | `needs_source_check` | Unknown challenge status. | Need source research. | Likely modern challenge; rights unclear. | Identify author/source and whether solved. |
| `Beale 1.txt` | 1336 | `beale_1` | `imported` | Beale cipher 1 is traditionally treated as unsolved/disputed. | Cipher Foundation Beale Papers transcription; original 1885 pamphlet via Internet Archive; local AZdecrypt copy used as cross-check. | Imported under `sources/famous_short/` with public-pamphlet provenance and numeric-token canonical transcription. | Live unsolved split row: `beale_1_unsolved`. |
| `Beale 3.txt` | 1505 | `beale_3` | `imported` | Beale cipher 3 is traditionally treated as unsolved/disputed. | Same Beale sources as above; local AZdecrypt copy used as cross-check. | Imported under `sources/famous_short/` with public-pamphlet provenance and numeric-token canonical transcription. | Live unsolved split row: `beale_3_unsolved`. |
| `Blitz cipher page 7.txt` | 470 | `blitz_cipher_p7` | `source_found` | Reported as unsolved/provisional transcription. | Cipher Foundation Blitz Ciphers page; Cipher Mysteries original discussion. | Images/transcriptions need rights review; likely linked-only or hold-for-review. | Compare AZdecrypt page text against public provisional transcription. |
| `Blitz cipher page 8.txt` | 159 | `blitz_cipher_p8` | `source_found` | Reported as unsolved/provisional transcription. | Same Blitz sources as above. | Same rights caveat. | Import only if source transcription can be cited cleanly. |
| `Copenhagen cryptogram.txt` | 101 | `copenhagen_cryptogram` | `needs_source_check` | Unknown; probably short unsolved challenge. | Need source research. | Do not import until identified. | Find canonical source/status. |
| `D'Agapeyeff.txt` | 392 | `dagapeyeff_cipher` | `imported` | Widely treated as unsolved; may include transcription/encoding error. | Original *Codes and Ciphers* first edition; Hyde & Rugg discussion; public transcription. | Imported under `sources/famous_short/` as `hold_for_review`; target preserves five-digit groups, with AZdecrypt two-digit-pair and Polybius files stored only as hypothesis/context material. | Live unsolved split row: `dagapeyeff_cipher_unsolved`. |
| `DCT Reloaded 3.txt` | 1100 | `dct_reloaded_3` | `needs_source_check` | AZdecrypt labels unsolved; file includes German plaintext/key-length hints. | Need source research, likely modern DCT challenge. | Modern challenge rights likely unclear. | Identify challenge author/source before importing. |
| `Dorabella.txt` | 87 | `dorabella_cipher` | `source_found` | Famous disputed/unsolved Elgar note; many claimed solutions, no consensus. | Elgar/Dora Penny historical sources; Cipher Foundation/Cipher Mysteries/other stable public pages. | Original image may have estate/archive rights; transcription may be linked-only or hold-for-review. | Create proper record rather than only docs packet; compare against existing Decipher qualitative material. |
| `Feynman 2.txt` | 261 | `feynman_2` | `promoted_to_solved_probable` | Historically presented as unsolved, but codewarrior0 published a 2023 claimed solve with strong re-encipherment evidence. | Cipher Foundation Feynman Challenge Ciphers; codewarrior0 claimed solution; Housman plaintext source. | Imported in the main benchmark under `sources/feynman/` as `solved_probable`; claimed plaintext and method metadata are stored, while blind/standard context avoids solution-bearing details. | Live main split row: `feynman_2_alternating_substitution`. |
| `Feynman 3.txt` | 231 | `feynman_3` | `promoted_to_solved_probable` | Same as Feynman 2; claimed solution re-enciphers almost completely under the published partial alphabets/method. | Cipher Foundation Feynman Challenge Ciphers; codewarrior0 claimed solution; CaltechAUTHORS Feynman paper source. | Imported in the main benchmark under `sources/feynman/` as `solved_probable`; claimed plaintext and method metadata are stored, while blind/standard context avoids solution-bearing details. | Live main split row: `feynman_3_alternating_substitution`. |
| `GUN WA 1889.txt` | 77 | `gun_wa_1889` | `needs_source_check` | Unknown short challenge. | Need source research. | Do not import until identified. | Find source/status. |
| `Glurk (Beale 3 emulation challenge).txt` | 1591 | `glurk_beale3_emulation` | `placeholder_candidate` | Likely modern synthetic/emulation challenge, not historical unsolved. | Need source research; may originate from AZdecrypt community. | Import only as synthetic/challenge if permission/provenance is clear. | Defer until codebook/book-cipher tooling needs this. |
| `Helen Fouché Gaines.txt` | 125 | `helen_fouche_gaines` | `needs_source_check` | Unknown short challenge. | Need source research. | Rights/status unclear. | Find canonical source. |
| `IKLP long.txt` | 358 | `iklp_long` | `needs_source_check` | Unknown. | Need source research. | Rights/status unclear. | Find source/status or defer. |
| `IKLP short.txt` | 19 | `iklp_short` | `defer_or_exclude` | Too short for useful automated cryptanalysis unless paired with context. | Need source research if retained. | Likely not worth a standalone benchmark record. | Defer unless related to `IKLP long`. |
| `Kryptos 4 (Berlin clock clue).txt` | 108 | `kryptos_k4_berlin_clock_clue` | `already_present` | K4 remains without a public accepted cryptanalytic solution; recent reports say solution information has been privately discovered/auctioned, not publicly reproducible. | CIA/artist/Kryptos public pages; AP/Scientific American reporting for current status. | Benchmark already has `kryptos_k4`; clue-bearing variant should be associated document or context tier, not separate source unless useful. | Compare with existing K4 record and decide whether to add clue overlay. |
| `Kryptos 4.txt` | 97 | `kryptos_k4` | `already_present` | Present in unsolved benchmark. | Existing benchmark source plus public Kryptos references. | Already imported. | Verify AZdecrypt text matches existing canonical K4. |
| `Lawrence Public Library Cryptogram part 1.txt` | 451 | `lawrence_public_library_cryptogram_p1` | `needs_source_check` | Unknown; likely two-part related challenge. | Need source research. | Rights/status unclear. | Identify library/source and import paired records if credible. |
| `Lawrence Public Library Cryptogram part 2.txt` | 395 | `lawrence_public_library_cryptogram_p2` | `needs_source_check` | Same as part 1. | Need source research. | Same caveat. | Import with part 1 if source is found. |
| `Moustier St Martin.txt` | 76 | `moustier_st_martin` | `needs_source_check` | Unknown short symbolic/historical example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Moustier Virgin.txt` | 80 | `moustier_virgin` | `needs_source_check` | Unknown short symbolic/historical example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Nick Pelling challenge 2.txt` | 354 | `nick_pelling_challenge_2` | `source_found` | Likely challenge/discussion material from Cipher Mysteries; status must be checked per challenge. | Cipher Mysteries/Nick Pelling pages. | Website text is copyrighted; likely linked-only or hold-for-review unless permission is clear. | Identify exact challenge pages and solve status. |
| `Nick Pelling challenge 3.txt` | 276 | `nick_pelling_challenge_3` | `source_found` | Same as above. | Same. | Same. | Same. |
| `Nick Pelling challenge 4.txt` | 246 | `nick_pelling_challenge_4` | `source_found` | Same as above. | Same. | Same. | Same. |
| `Nick Pelling challenge 5.txt` | 246 | `nick_pelling_challenge_5` | `source_found` | Same as above. | Same. | Same. | Same. |
| `Nick Pelling challenge 6.txt` | 237 | `nick_pelling_challenge_6` | `source_found` | Same as above. | Same. | Same. | Same. |
| `Nick Pelling challenge 7.txt` | 222 | `nick_pelling_challenge_7` | `source_found` | Same as above. | Same. | Same. | Same. |
| `Paul Rubin.txt` | 459 | `paul_rubin_cipher` | `needs_source_check` | Unknown. | Need source research. | Rights/status unclear. | Find canonical source/status. |
| `Powers cryptogram.txt` | 96 | `powers_cryptogram` | `needs_source_check` | Unknown short example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Ricky McCormick page 1.txt` | 406 | `ricky_mccormick_note_1` | `source_found` | FBI/ACA failed to decipher; still treated as unsolved. | FBI image repository/news pages for notes; public FBI call for help. | FBI materials are likely usable as U.S. government source, but verify specific image/transcription handling. | Prefer FBI image as canonical source; create diplomatic transcription with uncertainty notes. |
| `Ricky McCormick page 2.txt` | 425 | `ricky_mccormick_note_2` | `source_found` | Same as page 1. | Same FBI sources. | Same. | Import paired records with associated case context. |
| `Scorpio 5.txt` | 397 | `scorpion_s5` | `already_present` | Related Scorpion S5 record already exists with tentative v0.2 transcription. | Existing benchmark Scorpion sources; public cipher images/letters. | Compare AZdecrypt "Scorpio" numeric family labels to our v0.2 transcription, but do not silently replace. | Add cross-check note if materially different. |
| `Taman Shud.txt` | 44 | `taman_shud_code` | `source_found` | The code itself remains unresolved/likely acrostic or shorthand; Somerton Man identity has changed status separately. | Cipher Foundation Somerton Man page; police scan/public case sources. | Short text; likely linked-only/hold-for-review depending image/transcription source. | Import as qualitative "too short / no overclaim" record. |

## Sources Found So Far

- Beale ciphers: Cipher Foundation Beale Papers transcription and public-domain
  1885 pamphlet scans are likely better canonical sources than AZdecrypt.
- D'Agapeyeff: the original 1939 *Codes and Ciphers* first edition is the
  source, but redistribution may be restricted; Hyde & Rugg and other public
  discussions are useful for status/context.
- Feynman ciphers: Cipher Foundation has the challenge texts and notes that
  #1 is solved; public 2023 claimed solutions for #2/#3 have been promoted to
  main-benchmark `solved_probable` calibration rows, not fully verified
  `solved_verified` rows.
- Kryptos K4: already present; recent public reporting says the solution
  information has been privately discovered/auctioned but is not publicly
  reproducible as an accepted cryptanalytic solution.
- Ricky McCormick: FBI source materials should be preferred over AZdecrypt.
- Blitz Ciphers and Nick Pelling challenges: likely better sourced from Cipher
  Foundation / Cipher Mysteries, but rights and exact pages need review.

## Import Notes

- `famous_short` is the natural source bucket for most of these once imported.
- Very short records such as Taman Shud, IKLP short, Zodiac 13-style examples,
  and Moustier variants should be marked as qualitative/diagnostic. They are
  useful for agent overclaim restraint, not ordinary automated scoring.
- Modern community challenge records should not be mixed with historical
  records unless their provenance and permissions are explicit.
- If an AZdecrypt placeholder is used, store the ciphertext under a clearly
  named `azdecrypt_placeholder` metadata note, set `rights_class:
  hold_for_review`, and include a `curation_notes` sentence explaining that a
  better canonical source is still being sought.
