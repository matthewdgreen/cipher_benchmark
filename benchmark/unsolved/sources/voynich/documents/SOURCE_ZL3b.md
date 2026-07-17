# Voynich ZL3b Source Notes

- Raw source file: `https://www.voynich.nu/data/ZL3b-n.txt`
- Source overview page: `https://voynich.nu/transcr.html`
- Data directory README: `https://www.voynich.nu/data/000_README.txt`
- Local preserved copy: `sources/voynich/transcriptions/ZL3b-n.txt`
- Permission note: `sources/voynich/documents/PERMISSION_2026-05-17.md`

## Rights / Licensing

The Yale/Beinecke manuscript images are public-domain/open-access materials.
The ZL3b transliteration is a modern scholarly transliteration by René
Zandbergen and collaborators.

On 2026-05-17, René Zandbergen granted permission by E-mail to use any or all
transliteration files made available at `voynich.nu`. The benchmark therefore
treats the preserved ZL3b source snapshot and its derived benchmark files as
redistributable with attribution, and current Voynich records use
`rights_class: open`.

This permission is preserved locally rather than expressed as a standard public
license text. The benchmark should therefore continue to carry explicit
attribution and preserve the permission note in future exports or migrations.

## Reproducibility Status

The current ZL3b-based import is reproducible as a benchmark transformation:

- source snapshot preserved locally (`ZL3b-n.txt`);
- source version/header preserved below;
- deterministic importer (`scripts/import_voynich_zl3b.py`);
- importer choices documented in this file and in the per-source README.

However, the transliteration itself is not neutral. René explicitly cautioned
that both the transliteration alphabet and the grouping of glyphs into
characters are relatively arbitrary choices for automated processing. This
benchmark import should therefore be read as a documented transliteration view,
not as a final or ontology-free Voynich symbol ground truth.

## Import Choices

- Parse IVTFF 2.0 page/locus structure.
- Choose the first alternative reading in bracketed alternatives.
- Remove IVTFF comments and paragraph/drawing markup from canonical text.
- Treat both certain `.` and uncertain `,` spaces as word boundaries.
- Map importer-level EVA/high-ASCII units to a global S-token map.

## Source Header

```text
=IVTFF Eva- 2.0 M 5
ZL transliteration file, updated from EVMT project
Version 3b of 13/05/2025
```
