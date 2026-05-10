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
| `Blitz cipher page 7.txt` | 470 | `blitz_cipher_p7` | `imported` | Reported as unsolved/provisional transcription. | Cipher Mysteries partial transcription; local AZdecrypt copy used as cross-check. | Imported under `sources/blitz/` as `hold_for_review`; provenance and transcription certainty remain caveats. | Live unsolved split row: `blitz_cipher_p7_unsolved`. |
| `Blitz cipher page 8.txt` | 159 | `blitz_cipher_p8` | `imported` | Reported as unsolved/provisional transcription. | Same Blitz sources as above. | Imported under `sources/blitz/` as `hold_for_review`; companion to page 7. | Live unsolved split row: `blitz_cipher_p8_unsolved`. |
| `Copenhagen cryptogram.txt` | 101 | `copenhagen_cryptogram` | `needs_source_check` | Unknown; probably short unsolved challenge. | Need source research. | Do not import until identified. | Find canonical source/status. |
| `D'Agapeyeff.txt` | 392 | `dagapeyeff_cipher` | `imported` | Widely treated as unsolved; may include transcription/encoding error. | Original *Codes and Ciphers* first edition; Hyde & Rugg discussion; public transcription. | Imported under `sources/famous_short/` as `hold_for_review`; target preserves five-digit groups, with AZdecrypt two-digit-pair and Polybius files stored only as hypothesis/context material. | Live unsolved split row: `dagapeyeff_cipher_unsolved`. |
| `DCT Reloaded 3.txt` | 1100 | `dct_reloaded_3` | `imported` | MysteryTwister C3 / Double Column Transposition Reloaded Part 3; no accepted solution in benchmark. | MTC3 challenge PDF by A. Wacker with Bernhard Esslinger/Klaus Schmeh credits; local AZdecrypt copy used as cross-check. | Imported under `sources/dct_reloaded/` as `hold_for_review`; challenge constraints are context, not plaintext. | Live unsolved split row: `dct_reloaded_3_unsolved`. |
| `Dorabella.txt` | 87 | `dorabella_cipher` | `imported` | Famous disputed/unsolved Elgar note; many claimed solutions, no consensus. | Cipher Mysteries public context plus local AZdecrypt letter-surrogate cross-check. | Imported under `sources/dorabella/` as `hold_for_review`; surrogate encoding is not a final glyph ontology. | Live unsolved split row: `dorabella_cipher_unsolved`. |
| `Feynman 2.txt` | 261 | `feynman_2` | `promoted_to_solved_probable` | Historically presented as unsolved, but codewarrior0 published a 2023 claimed solve with strong re-encipherment evidence. | Cipher Foundation Feynman Challenge Ciphers; codewarrior0 claimed solution; Housman plaintext source. | Imported in the main benchmark under `sources/feynman/` as `solved_probable`; claimed plaintext and method metadata are stored, while blind/standard context avoids solution-bearing details. | Live main split row: `feynman_2_alternating_substitution`. |
| `Feynman 3.txt` | 231 | `feynman_3` | `promoted_to_solved_probable` | Same as Feynman 2; claimed solution re-enciphers almost completely under the published partial alphabets/method. | Cipher Foundation Feynman Challenge Ciphers; codewarrior0 claimed solution; CaltechAUTHORS Feynman paper source. | Imported in the main benchmark under `sources/feynman/` as `solved_probable`; claimed plaintext and method metadata are stored, while blind/standard context avoids solution-bearing details. | Live main split row: `feynman_3_alternating_substitution`. |
| `GUN WA 1889.txt` | 77 | `gun_wa_1889` | `needs_source_check` | Unknown short challenge. | Need source research. | Do not import until identified. | Find source/status. |
| `Glurk (Beale 3 emulation challenge).txt` | 1591 | `glurk_beale3_emulation` | `imported_placeholder` | Likely modern synthetic/emulation challenge, not historical unsolved. | Local AZdecrypt file only; better source still needed. | Imported under `sources/glurk/` as `hold_for_review`, `synthetic: true`; not a historical claim. | Live unsolved split row: `glurk_beale3_emulation_unsolved`. |
| `Helen Fouché Gaines.txt` | 125 | `helen_fouche_gaines` | `needs_source_check` | Unknown short challenge. | Need source research. | Rights/status unclear. | Find canonical source. |
| `IKLP long.txt` | 358 | `iklp_long` | `needs_source_check` | Unknown. | Need source research. | Rights/status unclear. | Find source/status or defer. |
| `IKLP short.txt` | 19 | `iklp_short` | `defer_or_exclude` | Too short for useful automated cryptanalysis unless paired with context. | Need source research if retained. | Likely not worth a standalone benchmark record. | Defer unless related to `IKLP long`. |
| `Kryptos 4 (Berlin clock clue).txt` | 108 | `kryptos_k4_berlin_clock_clue` | `already_present` | K4 remains without a public accepted cryptanalytic solution; recent reports say solution information has been privately discovered/auctioned, not publicly reproducible. | CIA/artist/Kryptos public pages; AP/Scientific American reporting for current status. | Benchmark already has `kryptos_k4`; clue-bearing variant should be associated document or context tier, not separate source unless useful. | Compare with existing K4 record and decide whether to add clue overlay. |
| `Kryptos 4.txt` | 97 | `kryptos_k4` | `already_present` | Present in unsolved benchmark. | Existing benchmark source plus public Kryptos references. | Already imported. | Verify AZdecrypt text matches existing canonical K4. |
| `Lawrence Public Library Cryptogram part 1.txt` | 451 | `lawrence_public_library_cryptogram_p1` | `imported` | Two-part cryptogram reported by Cipherbrain/Klaus Schmeh; no accepted solution. | Cipherbrain article from Klaus Schmeh's Krypto Kolumne; local AZdecrypt copy used as cross-check. | Imported under `sources/lawrence_public_library/` as `hold_for_review`. | Live unsolved split row: `lawrence_public_library_p1_unsolved`. |
| `Lawrence Public Library Cryptogram part 2.txt` | 395 | `lawrence_public_library_cryptogram_p2` | `imported` | Companion part to part 1; no accepted solution. | Same source as part 1. | Imported under `sources/lawrence_public_library/` as `hold_for_review`. | Live unsolved split row: `lawrence_public_library_p2_unsolved`. |
| `Moustier St Martin.txt` | 76 | `moustier_st_martin` | `needs_source_check` | Unknown short symbolic/historical example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Moustier Virgin.txt` | 80 | `moustier_virgin` | `needs_source_check` | Unknown short symbolic/historical example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Nick Pelling challenge 2.txt` | 354 | `nick_pelling_challenge_2` | `imported_placeholder` | Likely challenge/discussion material from Cipher Mysteries; exact page/status still needs verification. | Local AZdecrypt file plus Cipher Mysteries family lead. | Imported under `sources/nick_pelling/` as `hold_for_review`; exact source page pending. | Live unsolved split row: `nick_pelling_challenge_2_unsolved`. |
| `Nick Pelling challenge 3.txt` | 276 | `nick_pelling_challenge_3` | `imported_placeholder` | Same as challenge 2. | Same. | Same. | Live unsolved split row: `nick_pelling_challenge_3_unsolved`. |
| `Nick Pelling challenge 4.txt` | 246 | `nick_pelling_challenge_4` | `imported_placeholder` | Same as challenge 2. | Same. | Same. | Live unsolved split row: `nick_pelling_challenge_4_unsolved`. |
| `Nick Pelling challenge 5.txt` | 246 | `nick_pelling_challenge_5` | `imported_placeholder` | Same as challenge 2. | Same. | Same. | Live unsolved split row: `nick_pelling_challenge_5_unsolved`. |
| `Nick Pelling challenge 6.txt` | 237 | `nick_pelling_challenge_6` | `imported_placeholder` | Same as challenge 2. | Same. | Same. | Live unsolved split row: `nick_pelling_challenge_6_unsolved`. |
| `Nick Pelling challenge 7.txt` | 222 | `nick_pelling_challenge_7` | `imported_placeholder` | Same as challenge 2. | Same. | Same. | Live unsolved split row: `nick_pelling_challenge_7_unsolved`. |
| `Paul Rubin.txt` | 459 | `paul_rubin_cipher` | `imported` | Modern mixed-stream unsolved challenge. | Cipher Mysteries Paul Rubin transcription/context plus local AZdecrypt cross-check. | Imported under `sources/paul_rubin/` as `hold_for_review`; heterogeneous stream needs structural diagnosis. | Live unsolved split row: `paul_rubin_cipher_unsolved`. |
| `Powers cryptogram.txt` | 96 | `powers_cryptogram` | `needs_source_check` | Unknown short example. | Need source research. | Rights/status unclear. | Find source/status. |
| `Ricky McCormick page 1.txt` | 406 | `ricky_mccormick_note_1` | `imported` | FBI/ACA failed to decipher; still treated as unsolved. | Cipher Foundation page with note images/context; local AZdecrypt copy used as cross-check. | Imported under `sources/ricky_mccormick/` as `hold_for_review`; better FBI-primary image/source curation remains desirable. | Live unsolved split row: `ricky_mccormick_note_1_unsolved`. |
| `Ricky McCormick page 2.txt` | 425 | `ricky_mccormick_note_2` | `imported` | Same as page 1. | Same source as page 1. | Imported under `sources/ricky_mccormick/` as `hold_for_review`; companion to note 1. | Live unsolved split row: `ricky_mccormick_note_2_unsolved`. |
| `Scorpio 5.txt` | 397 | `scorpion_s5` | `already_present` | Related Scorpion S5 record already exists with tentative v0.2 transcription. | Existing benchmark Scorpion sources; public cipher images/letters. | Compare AZdecrypt "Scorpio" numeric family labels to our v0.2 transcription, but do not silently replace. | Add cross-check note if materially different. |
| `Taman Shud.txt` | 44 | `taman_shud_code` | `imported` | The code itself remains unresolved/likely acrostic or shorthand; Somerton Man identity has changed status separately. | Cipher Foundation Somerton Man page plus local AZdecrypt cross-check. | Imported under `sources/taman_shud/` as `hold_for_review`; crossed-out line documented separately. | Live unsolved split row: `taman_shud_code_unsolved`. |

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
- Ricky McCormick: imported from public context/transcription cross-checks, but
  FBI source materials should still be preferred in a future image-level pass.
- DCT Reloaded 3: imported from the MTC3 challenge PDF plus AZdecrypt
  cross-check; useful for pure-transposition tooling.
- Lawrence Public Library cryptogram: imported from Cipherbrain/Klaus Schmeh
  context plus AZdecrypt cross-check.
- Blitz Ciphers: imported pages 7/8 from Cipher Mysteries partial
  transcription plus AZdecrypt cross-check; rights and transcription certainty
  still need review.
- Nick Pelling challenges: likely better sourced from Cipher Mysteries, but
  rights and exact pages need review.
- Dorabella and Taman Shud: imported as famous short/no-overclaim diagnostics;
  both still need better image-level source curation before public release.
- Paul Rubin: imported from Cipher Foundation context plus AZdecrypt cross-check
  as a mixed-stream diagnostic record.
- Glurk: imported as a synthetic/challenge placeholder from AZdecrypt only;
  keep separate from historical unsolved claims until provenance improves.

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
