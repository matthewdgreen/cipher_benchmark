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
- [x] Import only records with clear provenance and usable plaintext/key data.
- [x] Keep unsolved famous ciphers marked as diagnostic/unsupported, not solved parity tasks.
- [ ] Candidate sources:
  - Zenith bundled JSON ciphers.
  - zkdecrypto-lite Zodiac files.
  - zkdecrypto-lite classical test ciphers.

## Agentic Advantage Support

- [ ] Add context-scaling splits for Borg and Copiale.
- [ ] Add dirty-transcription stress variants.
- [ ] Add nomenclator/codeword stress cases.
- [ ] Add Track C image-to-plaintext experiments.
- [ ] Add explicit `agentic_hypothesis` metadata for each advantage test.
