# Cipher Benchmark TODO

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
- [ ] Complete external-tool corpus inventory.
  - Zenith bundled JSON ciphers currently observed in `../decipher/other_tools/zenith-src/zenith-inference/src/main/resources/ciphers/`: `goldbug`, `hamptonfull`, `horacemann`, `jameshampton1`, `kryptos1`, `kryptos2`, `kryptos3`, `kryptos4`, `zodiac340-original`, `zodiac340-transformed`, `zodiac408`.
  - zkdecrypto-lite currently has 24 bundled `cipher/*.txt` files under `../decipher/other_tools/zkdecrypto-src/zkdecrypto-lite/cipher/`.
  - For each candidate, record: source path, provenance/license note, cipher type, dimensions/token count, plaintext/key availability, transform requirements, scorable status, and likely baseline solver.
- [ ] Import remaining solved/scorable Zenith records.
  - Confirm which Zenith JSON files include or imply a plaintext/key suitable for `transcription2plaintext`.
  - Treat Kryptos sections and Hampton/J. Hampton carefully; add as parity only when the cipher family and solution layer are unambiguous.
  - Represent Zodiac 340 original/transformed with explicit `transform_applied` metadata before using in scored splits.
- [ ] Import selected zkdecrypto-lite records.
  - Start with solved/reference Zodiac and other solved examples.
  - Add unsolved or special-family ciphers only as diagnostic records, not solved parity tests.
  - Label unsupported families explicitly instead of letting Decipher failures look like regressions.
- [ ] Expand tool-bundled split coverage.
  - `parity_tool_builtins.jsonl`: all solved tool-bundled records expected to be solvable by automated tools.
  - Consider separate splits: `parity_zodiac.jsonl`, `parity_kryptos.jsonl`, `parity_polygraphic_or_transposition.jsonl`, and `agentic_advantage_unsolved_or_contextual.jsonl`.
- [ ] Add/standardize tool-bundled metadata fields where useful.
  - `known_cipher_type`
  - `word_boundaries`
  - `baseline_solvers`
  - `expected_min_char_accuracy`
  - `transform_applied`
  - `scorable`
  - `unsupported_reason`
  - `source_file`
  - `upstream_provenance`
- [ ] Run validator after each tool-bundled import batch and verify all manifest/split references.

## Agentic Advantage Support

- [ ] Add context-scaling splits for Borg and Copiale.
- [ ] Add dirty-transcription stress variants.
- [ ] Add nomenclator/codeword stress cases.
- [ ] Add Track C image-to-plaintext experiments.
- [ ] Add explicit `agentic_hypothesis` metadata for each advantage test.
