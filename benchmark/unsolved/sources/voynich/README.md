# Voynich Manuscript (Beinecke MS 408)

## Source
Beinecke Rare Book and Manuscript Library, Yale University, MS 408.
- IIIF manifest: https://collections.library.yale.edu/manifests/2002046
- Catalog page: https://collections.library.yale.edu/catalog/2002046

## Images
Fetched via IIIF at a standard max-width for consistent pixel density.
See `scripts/create_voynich_intake.py` for the download process.

## Rights
Beinecke digitized images of MS 408 are released under Yale's open-access
policy for public-domain materials (no known rights restrictions). We
redistribute alongside attribution and a link to the source. If this
position changes, switch `rights_class` to `linked_only`.

## Transcription
The community-standard transcription file is the Zandbergen–Landini
interlinear in IVTFF (Intermediate Voynich Transliteration File Format).
We use it unmodified as `transcriptions/voynich_zl_ivtff.txt` with a
permalink citation in `transcriptions/SOURCE.md`.

Alphabets in use:
- **EVA** (Takahashi–D'Imperio–Currier–Stolfi): dominant since late 1990s.
- **ZL (Zandbergen–Landini)**: refinement of EVA with disambiguated glyphs.

We preserve IVTFF's multi-alphabet columns rather than projecting to a
single alphabet; tools can pick their preferred representation.

## Folio conventions
- Folio IDs follow the Beinecke convention: `f1r`, `f1v`, ..., `f116v`.
- Foldouts (e.g. `f67r1/f67r2`, `f68r1/f68r2/f68r3`) are expanded into
  separate records, one per numbered sub-folio.
- Missing folios (f12, f59–f64, etc.) are NOT included. ~240 extant folios.

## Known partial signals
- `partial_solution_evidence: none` for the corpus as a whole — no section
  has a widely accepted reading.
- Certain marginalia (notably on f66r, f116v) are in readable Latin/German
  scripts but their relationship to the main text is unclear.
- Quire structure, illustration clustering (herbal/astronomical/balneological/
  pharmaceutical/recipe), and internal language statistics (Currier A vs. B)
  are well-characterized and recorded in `metadata/voynich_folio_meta.json`.

## Notable attempts (non-exhaustive)
Included as `notable_attempts` in per-folio records for traceability;
none are accepted as solutions.
- Cheshire 2019 (proto-Romance) — widely rejected.
- Gibbs 2017 (Latin abbreviation shorthand) — widely rejected.
- Rugg 2004 (hoax via grille) — not a decipherment; structural hypothesis.
- Friedman / NSA studies — inconclusive.
