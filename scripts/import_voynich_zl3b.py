#!/usr/bin/env python3
"""Import the Zandbergen-Landini ZL3b Voynich transliteration.

The raw IVTFF file is preserved separately from derived benchmark records.
Derived canonical records use the benchmark S-token convention and are intended
for exploratory unsolved runs only. No plaintext solution is implied.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
UNSOLVED = ROOT / "benchmark" / "unsolved"
STAGING = ROOT / "data_staging" / "voynich" / "transcriptions"
SOURCE_DEFAULT = STAGING / "ZL3b-n.txt"

TRANSCRIPTIONS = UNSOLVED / "sources" / "voynich" / "transcriptions"
DOCUMENTS = UNSOLVED / "sources" / "voynich" / "documents"
METADATA = UNSOLVED / "sources" / "voynich" / "metadata"
RECORDS_PATH = UNSOLVED / "manifest" / "records.jsonl"
SPLITS = UNSOLVED / "splits"

SOURCE_URL = "https://www.voynich.nu/data/ZL3b-n.txt"
SOURCE_PAGE = "https://voynich.nu/transcr.html"
DATA_README_URL = "https://www.voynich.nu/data/000_README.txt"
PUBLIC_OVERVIEW_URLS = [
    "https://en.wikipedia.org/wiki/Voynich_manuscript",
    "https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript",
    "https://collections.library.yale.edu/catalog/2002046",
]
PUBLIC_OVERVIEW_TEXT = (
    "Public-source overview: The Voynich manuscript is an illustrated codex "
    "written in an unknown script/language, with no accepted decipherment. "
    "Its text and illustrations are generally treated as European; Yale's "
    "Beinecke overview describes it as written in Central Europe at the end "
    "of the 15th or during the 16th century, while common modern summaries "
    "also note early-15th-century vellum dating around 1404-1438. The "
    "manuscript includes herbal/botanical, astronomical or astrological, "
    "biological/bathing, cosmological, pharmaceutical, and recipe-like "
    "illustrated sections. These facts are broad provenance/context signals, "
    "not solution hints."
)

PAGE_HEADER_RE = re.compile(r"^<(?P<folio>f[^.>]+)>\s*(?P<meta>.*)$")
LOCUS_RE = re.compile(r"^<(?P<folio>f[^.>,]+)\.(?P<locus>[^,>]+),(?P<kind>[^>]+)>\s*(?P<text>.*)$")
COMMENT_RE = re.compile(r"^#\s?(?P<text>.*)$")
BRACKET_ALT_RE = re.compile(r"\[([^\]:]+):[^\]]+\]")
COMMENT_MARKUP_RE = re.compile(r"<![^>]*>")
ANGLE_MARKUP_RE = re.compile(r"<[^>]*>")
HIGH_ASCII_RE = re.compile(r"@\d+;")
GLYPH_RE = re.compile(r"@\d+;|[A-Za-z?']")


def clean_ivtff_text(text: str) -> str:
    """Return a benchmark-friendly EVA-ish surface string.

    This deliberately makes a simple, documented choice for alternatives:
    choose the first reading. It removes IVTFF comments/paragraph markers and
    treats both certain and uncertain spaces as word separators downstream.
    """

    text = BRACKET_ALT_RE.sub(lambda m: m.group(1), text)
    text = text.replace("{", "").replace("}", "")
    text = COMMENT_MARKUP_RE.sub("", text)
    text = ANGLE_MARKUP_RE.sub("", text)
    text = text.replace("[", "").replace("]", "")
    return text.strip()


def split_words(cleaned: str) -> list[str]:
    words: list[str] = []
    for chunk in re.split(r"[\s.,]+", cleaned):
        chunk = chunk.strip()
        if not chunk:
            continue
        words.append(chunk)
    return words


def glyphs_for_word(word: str) -> list[str]:
    return GLYPH_RE.findall(word)


def read_canvas_map() -> dict[str, dict[str, Any]]:
    path = METADATA / "voynich_canvas_map.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    folio_re = re.compile(r"\bf?\s*0*(\d{1,3})\s*([rv])\s*(\d)?\b", re.IGNORECASE)
    for index, item in enumerate(payload.get("canvases") or []):
        label = str(item.get("label") or "")
        match = folio_re.search(label)
        if not match:
            continue
        n, side, sub = match.group(1), match.group(2).lower(), match.group(3)
        folio = f"f{int(n)}{side}" + (str(sub) if sub else "")
        out[folio] = {
            "label": label,
            "service": item.get("service"),
            "folio_offset": index,
        }
    return out


def parse_zl(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    source_header: list[str] = []
    pages: dict[str, dict[str, Any]] = OrderedDict()
    current: dict[str, Any] | None = None

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        header = PAGE_HEADER_RE.match(line)
        if header:
            folio = header.group("folio")
            current = pages.setdefault(
                folio,
                {
                    "folio": folio,
                    "header": header.group("meta").strip(),
                    "comments": [],
                    "loci": [],
                    "source_start_line": line_no,
                },
            )
            continue

        locus = LOCUS_RE.match(line)
        if locus:
            folio = locus.group("folio")
            current = pages.setdefault(
                folio,
                {
                    "folio": folio,
                    "header": "",
                    "comments": [],
                    "loci": [],
                    "source_start_line": line_no,
                },
            )
            raw_text = locus.group("text").strip()
            cleaned = clean_ivtff_text(raw_text)
            words = split_words(cleaned)
            glyph_words = [glyphs_for_word(word) for word in words]
            glyph_words = [word for word in glyph_words if word]
            current["loci"].append(
                {
                    "line_no": line_no,
                    "locus": locus.group("locus"),
                    "kind": locus.group("kind"),
                    "raw_text": raw_text,
                    "cleaned_text": cleaned,
                    "words": words,
                    "glyph_words": glyph_words,
                }
            )
            continue

        comment = COMMENT_RE.match(line)
        if comment:
            text = comment.group("text")
            if current is None:
                source_header.append(text)
            else:
                current["comments"].append(text)

    return pages, source_header


def build_symbol_map(pages: dict[str, dict[str, Any]]) -> dict[str, str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for page in pages.values():
        for locus in page["loci"]:
            for word in locus["glyph_words"]:
                for glyph in word:
                    seen.setdefault(glyph, None)
    return {glyph: f"S{i:03d}" for i, glyph in enumerate(seen, start=1)}


def canonical_lines(page: dict[str, Any], symbol_map: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for locus in page["loci"]:
        words = []
        for word in locus["glyph_words"]:
            tokens = [symbol_map[glyph] for glyph in word]
            if tokens:
                words.append(" ".join(tokens))
        if words:
            lines.append(" | ".join(words))
    return lines


def diplomatic_lines(page: dict[str, Any]) -> list[str]:
    lines = [
        f"# Folio {page['folio']} from ZL3b-n.txt",
        f"# Header: {page.get('header', '')}",
        "# Columns: locus<TAB>kind<TAB>raw_ivtff<TAB>cleaned_eva_first_alternatives",
    ]
    for locus in page["loci"]:
        lines.append(
            "\t".join(
                [
                    str(locus["locus"]),
                    str(locus["kind"]),
                    str(locus["raw_text"]),
                    str(locus["cleaned_text"]),
                ]
            )
        )
    return lines


def note_lines(page: dict[str, Any], source_header: list[str]) -> list[str]:
    comments = [line for line in page.get("comments", []) if line.strip()]
    lines = [
        f"# Voynich {page['folio']} ZL3b Context Notes",
        "",
        "These notes are copied from comments adjacent to this folio in the "
        "Zandbergen-Landini ZL3b IVTFF transliteration file.",
        "",
        "## Folio Header",
        "",
        f"```text\n<{page['folio']}> {page.get('header', '')}\n```",
        "",
        "## Page Comments",
        "",
    ]
    if comments:
        lines.append("```text")
        lines.extend(comments)
        lines.append("```")
    else:
        lines.append("_No page-specific comments were present in the source file._")
    if source_header:
        lines.extend([
            "",
            "## Source File Header",
            "",
            "```text",
            *[line for line in source_header if line.strip()],
            "```",
        ])
    return lines


def context_layers(page: dict[str, Any], token_count: int, word_count: int, symbol_count: int) -> dict[str, Any]:
    folio = page["folio"]
    comments = " ".join(line.strip() for line in page.get("comments", []) if line.strip())
    comments_short = comments[:900] + ("..." if len(comments) > 900 else "")
    return {
        "minimal": {
            "label": "Minimal archival context",
            "text": (
                f"Record voynich_{folio} is a folio from the Voynich manuscript "
                "(Beinecke MS 408). Date or period: early_15c. Provenance: "
                "Beinecke Rare Book and Manuscript Library, Yale University. "
                f"Manuscript/page identifier: {folio}. This is an unsolved "
                "benchmark-area record."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance", "manuscript_page"],
        },
        "standard": {
            "label": "Standard transliteration context",
            "text": (
                "This record uses a derived canonical transcription from the "
                "Zandbergen-Landini ZL3b EVA/IVTFF transliteration. Plaintext "
                "language is unknown and no accepted solution is available. "
                f"Canonical token count: {token_count}; word groups: {word_count}; "
                f"global canonical symbol count: {symbol_count}. The S-token "
                "mapping represents transliteration units selected by the importer, "
                "not a claim about final Voynich glyph ontology."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": True,
            "source_fields": [
                "transcription_canonical_file",
                "plaintext_language",
                "cipher_type",
                "symbol_count",
                "token_count",
                "word_count",
            ],
        },
        "historical": {
            "label": "Historical/source comments",
            "text": (
                f"{PUBLIC_OVERVIEW_TEXT} Voynich folio {folio}. ZL3b page comments: "
                f"{comments_short if comments_short else 'No page-specific comments present.'} "
                "Notable published attempts include Cheshire 2019, Gibbs 2017, "
                "and Rugg 2004; none is treated as an accepted solution."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": [
                "curation_notes",
                "notable_attempts",
                "associated_documents",
                "public_overview_sources",
            ],
        },
    }


def build_record(
    page: dict[str, Any],
    *,
    token_count: int,
    word_count: int,
    symbol_count: int,
    canvas: dict[str, Any] | None,
) -> dict[str, Any]:
    folio = page["folio"]
    record_id = f"voynich_{folio}"
    image_files: list[str] = []
    local_image = UNSOLVED / "sources" / "voynich" / "images" / f"voynich_{folio}.jpg"
    if local_image.exists():
        image_files.append(f"sources/voynich/images/voynich_{folio}.jpg")
    image_url = None
    if canvas and canvas.get("service"):
        image_url = str(canvas["service"]).rstrip("/") + "/full/2000,/0/default.jpg"

    task_tracks = ["transcription2plaintext"]
    if image_files:
        task_tracks.extend(["image2transcription", "image2hypothesis"])

    rec: dict[str, Any] = {
        "id": record_id,
        "source": "voynich",
        "source_record_id": f"Beinecke_MS408_{folio}_ZL3b",
        "source_url": "https://collections.library.yale.edu/catalog/2002046",
        "task_tracks": task_tracks,
        "rights_class": "hold_for_review",
        "status": "unsolved",
        "partial_solution_evidence": "none",
        "cipher_type": ["unknown"],
        "symbol_set": ["symbolic", "eva_transliteration", "zl3b"],
        "symbol_count": symbol_count,
        "plaintext_language": "",
        "date_or_century": "early_15c",
        "page_count": 1,
        "provenance": "Beinecke Rare Book and Manuscript Library, Yale University, MS 408",
        "transcription_diplomatic_file": f"sources/voynich/transcriptions/{record_id}.zl3b.diplomatic.txt",
        "transcription_canonical_file": f"sources/voynich/transcriptions/{record_id}.zl3b.canonical.txt",
        "manuscript_page": folio,
        "length_chars": token_count,
        "word_boundaries": True,
        "token_count": token_count,
        "word_count": word_count,
        "notable_attempts": [
            "Cheshire 2019 (proto-Romance) — widely rejected",
            "Gibbs 2017 (Latin abbreviation shorthand) — widely rejected",
            "Rugg 2004 (hoax/grille) — structural hypothesis, not a decipherment",
        ],
        "curation_notes": (
            f"Voynich folio {folio} imported from Zandbergen-Landini ZL3b IVTFF "
            "transliteration. Canonical form chooses the first listed alternative "
            "reading, removes IVTFF markup/comments, treats certain and uncertain "
            "spaces as word boundaries, and maps importer-level EVA units to a "
            "global S-token map. The Yale manuscript images are public-domain/open "
            "access, but the ZL transliteration page carries a copyright notice "
            "and no explicit permissive redistribution license was found during "
            "intake; rights_class is therefore hold_for_review."
        ),
        "context_layers": context_layers(page, token_count, word_count, symbol_count),
        "associated_documents": [
            {
                "id": "voynich_public_overview",
                "document_type": "metadata_note",
                "title": "Concise public overview of the Voynich manuscript",
                "summary": (
                    "Short paraphrased overview of the manuscript's unknown "
                    "text, illustrated contents, date/origin context, and "
                    "unsolved status."
                ),
                "rights_class": "linked_only",
                "text_file": "sources/voynich/documents/voynich_public_overview.md",
                "source_url": PUBLIC_OVERVIEW_URLS[0],
                "contains_solution": False,
                "contains_plaintext_hint": False,
                "safe_context_layers": ["historical", "max"],
            },
            {
                "id": f"{record_id}_zl3b_notes",
                "document_type": "metadata_note",
                "title": f"ZL3b source notes for {folio}",
                "summary": "Page-level comments and source header from the ZL3b IVTFF file.",
                "rights_class": "hold_for_review",
                "text_file": f"sources/voynich/documents/{record_id}.zl3b.notes.md",
                "source_url": SOURCE_URL,
                "contains_solution": False,
                "contains_plaintext_hint": False,
                "safe_context_layers": ["historical", "max"],
            },
            {
                "id": f"{record_id}_zl3b_diplomatic",
                "document_type": "transcription",
                "title": f"ZL3b diplomatic transliteration for {folio}",
                "summary": "Raw IVTFF locus text plus importer-cleaned EVA surface text.",
                "rights_class": "hold_for_review",
                "text_file": f"sources/voynich/transcriptions/{record_id}.zl3b.diplomatic.txt",
                "source_url": SOURCE_URL,
                "contains_solution": False,
                "contains_plaintext_hint": False,
                "safe_context_layers": ["standard", "historical", "max"],
            },
        ],
    }
    if image_files:
        rec["image_files"] = image_files
    if canvas:
        rec["image_provenance"] = {
            "iiif_service": canvas.get("service"),
            "requested_width": 2000,
            "fetched_at": date.today().isoformat(),
            "folio_offset": canvas.get("folio_offset"),
            "source_image_url": image_url,
            "local_image_present": bool(image_files),
        }
    return rec


def write_public_overview_doc() -> None:
    DOCUMENTS.mkdir(parents=True, exist_ok=True)
    (DOCUMENTS / "voynich_public_overview.md").write_text(
        "\n".join(
            [
                "# Concise Public Overview of the Voynich Manuscript",
                "",
                PUBLIC_OVERVIEW_TEXT.replace("Public-source overview: ", ""),
                "",
                "## Use in Benchmark Context",
                "",
                "This note is intended as non-solution historical context for "
                "agentic runs. It should help a solver avoid treating the target "
                "as ordinary English, Latin, German, or a known solved cipher, "
                "but it does not provide a plaintext, crib, accepted cipher "
                "family, or accepted decipherment.",
                "",
                "## Sources",
                "",
                *[f"- {url}" for url in PUBLIC_OVERVIEW_URLS],
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_source_docs(source_path: Path, source_header: list[str]) -> None:
    TRANSCRIPTIONS.mkdir(parents=True, exist_ok=True)
    DOCUMENTS.mkdir(parents=True, exist_ok=True)
    METADATA.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, TRANSCRIPTIONS / "ZL3b-n.txt")
    source_md = DOCUMENTS / "SOURCE_ZL3b.md"
    source_md.write_text(
        "\n".join(
            [
                "# Voynich ZL3b Source Notes",
                "",
                f"- Raw source file: `{SOURCE_URL}`",
                f"- Source overview page: `{SOURCE_PAGE}`",
                f"- Data directory README: `{DATA_README_URL}`",
                "- Local preserved copy: `sources/voynich/transcriptions/ZL3b-n.txt`",
                "",
                "## Rights / Licensing",
                "",
                "The Yale/Beinecke manuscript images are public-domain/open-access "
                "materials, but the ZL3b transliteration is a modern scholarly "
                "transliteration. The downloaded source page carries a copyright "
                "notice for René Zandbergen and the data README describes provenance "
                "but does not state an explicit permissive redistribution license. "
                "Derived benchmark records therefore use `rights_class: hold_for_review`.",
                "",
                "## Import Choices",
                "",
                "- Parse IVTFF 2.0 page/locus structure.",
                "- Choose the first alternative reading in bracketed alternatives.",
                "- Remove IVTFF comments and paragraph/drawing markup from canonical text.",
                "- Treat both certain `.` and uncertain `,` spaces as word boundaries.",
                "- Map importer-level EVA/high-ASCII units to a global S-token map.",
                "",
                "## Source Header",
                "",
                "```text",
                *[line for line in source_header if line.strip()],
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    pages, source_header = parse_zl(args.source)
    if args.limit is not None:
        pages = OrderedDict(list(pages.items())[: args.limit])
    symbol_map = build_symbol_map(pages)
    canvas_map = read_canvas_map()

    records: list[dict[str, Any]] = []
    per_page_meta: dict[str, Any] = {}

    for page in pages.values():
        record_id = f"voynich_{page['folio']}"
        lines = canonical_lines(page, symbol_map)
        token_count = sum(len(word.split()) for line in lines for word in line.split(" | "))
        word_count = sum(len(line.split(" | ")) for line in lines)
        if token_count == 0:
            continue
        records.append(
            build_record(
                page,
                token_count=token_count,
                word_count=word_count,
                symbol_count=len(symbol_map),
                canvas=canvas_map.get(page["folio"]),
            )
        )
        per_page_meta[record_id] = {
            "folio": page["folio"],
            "locus_count": len(page["loci"]),
            "token_count": token_count,
            "word_count": word_count,
            "source_start_line": page.get("source_start_line"),
            "comments": page.get("comments") or [],
        }

        if not args.no_write:
            TRANSCRIPTIONS.mkdir(parents=True, exist_ok=True)
            DOCUMENTS.mkdir(parents=True, exist_ok=True)
            (TRANSCRIPTIONS / f"{record_id}.zl3b.canonical.txt").write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )
            (TRANSCRIPTIONS / f"{record_id}.zl3b.diplomatic.txt").write_text(
                "\n".join(diplomatic_lines(page)) + "\n",
                encoding="utf-8",
            )
            (DOCUMENTS / f"{record_id}.zl3b.notes.md").write_text(
                "\n".join(note_lines(page, source_header)) + "\n",
                encoding="utf-8",
            )

    if args.no_write:
        print(f"Would import {len(records)} Voynich ZL3b records")
        print(f"Global symbol count: {len(symbol_map)}")
        return

    write_source_docs(args.source, source_header)
    write_public_overview_doc()
    METADATA.mkdir(parents=True, exist_ok=True)
    (METADATA / "voynich_zl3b_symbol_map.json").write_text(
        json.dumps(
            {
                "source": "voynich_zl3b",
                "source_url": SOURCE_URL,
                "symbol_count": len(symbol_map),
                "symbols": {
                    token: {"glyph_id": glyph, "source_unit": glyph}
                    for glyph, token in symbol_map.items()
                },
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (METADATA / "voynich_zl3b_page_metadata.json").write_text(
        json.dumps(per_page_meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    existing: list[dict[str, Any]] = []
    if RECORDS_PATH.exists():
        for line in RECORDS_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("source") != "voynich":
                existing.append(record)
    RECORDS_PATH.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in existing + records),
        encoding="utf-8",
    )

    SPLITS.mkdir(parents=True, exist_ok=True)
    (SPLITS / "voynich_zl3b_tests.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "test_id": f"{record['id']}_zl3b",
                    "track": "transcription2plaintext",
                    "cipher_system": "voynich_unknown_zl3b",
                    "target_records": [record["id"]],
                    "context_records": [],
                    "description": (
                        f"Voynich {record['manuscript_page']} ZL3b transliteration "
                        "unsolved hypothesis record."
                    ),
                    "agentic_hypothesis": (
                        "Use the ZL3b EVA/IVTFF transliteration to produce "
                        "statistical characterization or structural/plaintext "
                        "hypotheses. No accepted solution exists."
                    ),
                    "stressors": [
                        "unsolved",
                        "unknown_cipher_family",
                        "unknown_language",
                        "voynich",
                        "eva_transliteration",
                    ],
                    "baseline_expected_failure_mode": (
                        "No reliable automated score is available; treat output "
                        "as a hypothesis unless independently validated."
                    ),
                },
                ensure_ascii=False,
            )
            + "\n"
            for record in records
        ),
        encoding="utf-8",
    )

    print(f"Imported Voynich ZL3b records: {len(records)}")
    print(f"Global canonical symbols: {len(symbol_map)}")
    print(f"records.jsonl: {len(existing)} existing non-Voynich + {len(records)} Voynich")
    print(f"split: benchmark/unsolved/splits/voynich_zl3b_tests.jsonl")


if __name__ == "__main__":
    main()
