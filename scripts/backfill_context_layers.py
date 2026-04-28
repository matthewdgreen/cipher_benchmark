#!/usr/bin/env python3
"""Backfill tiered solver-facing context metadata.

The context layers are intentionally concise and policy-neutral. They give
benchmark runners enough structure to test blind/minimal/standard/stronger
context modes without forcing every solver to consume the same prose.
"""
from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
BENCHMARK = REPO / "benchmark"


LANG_NAMES = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "la": "Latin",
    "hu": "Hungarian",
    "nl": "Dutch",
    "": "unknown",
}


SOURCE_DESCRIPTIONS = {
    "borg": "a handwritten page from MSS Borg.lat.898",
    "copiale": "a handwritten page from the Copiale cipher manuscript",
    "decode_gallica": "a manuscript page represented in DECODE/Gallica metadata",
    "tool_builtins": "a reference cipher bundled with an external solver",
    "zodiac": "a Zodiac cipher record curated from external solver transcriptions",
    "voynich": "a manuscript folio from the Voynich manuscript",
}


def read_jsonl(path: Path) -> list[OrderedDict[str, Any]]:
    rows: list[OrderedDict[str, Any]] = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line, object_pairs_hook=OrderedDict))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def lang_name(code: str | None) -> str:
    if code is None:
        return "unknown"
    return LANG_NAMES.get(code, code)


def record_kind(record: dict[str, Any]) -> str:
    source = record.get("source", "")
    if source in SOURCE_DESCRIPTIONS:
        return SOURCE_DESCRIPTIONS[source]
    if record.get("synthetic"):
        return "a synthetic benchmark cipher generated from public-domain prose"
    if source.endswith("_synth") or "_ss_synth" in source:
        return "a synthetic benchmark cipher generated from public-domain prose"
    return f"a benchmark record from source family {source!r}"


def join_nonempty(parts: list[str]) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def minimal_layer(record: dict[str, Any], *, unsolved: bool = False) -> dict[str, Any]:
    fields = ["id", "source", "date_or_century", "provenance", "task_tracks"]
    page = record.get("manuscript_page")
    if page is not None:
        fields.append("manuscript_page")
    text = join_nonempty(
        [
            f"Record {record['id']} is {record_kind(record)}.",
            f"Date or period: {record.get('date_or_century', 'unknown')}.",
            f"Provenance: {record.get('provenance', 'unknown')}.",
            f"Task tracks: {', '.join(record.get('task_tracks', []))}.",
            f"Manuscript/page identifier: {page}." if page is not None else "",
            (
                "This is an unsolved/disputed benchmark-area record."
                if unsolved
                else "This layer contains no plaintext, key, or solution reference."
            ),
        ]
    )
    return {
        "label": "Minimal archival context",
        "text": text,
        "contains_solution": False,
        "contains_plaintext_hint": False,
        "contains_cipher_type_hint": False,
        "source_fields": fields,
    }


def standard_layer(record: dict[str, Any], *, unsolved: bool = False) -> dict[str, Any]:
    fields = [
        "plaintext_language",
        "cipher_type",
        "symbol_set",
        "symbol_count",
        "word_boundaries",
        "token_count",
        "length_chars",
        "partial_solution_evidence",
    ]
    cipher_type = ", ".join(record.get("cipher_type", [])) or "unknown"
    symbol_set = ", ".join(record.get("symbol_set", [])) or "unknown"
    text = join_nonempty(
        [
            f"Hypothesized/plaintext language: {lang_name(record.get('plaintext_language'))}.",
            f"Cipher family labels: {cipher_type}.",
            f"Symbol set labels: {symbol_set}.",
            (
                f"Distinct symbols: {record['symbol_count']}."
                if "symbol_count" in record
                else ""
            ),
            f"Token count: {record['token_count']}." if "token_count" in record else "",
            f"Approximate length: {record['length_chars']} cipher characters."
            if "length_chars" in record
            else "",
            (
                f"Word boundaries preserved: {record['word_boundaries']}."
                if "word_boundaries" in record
                else ""
            ),
            (
                f"Partial-solution evidence category: {record['partial_solution_evidence']}."
                if unsolved and record.get("partial_solution_evidence")
                else ""
            ),
        ]
    )
    return {
        "label": "Standard benchmark context",
        "text": text,
        "contains_solution": False,
        "contains_plaintext_hint": bool(record.get("plaintext_language")),
        "contains_cipher_type_hint": bool(record.get("cipher_type")),
        "source_fields": [field for field in fields if field in record],
    }


def historical_layer(record: dict[str, Any], *, unsolved: bool = False) -> dict[str, Any] | None:
    parts: list[str] = []
    fields: list[str] = []
    if record.get("curation_notes"):
        parts.append(record["curation_notes"])
        fields.append("curation_notes")
    if record.get("notes"):
        parts.append(record["notes"])
        fields.append("notes")
    if unsolved and record.get("notable_attempts"):
        attempts = "; ".join(record["notable_attempts"][:4])
        parts.append(f"Notable published or community attempts: {attempts}.")
        fields.append("notable_attempts")

    source = record.get("source")
    if source == "zodiac":
        parts.append(
            "The Zodiac ciphers are associated with letters attributed to the "
            "Zodiac Killer in 1969-1970. This contextual fact may influence "
            "plausible plaintext genre and tone, but it is not itself a solution."
        )
        fields.append("source")
    elif source == "borg":
        parts.append(
            "The Borg manuscript is a historical Latin cipher manuscript; known "
            "published context describes medical and pharmaceutical material."
        )
        fields.append("source")
    elif source == "copiale":
        parts.append(
            "The Copiale manuscript is an eighteenth-century German manuscript "
            "associated with a secret society context."
        )
        fields.append("source")

    if not parts:
        return None

    return {
        "label": "Historical/background context",
        "text": join_nonempty(parts),
        "contains_solution": False,
        "contains_plaintext_hint": source in {"borg", "copiale", "zodiac"},
        "contains_cipher_type_hint": False,
        "source_fields": fields,
    }


def context_layers(record: dict[str, Any], *, unsolved: bool = False) -> OrderedDict[str, Any]:
    layers: OrderedDict[str, Any] = OrderedDict()
    layers["minimal"] = minimal_layer(record, unsolved=unsolved)
    layers["standard"] = standard_layer(record, unsolved=unsolved)
    historical = historical_layer(record, unsolved=unsolved)
    if historical:
        layers["historical"] = historical
    return layers


def zodiac_related(record: dict[str, Any], *, unsolved: bool = False) -> list[dict[str, Any]]:
    record_id = record.get("id", "")
    related: list[dict[str, Any]] = []
    if record_id == "zodiac340_zenith_original":
        related.append(
            {
                "record_id": "zodiac408_zenith_global",
                "relationship": "same_author_family_known_solution",
                "area": "benchmark",
                "solution_available": True,
                "safe_context_layers": ["related_metadata", "related_solutions"],
                "notes": (
                    "Zodiac 408 is a solved Zodiac homophonic cipher and may be "
                    "useful as same-author/same-era context when explicitly allowed."
                ),
            }
        )
    elif record_id == "zodiac408_zenith_global":
        related.append(
            {
                "record_id": "zodiac340_zenith_original",
                "relationship": "same_author_family_solved_record",
                "area": "benchmark",
                "solution_available": True,
                "safe_context_layers": ["related_metadata", "related_solutions"],
                "notes": (
                    "Zodiac 340 is a solved but transposition+homophonic Zodiac "
                    "cipher; use only under explicit related-context policies."
                ),
            }
        )
    elif record_id.startswith("zodiac340_zkdecrypto") or record_id.startswith("zodiac153_"):
        related.extend(
            [
                {
                    "record_id": "zodiac340_zenith_original",
                    "relationship": "same_cipher_or_fragment_solved_reference",
                    "area": "benchmark",
                    "solution_available": True,
                    "safe_context_layers": ["related_metadata", "related_solutions"],
                    "notes": (
                        "The benchmark Zodiac 340 record is a solved reference "
                        "for the same cipher family; expose plaintext only under "
                        "an explicit related-solutions policy."
                    ),
                },
                {
                    "record_id": "zodiac408_zenith_global",
                    "relationship": "same_author_family_known_solution",
                    "area": "benchmark",
                    "solution_available": True,
                    "safe_context_layers": ["related_metadata", "related_solutions"],
                    "notes": (
                        "Zodiac 408 is a solved Zodiac homophonic cipher and may "
                        "provide same-author context when explicitly allowed."
                    ),
                },
            ]
        )
    return related


def apply(path: Path, *, unsolved: bool = False) -> None:
    rows = read_jsonl(path)
    for record in rows:
        record["context_layers"] = context_layers(record, unsolved=unsolved)
        related = zodiac_related(record, unsolved=unsolved)
        if related:
            record["related_records"] = related
        elif "related_records" in record:
            del record["related_records"]
    write_jsonl(path, rows)
    print(f"Backfilled context layers in {path} ({len(rows)} records)")


def main() -> None:
    apply(BENCHMARK / "manifest" / "records.jsonl")
    apply(BENCHMARK / "unsolved" / "manifest" / "records.jsonl", unsolved=True)


if __name__ == "__main__":
    main()
