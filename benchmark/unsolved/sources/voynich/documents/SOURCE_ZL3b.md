# Voynich ZL3b Source Notes

- Raw source file: `https://www.voynich.nu/data/ZL3b-n.txt`
- Source overview page: `https://voynich.nu/transcr.html`
- Data directory README: `https://www.voynich.nu/data/000_README.txt`
- Local preserved copy: `sources/voynich/transcriptions/ZL3b-n.txt`

## Rights / Licensing

The Yale/Beinecke manuscript images are public-domain/open-access materials, but the ZL3b transliteration is a modern scholarly transliteration. The downloaded source page carries a copyright notice for René Zandbergen and the data README describes provenance but does not state an explicit permissive redistribution license. Derived benchmark records therefore use `rights_class: hold_for_review`.

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
