# Normalization Rules

**Version:** 0.1 (pilot draft)
**Date:** 2026-04-15
**Status:** Draft — derived from the Copiale cipher pilot; will evolve as more sources are added

---

## 1. Purpose

The benchmark maintains two transcription layers for every record:

- **Diplomatic transcription**: A close representation of the source, preserving the original symbol choices, line breaks, and notation conventions of the transcriber or scholarly edition.
- **Canonical transcription**: A normalized symbol stream where each distinct cipher symbol class is remapped to an abstract stable token (`S001`, `S002`, ...).

The canonical form exists so that evaluation metrics are not affected by arbitrary transcription conventions (e.g., whether a symbol is called `grr` or `γ` or `U+0263`).

This document defines the rules for producing canonical transcriptions from diplomatic ones.

---

## 2. Core Principles

1. **One symbol class = one canonical token.** If two visual forms represent the same cipher symbol (e.g., a sloppy vs. neat version of the same glyph), they get the same S-token.
2. **Different symbol classes = different tokens.** If two symbols are visually similar but functionally distinct in the cipher system (e.g., homophonic variants), they get different S-tokens.
3. **The diplomatic transcription is authoritative.** The canonical form is a mechanical remapping of the diplomatic form. It never adds, removes, or reorders symbols.
4. **The mapping must be deterministic and documented.** Given the same diplomatic transcription and the same symbol map, anyone must produce the same canonical output.

---

## 3. Token Format

Canonical tokens follow the pattern:

```
S{NNN}
```

Where NNN is a zero-padded three-digit integer (e.g., `S001`, `S042`, `S136`).

Tokens are assigned in order of first appearance across the full document (not per-page). This means the same symbol always gets the same canonical token regardless of which page it appears on.

If a corpus exceeds 999 distinct symbols, extend to four digits (`S0001`). Do not mix widths within a corpus.

---

## 4. Scope of a Symbol Map

A symbol map is defined **per cipher system**, not per page or per document. If multiple pages use the same cipher system (as in the Copiale manuscript), they share one symbol map.

Different cipher systems (e.g., a Spanish nomenclator vs. the Copiale cipher) have independent symbol maps. The same canonical token `S001` in one system has no relation to `S001` in another.

Symbol maps are stored in `metadata/{source}_symbol_map.json`.

---

## 5. Handling Diplomatic Transcription Conventions

### 5.1 Whitespace

- Diplomatic transcriptions use **spaces** to separate tokens.
- Canonical transcriptions preserve the same token boundaries.
- **Blank lines** in the diplomatic transcription represent line breaks in the source document. Canonical transcriptions preserve these.

### 5.2 Logograms and special symbols

Some cipher systems include logograms — symbols that represent whole words rather than letters. In the diplomatic transcription, these may be marked with special notation (e.g., `*nee*` for the "master" logogram in the Copiale cipher).

**Rule:** Logograms are treated as regular cipher symbols for canonical mapping purposes. If a logogram appears as `nee` in the diplomatic text, it maps to a single S-token (e.g., `S077`). The logogram's meaning is documented in the symbol map metadata, not in the canonical transcription.

If a logogram appears with variant markers (e.g., `tri` vs. `tri..`), each variant gets its own S-token unless the transcriber explicitly marks them as equivalent.

### 5.3 Punctuation

Punctuation marks that are part of the original cipher document (e.g., period, colon) are treated as cipher symbols and receive their own S-tokens.

Punctuation that is editorial (added by the transcriber for readability) should be excluded from the canonical form. The diplomatic transcription should document which punctuation is original vs. editorial.

### 5.4 Capitalization

If the diplomatic transcription preserves capitalization (e.g., `L` vs. `l`), the capitalized and lowercase forms are treated as **separate tokens** in the canonical mapping, since they may represent distinct cipher symbols.

### 5.5 Uncertainty markers

Characters marked as uncertain in the diplomatic transcription (e.g., with `?`) should be preserved in the canonical form with an uncertainty flag:

- Diplomatic: `grr?`
- Canonical: `S007?`

The `?` suffix indicates transcription uncertainty, not a different symbol.

### 5.6 Catch-word markers

Some manuscripts repeat words at the bottom of a page as catch-words (reading aids). In the Copiale transcription, these are marked with `#`. Catch-words are **excluded** from the canonical transcription since they are duplicates, not independent cipher content.

### 5.7 Page markers

Page markers (e.g., `## PAGE 50`) are metadata, not cipher content. They are **excluded** from both diplomatic and canonical transcription files in the per-page benchmark format (since each file already represents one page).

---

## 6. Normalization Process

Given a diplomatic transcription file and a symbol map:

```
For each line in the diplomatic transcription:
  1. Skip blank lines (preserve as line breaks)
  2. Skip comment lines (## markers, # catch-words)
  3. Split line into space-separated tokens
  4. For each token:
     a. Look up token in the symbol map
     b. If found: emit the corresponding S-token
     c. If not found: flag as unknown symbol (curation error)
  5. Join canonical tokens with spaces
  6. Emit the canonical line
```

### Edge cases

- **Token not in map:** This indicates a curation error — every symbol in the diplomatic transcription must have a canonical mapping. Flag for review.
- **Empty lines:** Preserved as-is (they represent line breaks).
- **Multi-token logograms:** If a logogram is represented as multiple space-separated tokens in the diplomatic form, it must be consolidated into a single token before canonical mapping, or each sub-token mapped independently. Document which convention is used per source.

---

## 7. Symbol Map Format

```json
{
  "description": "Mapping from diplomatic tokens to canonical S### identifiers",
  "source": "Description of the transcription source",
  "cipher_system": "Name or ID of the cipher system",
  "total_symbols": 136,
  "mapping": {
    "L": "S001",
    "i": "S002",
    "grr": "S007",
    "nee": "S077",
    ...
  },
  "logogram_glossary": {
    "nee": "master",
    "tri": "lodge",
    "lip": "oculist (eye)",
    "star": "secret",
    "bigx": "freemason",
    "sci": "God",
    "toe": "power"
  },
  "notes": "Free-text notes about ambiguities, variants, etc."
}
```

---

## 8. Worked Example: Copiale Cipher

### Source
Knight, Megyesi, Schaefer (2011). "The Copiale Cipher."

### Diplomatic transcription (page 50, line 1)
```
r. zzz x. y.. grr three uu pi ah nee h z ih plus r g uh ki uu ds nee e o grr r. p bar tri c. : ih m bar ki arr uu ds
```

### Canonical transcription (same line)
```
S052 S013 S012 S054 S007 S029 S035 S023 S031 S077 S081 S006 S014 S041 S036 S050 S033 S019 S035 S059 S077 S083 S084 S007 S052 S042 S008 S027 S030 S004 S014 S005 S008 S019 S020 S035 S059
```

### Plaintext (corresponding German)
```
regiereNde *nee* dem neueN *nee*  er solle sucheN
```

### Notes
- The diplomatic transcription uses ASCII mnemonics (e.g., `grr`, `bar`, `zzz`) for cipher symbols that are actually handwritten glyphs
- The canonical form makes no assumptions about what the symbols look like — just their identity
- The plaintext retains logogram markers (e.g., `*nee*`) where the original cipher used a special symbol rather than spelling out the word
- Capital `N` in the plaintext indicates a character written with a special mark in the original German text

---

## 9. Open Questions for Future Versions

1. **Cross-document symbol alignment:** When two documents use the same cipher system (e.g., two letters encrypted with the same nomenclator), should they share a symbol map? Probably yes, but this requires a "cipher system" registry.

2. **Symbol variants:** How to handle symbols that are clearly the same letter but written differently on different pages (e.g., due to different scribes)? Current rule: follow the diplomatic transcription's judgment.

3. **Cleartext passages:** Some cipher documents contain passages in cleartext (unencrypted). Should these be transcribed as regular letters in the diplomatic form, and mapped to S-tokens in the canonical form? Or marked separately? Current approach: treat cleartext letters as symbols in the map (they have their own S-tokens).

4. **Null/separator symbols:** Some ciphers include null symbols (meaningless fillers) or word separators. These should be mapped to canonical tokens and documented in the symbol map metadata.

5. **Multi-language normalization:** As we add sources with different transcription conventions (e.g., Unicode-based transcriptions from DECRYPT, ASCII from the Copiale paper), we will need source-specific parsing rules before the shared canonical mapping step.
