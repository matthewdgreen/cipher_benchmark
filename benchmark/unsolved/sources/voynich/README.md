# Voynich Manuscript (Beinecke MS 408)

## Source
Beinecke Rare Book and Manuscript Library, Yale University, MS 408.
- IIIF manifest: https://collections.library.yale.edu/manifests/2002046
- Catalog page: https://collections.library.yale.edu/catalog/2002046

## Images
Images are available from the Beinecke IIIF manifest. The earlier intake
script can fetch local JPEGs at a standard max-width for consistent pixel
density, but the current ZL3b transcription import does not require local
image files.

## Rights
Beinecke digitized images of MS 408 are released under Yale's open-access
policy for public-domain materials (no known rights restrictions). We
redistribute alongside attribution and a link to the source. If this
position changes, switch `rights_class` to `linked_only`.

The Zandbergen-Landini transliteration is modern scholarly work. On
2026-05-17, René Zandbergen explicitly granted permission by E-mail to use any
or all transliteration files made available at `voynich.nu`. A local note with
the permission text is preserved at `documents/PERMISSION_2026-05-17.md`.
Accordingly, the current ZL3b-derived benchmark records are treated as
redistributable benchmark materials and use `rights_class: open`, with
attribution and source links preserved.

This is still not a claim that the transliteration is uniquely "correct." As
René notes in the permission E-mail, both the transliteration alphabet and the
grouping of glyphs into characters are editorial choices. Benchmark users
should treat the current import as one documented, reproducible representation,
not as a final Voynich glyph ontology.

## Transcription
The current benchmark import uses the Zandbergen-Landini ZL3b transliteration:

- Raw source: `transcriptions/ZL3b-n.txt`
- Source notes: `documents/SOURCE_ZL3b.md`
- Global S-token map: `metadata/voynich_zl3b_symbol_map.json`
- Per-folio metadata/comments: `metadata/voynich_zl3b_page_metadata.json`
- Per-folio derived files:
  - `transcriptions/voynich_{folio}.zl3b.canonical.txt`
  - `transcriptions/voynich_{folio}.zl3b.diplomatic.txt`
  - `documents/voynich_{folio}.zl3b.notes.md`

The importer is `scripts/import_voynich_zl3b.py`. It preserves the raw IVTFF
file, writes a per-folio diplomatic file, then derives canonical benchmark
files by choosing the first listed alternative reading, removing IVTFF markup,
treating certain and uncertain spaces as word boundaries, and mapping
importer-level EVA/high-ASCII units to a global S-token map. This is a
practical benchmark representation, not a claim about final Voynich glyph
ontology.

## Reproducibility

The current Voynich benchmark import is reproducible in a narrow, benchmark
sense:

- the raw source snapshot (`ZL3b-n.txt`) is preserved locally in the benchmark;
- the source-file header/version is recorded in `documents/SOURCE_ZL3b.md`;
- the importer is deterministic and documented in
  `scripts/import_voynich_zl3b.py`.

It is not uniquely reproducible in a stronger philological sense, because
alternative transliteration alphabets and alternative glyph-grouping decisions
remain plausible and should be expected in future comparative imports.

Alphabets in use:
- **EVA** (Takahashi–D'Imperio–Currier–Stolfi): dominant since late 1990s.
- **ZL (Zandbergen–Landini)**: refinement of EVA with disambiguated glyphs.

The local staging area `data_staging/voynich/` also holds downloaded copies of
the other stable files from `https://www.voynich.nu/data/` for comparison
work. That directory is git-ignored.

## Folio conventions
- Folio IDs follow the Beinecke convention: `f1r`, `f1v`, ..., `f116v`.
- Foldouts (e.g. `f67r1/f67r2`, `f68r1/f68r2/f68r3`) are expanded into
  separate records, one per numbered sub-folio.
- Missing folios (f12, f59–f64, etc.) are NOT included. ~240 extant folios.

## Known partial signals
- `partial_solution_evidence: none` for the corpus as a whole — no section
  has a widely accepted reading.
- A concise public-source overview is stored at
  `documents/voynich_public_overview.md` and injected into the historical
  context layer for each ZL3b folio record. It is paraphrased from public
  sources and is meant to supply broad facts only: the manuscript is
  illustrated, unsolved, written in an unknown script/language, and generally
  placed in a late-medieval/early-modern European manuscript context.
- Certain marginalia (notably on f66r, f116v) are in readable Latin/German
  scripts but their relationship to the main text is unclear.
- Quire structure, illustration clustering (herbal/astronomical/balneological/
  pharmaceutical/recipe), and internal language statistics (Currier A vs. B)
  are well-characterized in the literature. ZL3b page comments are preserved
  in `metadata/voynich_zl3b_page_metadata.json` and per-folio notes files.

## Notable attempts (non-exhaustive)
Included as `notable_attempts` in per-folio records for traceability;
none are accepted as solutions.
- Cheshire 2019 (proto-Romance) — widely rejected.
- Gibbs 2017 (Latin abbreviation shorthand) — widely rejected.
- Rugg 2004 (hoax via grille) — not a decipherment; structural hypothesis.
- Friedman / NSA studies — inconclusive.
