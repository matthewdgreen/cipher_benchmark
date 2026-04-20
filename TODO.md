# Cipher Benchmark TODO

## Agentic Parity Support

### 1. Benchmark Hygiene

- [ ] Keep README and guide counts synchronized with `benchmark/manifest/records.jsonl`.
- [ ] Keep `benchmark/manifest/schema.json` aligned with actual record classes.
- [ ] Fix or explicitly mark missing referenced files.
- [ ] Validate all split references after curation scripts run.
- [ ] Distinguish Track-B-only generated records from image-backed historical records.

### 2. Schema And Metadata

- [ ] Support optional generated-record fields:
  - `word_boundaries`
  - `token_count`
  - `word_count`
  - `notes`
- [ ] Support optional parity split metadata:
  - `parity_family`
  - `recommended_agent_tool`
  - `baseline_solvers`
  - `expected_baseline_status`
  - `expected_min_char_accuracy`
  - `known_cipher_type`
  - `word_boundaries`
- [ ] Add `source_record_id` and `rights_class` to generated records, or document why generated Track-B-only records are allowed to omit image/source fields.

### 3. Parity Splits

- [ ] `parity_homophonic_en.jsonl`
- [ ] `parity_simple_substitution_multilang.jsonl`
- [ ] `parity_borg_latin.jsonl`
- [ ] `parity_copiale_german.jsonl`
- [ ] `parity_tool_builtins.jsonl`
- [ ] `parity_zodiac.jsonl`

### 4. Tool-Bundled Ciphers

- [ ] Add a separate source for reference ciphers bundled with external tools.
- [ ] Import only records with clear provenance and usable plaintext/key data.
- [ ] Keep unsolved famous ciphers marked as diagnostic/unsupported, not solved parity tasks.
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
