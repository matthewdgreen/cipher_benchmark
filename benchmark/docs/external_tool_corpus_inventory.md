# External Tool Corpus Inventory

Last reviewed: 2026-07-19.

This inventory separates files bundled with external solvers from records that
are suitable for scored benchmark use. A filename containing `solved` is not
itself ground truth: scored imports require a bundled key/plaintext or an
independently curated accepted solution. Upstream ciphertext files remain in
the sibling Decipher tool checkouts and are not copied merely for coverage.

## Zenith

Upstream checkout: `../decipher/other_tools/zenith-src/` (GPLv3). Cipher JSON
resources are under `zenith-inference/src/main/resources/ciphers/`.

| File | Tokens / dimensions | Bundled solution | Benchmark disposition |
|---|---:|---|---|
| `goldbug.json` | 203 / 1×203 | 20-symbol key | Imported as `tool_zenith_goldbug` |
| `horacemann.json` | 66 / 1×66 | 15-symbol key | Imported as `tool_zenith_horacemann` |
| `zodiac408.json` | 408 / 24×17 | 54-symbol key | Imported smoke record and curated global-glyph record |
| `zodiac340-original.json` | 340 / 20×17 | No bundled key | Curated separately with accepted plaintext and explicit transform metadata |
| `zodiac340-transformed.json` | 340 / 20×17 | No bundled key | Transform intermediate; represented by the curated Z340 pipeline, not a duplicate scored record |
| `kryptos1.json` | 63 | No bundled key | Curated separately as `kryptos_k1` with accepted solution parameters |
| `kryptos2.json` | 372 | No bundled key | Curated separately as `kryptos_k2` with accepted solution parameters |
| `kryptos3.json` | 337 | No bundled key | Curated separately as `kryptos_k3` with accepted solution parameters |
| `kryptos4.json` | 97 | Unsolved | `kryptos_k4` in the unsolved area |
| `hamptonfull.json` | 29,522 | None | Diagnostic/source material only; no scorable import |
| `jameshampton1.json` | 298 | None | Diagnostic/source material only; no scorable import |

Conclusion: all self-contained, known-key Zenith files are already imported.
The remaining useful solved material is already represented in dedicated
Zodiac and Kryptos sources, avoiding duplicate benchmark rows.

## zkdecrypto-lite

Upstream directory: `../decipher/other_tools/zkdecrypto-src/zkdecrypto-lite/cipher/`.
The bundle contains 23 ciphertext `.txt` files plus `readme.rtf`; it does not
ship a general plaintext sidecar set. Rights and original provenance vary by
file, so ciphertext-only examples are not automatically redistributable.

| Group | Files | Disposition |
|---|---|---|
| Curated Zodiac coverage | `408.zodiac.solved`, four Z340 order/plus variants, `153.zodiac.unsolved` | Z408/Z340 represented in the main Zodiac source; variants represented in the unsolved area |
| Other Zodiac short/copycat | `13.zodiac.mynameis`, `32.zodiac.button`, `149.zodiac.copycat`, `204.zodiac.solved` | Short unsolved/diagnostic or duplicate fragment; do not score without independent ground truth |
| Dorabella | `88.elgar.dorabella` | Represented in the unsolved area as disputed |
| Singh stage 3 | `1122.singh.stage3` | Known challenge family, but bundle lacks a plaintext fixture; candidate for separate provenance-backed curation |
| Tyler/Poe | `225.tyler1.solved` | Labelled solved and key-described in the readme, but no plaintext fixture; hold pending independent source verification |
| User-created examples | `306.unsub`, `318.bryianzum`, `330.kiuku`, six 340-symbol examples, `378.ray_n` | Ciphertexts only; generator keys/plaintexts and redistribution provenance absent, so not scored imports |

No additional zkdecrypto-lite record is imported by this sweep. This is a
deliberate ground-truth and provenance decision, not missing inventory work.

## Coverage Policy

- Dedicated curated records take precedence over duplicate tool-bundle rows.
- `scorable: true` requires available ground truth independent of a filename.
- Transformed intermediates must identify the transform and source order.
- Unsolved and disputed material belongs in `benchmark/unsolved/`.
- Unsupported or ciphertext-only examples must not make solver failures look
  like regressions.
