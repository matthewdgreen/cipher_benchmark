# Cipher Benchmark TODO

Last swept: 2026-07-19.

## Schema And Curation (post S1–S7 rollout)

- [x] Apply S1–S7 schema hardening (2026-04-23). Rollout committed across
  commits `a80adee` → `d0c56f8`.
- [x] Backfill `synthetic: true` on the 240 generated records.
- [x] Backfill `rights_class` (synthetic → `open`).
- [x] Coerce integer `manuscript_page` values to string (101 records).
- [x] Relabel 101 Copiale records to `rights_class: open` per Megyesi 2026-04-18.
- [x] Populate structured `image_provenance` on all 155 DECODE/Gallica
  records and update `scripts/create_decode_gallica_pilot.py` to emit it.
  `scripts/backfill_decode_gallica_metadata.py` is the idempotent migration.
- [x] Correct DECODE manuscript dates (the old values were DECODE database
  creation timestamps) and populate `date_earliest_year` /
  `date_latest_year` where source date bounds exist (154 of 155 records).
- [x] Complete the Voynich intake and commit 227 ZL3b-derived folio records
  into `benchmark/unsolved/manifest/records.jsonl`.

## Unsolved Area

- [x] Seed `benchmark/unsolved/` with relaxed schema + README +
  per-source Voynich README.
- [x] Write Voynich intake script (Beinecke IIIF).
- [x] Run the full Voynich intake and commit 227 folio records.
- [x] Import the Zandbergen-Landini ZL3b EVA/IVTFF transcription into
  `benchmark/unsolved/sources/voynich/transcriptions/`; direct permission
  from René Zandbergen is recorded with the source documentation.
- [ ] Build `decode_undecrypted/` intake (blocked on DECODE login).
- [ ] Build `famous_short/` with one record per cipher (Zodiac Z13/Z32,
  Kryptos K4, Dorabella, D'Agapeyeff, Beale 1 & 3, Somerton Man,
  Ricky McCormick, Scorpion S1–S5, Shugborough, Feynman #2/#3,
  Paul Rubin, Henry Debosnys).
  - Started: Scorpion S1/S5, Zodiac variants/Z153, Kryptos K4, Beale 1/3,
    and D'Agapeyeff are now seeded in the unsolved area. Feynman #2/#3 have
    been promoted to main-benchmark `solved_probable` calibration records with
    claimed plaintext and method metadata.
- [ ] Evaluate Rohonc Codex rights; include if feasible.
- [x] Draft the Track D (`image2hypothesis`) evaluation rubric in
  `benchmark/docs/track_d_image2hypothesis_rubric.md`.

## Agentic Parity Support

### 1. Benchmark Hygiene

- [x] Keep README and guide counts synchronized with `benchmark/manifest/records.jsonl`.
- [x] Keep `benchmark/manifest/schema.json` aligned with actual record classes.
- [x] Fix or explicitly mark missing referenced files.
- [x] Validate all split references after curation scripts run.
- [x] Distinguish Track-B-only generated records from image-backed historical records.

### 2. Schema And Metadata

- [x] Support optional generated-record fields:
  - `word_boundaries`
  - `token_count`
  - `word_count`
  - `notes`
- [x] Support optional parity split metadata:
  - `parity_family`
  - `recommended_agent_tool`
  - `baseline_solvers`
  - `expected_baseline_status`
  - `expected_min_char_accuracy`
  - `known_cipher_type`
  - `word_boundaries`
- [x] Add `source_record_id` and `rights_class` to generated records, or document why generated Track-B-only records are allowed to omit image/source fields.

### 3. Parity Splits

- [x] `parity_homophonic_en.jsonl`
- [x] `parity_simple_substitution_multilang.jsonl`
- [x] `parity_borg_latin.jsonl`
- [x] `parity_copiale_german.jsonl`
- [x] `parity_tool_builtins.jsonl`
- [x] `parity_zodiac.jsonl`

### 4. Tool-Bundled Ciphers

- [x] Add a separate source for reference ciphers bundled with external tools.
- [x] Import initial smoke records with clear provenance and usable plaintext/key data.
  - Current imported records: `tool_zenith_goldbug`, `tool_zenith_horacemann`, `tool_zenith_zodiac408`.
- [x] Keep unsolved famous ciphers marked as diagnostic/unsupported, not solved parity tasks.
- [x] Import first Kryptos calibration records.
  - `kryptos_k1` and `kryptos_k2` are solved keyed-Vigenere-style records in
    the main benchmark.
  - `kryptos_k3` is a solved pure-transposition/TransMatrix record in the
    main benchmark. Its runnable transcription excludes the final
    nonalphabetic `?` marker from the local source copy and records the
    original source text in metadata.
  - K1/K2 now include solution-bearing `known_cipher_parameters` for
    keyed-Vigenere replay; these must stay out of blind/standard context.
  - K3 includes solution-bearing `known_cipher_parameters` for TransMatrix
    replay/search calibration; these must stay out of blind/standard context.
  - K2 plaintext has been aligned to the imported ciphertext/keyed tableau
    calibration text ending `ID BY ROWS`; source `?` tokens are retained in
    the canonical transcription as skipped/unknown ciphertext symbols.
  - `kryptos_k4` is an unsolved challenge record in the unsolved area.
- [x] Complete external-tool corpus inventory.
  - Zenith bundled JSON ciphers currently observed in `../decipher/other_tools/zenith-src/zenith-inference/src/main/resources/ciphers/`: `goldbug`, `hamptonfull`, `horacemann`, `jameshampton1`, `kryptos1`, `kryptos2`, `kryptos3`, `kryptos4`, `zodiac340-original`, `zodiac340-transformed`, `zodiac408`.
  - zkdecrypto-lite currently has 24 bundled `cipher/*.txt` files under `../decipher/other_tools/zkdecrypto-src/zkdecrypto-lite/cipher/`.
  - For each candidate, record: source path, provenance/license note, cipher type, dimensions/token count, plaintext/key availability, transform requirements, scorable status, and likely baseline solver.
- [x] Resolve remaining solved/scorable Zenith records.
  - Confirmed: the three JSON files with bundled keys are already imported.
    Z340 and Kryptos K1-K3 are curated in dedicated sources; Hampton files lack
    ground truth and K4 remains unsolved.
  - Treat Kryptos sections and Hampton/J. Hampton carefully; add as parity only when the cipher family and solution layer are unambiguous.
  - Represent Zodiac 340 original/transformed with explicit `transform_applied` metadata before using in scored splits.
- [x] Evaluate selected zkdecrypto-lite records for import.
  - Zodiac coverage is already curated. No further records were imported:
    remaining files lack a bundled plaintext/key, duplicate curated targets,
    or are unsolved/diagnostic. See the external-tool corpus inventory.
  - Add unsolved or special-family ciphers only as diagnostic records, not solved parity tests.
  - Label unsupported families explicitly instead of letting Decipher failures look like regressions.
- [x] Expand tool-bundled split coverage.
  - `parity_tool_builtins.jsonl` covers all three self-contained known-key
    Zenith imports; dedicated Zodiac and Kryptos splits cover their curated
    source records. Contextual advantage packets are separate from parity.
- [x] Add/standardize tool-bundled metadata fields where useful.
  - `known_cipher_type`
  - `word_boundaries`
  - `baseline_solvers`
  - `expected_min_char_accuracy`
  - `transform_applied`
  - `scorable`
  - `unsupported_reason`
  - `source_file`
  - `upstream_provenance`
- [x] Run validator after the tool-bundled inventory/metadata batch and verify
  all manifest/split references (905 records, 23 split files, 455 tests).

## Agentic Advantage Support

- [x] Add context-scaling splits for Borg and Copiale.
- [x] Populate tiered `context_layers` across the current manifests (905/905
  main records and 262/262 unsolved records).
  - Keep `minimal` to archival/provenance facts only.
  - Keep `standard` to language, cipher-family, symbol, and transcript facts.
  - Use `historical` for stronger non-solution background, such as author,
    manuscript genre, known surrounding events, or likely plaintext domain.
  - Use explicit `contains_solution` / `contains_plaintext_hint` flags so
    solvers can run clean context-ablation experiments.
- [ ] Add `associated_documents` for long companion material.
  - Examples: Scorpion plaintext notes/letters, envelopes, newspaper clippings,
    manuscript catalog notes, or long source commentary.
  - Store concise summaries in context layers; store full text/images as
    associated document files and expose them only through explicit solver
    policy or agent tools.
  - [x] Initial Scorpion intake: S1/S5 records now link public cipher images,
    include a released-letter excerpt as an associated document, and provide
    tentative v0.2 Track-B-style transcriptions for exploratory solver runs.
  - [x] Add a clearly marked synthetic S1+S5 shared-key/shared-alphabet
    hypothesis case using a global v0.2 family-label map.
  - [ ] Complete Scorpion curation with a vetted glyph-ID transcription pass
    before making headline Track B or solver-performance claims.
- [ ] Add `related_records` links where one cipher has same-author,
  same-manuscript, same-key-family, or known-solution neighbors.
- [ ] Add dirty-transcription stress variants.
- [ ] Add nomenclator/codeword stress cases.
- [ ] Add Track C image-to-plaintext experiments.
- [x] Add explicit `agentic_hypothesis` metadata for each current advantage
  test.
