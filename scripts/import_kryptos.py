#!/usr/bin/env python3
"""Import Kryptos records for polyalphabetic and unsolved-cipher testing."""
from __future__ import annotations

import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
BENCHMARK = REPO / "benchmark"
DECIPHER = REPO.parent / "decipher"
ZENITH_CIPHERS = (
    DECIPHER
    / "other_tools"
    / "zenith-src"
    / "zenith-inference"
    / "src"
    / "main"
    / "resources"
    / "ciphers"
)
AZDECRYPT_CIPHERS = (
    DECIPHER
    / "other_tools"
    / "azdecrypt-src"
    / "AZdecrypt"
    / "Ciphers"
)
CIA_KRYPTOS_URL = "https://www.cia.gov/legacy/museum/artifact/kryptos-sculpture/"


SOLVED = [
    {
        "id": "kryptos_k1",
        "zenith_file": "kryptos1.json",
        "azdecrypt_file": AZDECRYPT_CIPHERS / "Vigenère" / "Kryptos 1.txt",
        "plaintext": "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION",
        "manuscript_page": "K1",
        "periodic_key": "PALIMPSEST",
        "alphabet_keyword": "KRYPTOS",
        "keyed_alphabet": "KRYPTOSABCDEFGHIJLMNQUVWXZ",
        "cipher_type": ["polyalphabetic", "vigenere", "keyed_vigenere", "kryptos"],
        "notes": (
            "Kryptos K1 solved calibration record. Public solution uses a keyed "
            "Vigenere-style alphabet; Decipher's first plain-tabula Vigenere "
            "solver should treat this as a real-world extension target."
        ),
    },
    {
        "id": "kryptos_k2",
        "zenith_file": "kryptos2.json",
        "azdecrypt_file": AZDECRYPT_CIPHERS / "Vigenère" / "Kryptos 2.txt",
        "plaintext": (
            "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS "
            "MAGNETIC FIELD X THE INFORMATION WAS GATHERED AND TRANSMITTED "
            "UNDERGRUUND TO AN UNKNOWN LOCATION X DOES LANGLEY KNOW ABOUT THIS "
            "THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X WHO KNOWS THE EXACT "
            "LOCATION ONLY WW THIS WAS HIS LAST MESSAGE X THIRTY EIGHT DEGREES "
            "FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH SEVENTY SEVEN "
            "DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST ID BY ROWS"
        ),
        "manuscript_page": "K2",
        "periodic_key": "ABSCISSA",
        "alphabet_keyword": "KRYPTOS",
        "keyed_alphabet": "KRYPTOSABCDEFGHIJLMNQUVWXZ",
        "cipher_type": ["polyalphabetic", "vigenere", "keyed_vigenere", "kryptos"],
        "notes": (
            "Kryptos K2 solved calibration record. The source ciphertext includes "
            "question-mark separators/unknowns; use it to test normalization and "
            "keyed-Vigenere support rather than the clean A-Z first slice."
        ),
    },
    {
        "id": "kryptos_k3",
        "zenith_file": "kryptos3.json",
        "azdecrypt_file": AZDECRYPT_CIPHERS / "Transposition" / "Kryptos 3.txt",
        "manuscript_page": "K3",
        "cipher_type": ["transposition", "transmatrix", "kryptos"],
        "transmatrix": {"w1": 24, "w2": 8, "direction": "cw"},
        "drop_non_az": True,
        "notes": (
            "Kryptos K3 solved pure-transposition calibration record. Public "
            "solutions describe this section as a transposition; this benchmark "
            "stores a Blake-compatible TransMatrix replay/search parameterization "
            "for provenance and regression testing. The final nonalphabetic '?' "
            "marker in the local Zenith transcription is excluded from the "
            "runnable A-Z ciphertext."
        ),
    },
]

UNSOLVED = {
    "id": "kryptos_k4",
    "zenith_file": "kryptos4.json",
    "azdecrypt_file": AZDECRYPT_CIPHERS / "Unsolved" / "Kryptos 4.txt",
    "manuscript_page": "K4",
    "cipher_type": ["unknown", "polyalphabetic", "kryptos"],
    "notes": (
        "Kryptos K4 unsolved final section. Public crib fragments exist, but "
        "there is no widely accepted full solution."
    ),
}


def main() -> None:
    import_solved()
    import_unsolved()
    print("Imported/updated Kryptos K1/K2/K3 solved records and K4 unsolved record.")


def import_solved() -> None:
    source_root = BENCHMARK / "sources" / "kryptos"
    transcriptions = source_root / "transcriptions"
    plaintext_dir = source_root / "plaintext"
    metadata_dir = source_root / "metadata"
    for directory in (transcriptions, plaintext_dir, metadata_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    records, order = load_manifest(manifest_path)

    for spec in SOLVED:
        source_ciphertext = load_zenith_cipher(spec["zenith_file"])
        ciphertext = [token for token in source_ciphertext if "A" <= token <= "Z"] if spec.get("drop_non_az") else source_ciphertext
        record_id = spec["id"]
        canonical = format_canonical_letters(ciphertext)
        plaintext = solved_plaintext(spec, ciphertext)
        normalized_plain = normalize_letters(plaintext)

        (transcriptions / f"{record_id}.canonical.txt").write_text(canonical + "\n", encoding="utf-8")
        (plaintext_dir / f"{record_id}.txt").write_text(plaintext + "\n", encoding="utf-8")
        (metadata_dir / f"{record_id}.json").write_text(
            json.dumps(
                {
                    "source": "Kryptos public cipher text, cross-checked against local Zenith/AZdecrypt sources",
                    "zenith_source_file": str(ZENITH_CIPHERS / spec["zenith_file"]),
                    "azdecrypt_source_file": str(spec["azdecrypt_file"]),
                    "plaintext_normalized": normalized_plain,
                    "ciphertext_normalized": "".join(ciphertext),
                    "source_ciphertext_normalized": "".join(source_ciphertext),
                    "known_cipher_note": known_cipher_note(spec),
                    "known_cipher_parameters": known_cipher_parameters(spec),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        if record_id not in records:
            order.append(record_id)
        records[record_id] = {
            "id": record_id,
            "source": "kryptos",
            "source_record_id": f"cia_kryptos:{spec['manuscript_page']}",
            "source_url": CIA_KRYPTOS_URL,
            "task_tracks": ["transcription2plaintext"],
            "rights_class": "linked_only",
            "status": "solved_verified",
            "cipher_type": spec["cipher_type"],
            "symbol_set": ["alphabetic"],
            "symbol_count": len(set(ciphertext)),
            "plaintext_language": "en",
            "date_or_century": "1990",
            "page_count": 1,
            "provenance": "Kryptos sculpture by Jim Sanborn at CIA headquarters; local ciphertext from Zenith/AZdecrypt source checkouts.",
            "solution_reference": "Publicly known Kryptos K1/K2/K3 solution text; ciphertext cross-checked against bundled solver references.",
            "transcription_canonical_file": f"sources/kryptos/transcriptions/{record_id}.canonical.txt",
            "plaintext_file": f"sources/kryptos/plaintext/{record_id}.txt",
            "has_key": True,
            "has_inline_plaintext": False,
            "manuscript_page": spec["manuscript_page"],
            "word_boundaries": False,
            "token_count": len(ciphertext),
            "word_count": 0,
            "notes": spec["notes"],
            "known_cipher_parameters": known_cipher_parameters(spec),
            "context_layers": solved_context_layers(spec),
            "related_records": solved_related_records(record_id),
            "associated_documents": [
                {
                    "id": f"{record_id}_metadata",
                    "document_type": "metadata_note",
                    "title": f"{spec['manuscript_page']} import metadata",
                    "summary": "Local source-file provenance and normalized plaintext/ciphertext checks.",
                    "rights_class": "hold_for_review",
                    "text_file": f"sources/kryptos/metadata/{record_id}.json",
                    "contains_solution": True,
                    "contains_plaintext_hint": True,
                    "safe_context_layers": ["related_solutions", "max"],
                    "notes": "Do not expose this document in blind or standard solver context.",
                }
            ],
        }

    write_manifest(manifest_path, records, order)
    write_solved_split()


def import_unsolved() -> None:
    source_root = BENCHMARK / "unsolved" / "sources" / "kryptos"
    transcriptions = source_root / "transcriptions"
    metadata_dir = source_root / "metadata"
    for directory in (transcriptions, metadata_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest_path = BENCHMARK / "unsolved" / "manifest" / "records.jsonl"
    records, order = load_manifest(manifest_path)

    ciphertext = load_zenith_cipher(UNSOLVED["zenith_file"])
    record_id = UNSOLVED["id"]
    (transcriptions / f"{record_id}.canonical.txt").write_text(
        format_canonical_letters(ciphertext) + "\n",
        encoding="utf-8",
    )
    (metadata_dir / f"{record_id}.json").write_text(
        json.dumps(
            {
                "source": "Kryptos public cipher text, cross-checked against local Zenith/AZdecrypt sources",
                "zenith_source_file": str(ZENITH_CIPHERS / UNSOLVED["zenith_file"]),
                "azdecrypt_source_file": str(UNSOLVED["azdecrypt_file"]),
                "ciphertext_normalized": "".join(ciphertext),
                "known_public_cribs": ["BERLIN", "CLOCK"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    if record_id not in records:
        order.append(record_id)
    records[record_id] = {
        "id": record_id,
        "source": "kryptos",
        "source_record_id": "cia_kryptos:K4",
        "source_url": CIA_KRYPTOS_URL,
        "task_tracks": ["transcription2plaintext", "image2hypothesis"],
        "rights_class": "linked_only",
        "status": "unsolved",
        "partial_solution_evidence": "partial_plaintext_published",
        "cipher_type": UNSOLVED["cipher_type"],
        "symbol_set": ["alphabetic"],
        "symbol_count": len(set(ciphertext)),
        "plaintext_language": "en",
        "date_or_century": "1990",
        "page_count": 1,
        "provenance": "Kryptos sculpture by Jim Sanborn at CIA headquarters; K4 remains unsolved.",
        "manuscript_page": "K4",
        "length_chars": len(ciphertext),
        "notable_attempts": [
            "Publicly released crib fragments include BERLIN and CLOCK.",
            "K1 and K2 are solved keyed Vigenere-style sections; K3 is solved transposition.",
        ],
        "curation_notes": UNSOLVED["notes"],
        "context_layers": unsolved_context_layers(),
        "related_records": [
            {
                "record_id": "kryptos_k1",
                "relationship": "same_artwork_solved_reference",
                "area": "benchmark",
                "solution_available": True,
                "safe_context_layers": ["related_metadata", "related_solutions", "max"],
                "notes": "Solved Kryptos K1 reference; expose plaintext only under explicit related-solution policy.",
            },
            {
                "record_id": "kryptos_k2",
                "relationship": "same_artwork_solved_reference",
                "area": "benchmark",
                "solution_available": True,
                "safe_context_layers": ["related_metadata", "related_solutions", "max"],
                "notes": "Solved Kryptos K2 reference; expose plaintext only under explicit related-solution policy.",
            },
            {
                "record_id": "kryptos_k3",
                "relationship": "same_artwork_solved_reference",
                "area": "benchmark",
                "solution_available": True,
                "safe_context_layers": ["related_metadata", "related_solutions", "max"],
                "notes": "Solved Kryptos K3 pure-transposition reference; expose plaintext only under explicit related-solution policy.",
            },
        ],
        "associated_documents": [
            {
                "id": "kryptos_k4_metadata",
                "document_type": "metadata_note",
                "title": "K4 import metadata",
                "summary": "Local source-file provenance and public crib notes for Kryptos K4.",
                "rights_class": "hold_for_review",
                "text_file": "sources/kryptos/metadata/kryptos_k4.json",
                "contains_solution": False,
                "contains_plaintext_hint": True,
                "safe_context_layers": ["historical", "related_metadata", "max"],
                "notes": "Contains public crib fragments, not a full solution.",
            }
        ],
        "transcription_canonical_file": "sources/kryptos/transcriptions/kryptos_k4.canonical.txt",
    }

    write_manifest(manifest_path, records, order)
    write_unsolved_split()


def solved_context_layers(spec: dict[str, Any]) -> OrderedDict[str, Any]:
    family_text = solved_family_text(spec)
    return OrderedDict([
        (
            "minimal",
            {
                "label": "Minimal artwork context",
                "text": (
                    f"{spec['manuscript_page']} is one section of the Kryptos sculpture, "
                    "installed at CIA headquarters in 1990. This layer gives no plaintext, "
                    "key, or cipher-family hint."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": False,
                "contains_cipher_type_hint": False,
                "source_fields": ["id", "source", "date_or_century", "provenance", "manuscript_page"],
            },
        ),
        (
            "standard",
            {
                "label": "Standard cipher metadata",
                "text": (
                    f"{spec['manuscript_page']} is an English alphabetic Kryptos section "
                    f"classified here as {family_text}. "
                    "It is a solved calibration record, but this context layer does not "
                    "include the plaintext or key."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": True,
                "contains_cipher_type_hint": True,
                "source_fields": ["plaintext_language", "cipher_type", "symbol_set", "symbol_count"],
            },
        ),
        (
            "historical",
            {
                "label": "Historical/background context",
                "text": (
                    "Kryptos is a public sculpture by Jim Sanborn containing four encrypted "
                    "sections. The first three sections are solved; the fourth remains unsolved. "
                    "This layer does not reveal this section's accepted plaintext."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": True,
                "contains_cipher_type_hint": False,
                "source_fields": ["source_url", "provenance", "notes"],
            },
        ),
    ])


def solved_family_text(spec: dict[str, Any]) -> str:
    if spec.get("transmatrix"):
        return "a pure transposition cipher"
    return "a keyed Vigenere-style polyalphabetic cipher"


def solved_related_records(record_id: str) -> list[dict[str, Any]]:
    return [
        {
            "record_id": other_id,
            "relationship": "same_artwork_solved_reference",
            "area": "benchmark",
            "solution_available": True,
            "safe_context_layers": ["related_metadata", "related_solutions", "max"],
            "notes": "Another solved Kryptos section; expose plaintext only under explicit related-solution policy.",
        }
        for other_id in ("kryptos_k1", "kryptos_k2", "kryptos_k3")
        if other_id != record_id
    ]


def unsolved_context_layers() -> OrderedDict[str, Any]:
    return OrderedDict([
        (
            "minimal",
            {
                "label": "Minimal artwork context",
                "text": (
                    "Kryptos K4 is the unsolved final section of the Kryptos sculpture, "
                    "installed at CIA headquarters in 1990. This layer gives no plaintext "
                    "or cipher-family hint."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": False,
                "contains_cipher_type_hint": False,
                "source_fields": ["id", "source", "date_or_century", "provenance", "manuscript_page"],
            },
        ),
        (
            "standard",
            {
                "label": "Standard cipher metadata",
                "text": (
                    "K4 is a 97-character alphabetic English-language Kryptos section. "
                    "It is related to solved Kryptos sections, but the accepted full "
                    "plaintext for K4 is not known."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": True,
                "contains_cipher_type_hint": True,
                "source_fields": ["plaintext_language", "cipher_type", "symbol_set", "symbol_count", "length_chars"],
            },
        ),
        (
            "historical",
            {
                "label": "Historical/background context",
                "text": (
                    "Kryptos contains four encrypted sections. Public hints for K4 include "
                    "crib fragments such as BERLIN and CLOCK; these are partial clues, not "
                    "a full solution."
                ),
                "contains_solution": False,
                "contains_plaintext_hint": True,
                "contains_cipher_type_hint": False,
                "source_fields": ["notable_attempts", "associated_documents", "source_url"],
            },
        ),
    ])


def load_manifest(path: Path) -> tuple[OrderedDict[str, dict[str, Any]], list[str]]:
    records: OrderedDict[str, dict[str, Any]] = OrderedDict()
    order: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            records[record["id"]] = record
            order.append(record["id"])
    return records, order


def write_manifest(path: Path, records: OrderedDict[str, dict[str, Any]], order: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    lines = []
    for record_id in order:
        if record_id in records and record_id not in seen:
            lines.append(json.dumps(records[record_id], ensure_ascii=False))
            seen.add(record_id)
    for record_id, record in records.items():
        if record_id not in seen:
            lines.append(json.dumps(record, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_zenith_cipher(filename: str) -> list[str]:
    data = json.loads((ZENITH_CIPHERS / filename).read_text(encoding="utf-8"))
    return [str(token).upper() for token in data["ciphertext"]]


def format_canonical_letters(tokens: list[str]) -> str:
    return " ".join(tokens)


def normalize_letters(text: str) -> str:
    return re.sub(r"[^A-Z]", "", text.upper())


def solved_plaintext(spec: dict[str, Any], ciphertext: list[str]) -> str:
    if spec.get("transmatrix"):
        params = spec["transmatrix"]
        return "".join(
            transmatrix(
                ciphertext,
                int(params["w1"]),
                int(params["w2"]),
                str(params.get("direction", "cw")).lower() in {"cw", "clockwise"},
            )
        )
    return spec["plaintext"].strip()


def matrix_rotate(tokens: list[str], width: int, clockwise: bool) -> list[str]:
    if width <= 1 or width >= len(tokens):
        return list(tokens)
    rows = (len(tokens) + width - 1) // width
    out: list[str] = []
    if clockwise:
        for col in range(width):
            for row in range(rows - 1, -1, -1):
                idx = row * width + col
                if idx < len(tokens):
                    out.append(tokens[idx])
    else:
        for col in range(width - 1, -1, -1):
            for row in range(rows):
                idx = row * width + col
                if idx < len(tokens):
                    out.append(tokens[idx])
    return out


def transmatrix(tokens: list[str], w1: int, w2: int, clockwise: bool) -> list[str]:
    return matrix_rotate(matrix_rotate(tokens, w1, clockwise), w2, clockwise)


def known_cipher_note(spec: dict[str, Any]) -> str:
    if spec.get("transmatrix"):
        return "Solved Kryptos section; pure transposition with known TransMatrix parameters."
    return "Solved Kryptos section; keyed Vigenere-style alphabet."


def known_cipher_parameters(spec: dict[str, Any]) -> OrderedDict[str, Any]:
    if spec.get("transmatrix"):
        params = spec["transmatrix"]
        return OrderedDict([
            ("type", "transmatrix"),
            ("w1", params["w1"]),
            ("w2", params["w2"]),
            ("direction", params.get("direction", "cw")),
            (
                "notes",
                (
                    "Solution-bearing calibration parameters for known transform replay. "
                    "Do not expose these in blind or standard agent context."
                ),
            ),
        ])
    return OrderedDict([
        ("type", "keyed_vigenere"),
        ("periodic_key", spec["periodic_key"]),
        ("alphabet_keyword", spec["alphabet_keyword"]),
        ("keyed_alphabet", spec["keyed_alphabet"]),
        ("key_advances_over_skipped_symbols", False),
        (
            "notes",
            (
                "Solution-bearing calibration parameters for known-key replay. "
                "Do not expose these in blind or standard agent context."
            ),
        ),
    ])


def write_solved_split() -> None:
    split_path = BENCHMARK / "splits" / "kryptos_tests.jsonl"
    rows = [
        {
            "test_id": "kryptos_k3_transmatrix",
            "track": "transcription2plaintext",
            "cipher_system": "kryptos3 pure transposition transmatrix",
            "target_records": ["kryptos_k3"],
            "context_records": ["kryptos_k1", "kryptos_k2"],
            "description": "Kryptos K3 solved TransMatrix pure-transposition calibration record.",
            "known_cipher_type": "transposition",
            "recommended_agent_tool": "observe_cipher_id_then_transposition_tools",
            "word_boundaries": False,
        },
    ]
    rows = [
        {
            "test_id": "kryptos_k1_keyed_vigenere",
            "track": "transcription2plaintext",
            "cipher_system": "kryptos_keyed_vigenere",
            "target_records": ["kryptos_k1"],
            "context_records": [],
            "description": "Kryptos K1 solved keyed-Vigenere calibration record.",
            "known_cipher_type": "keyed_vigenere",
            "recommended_agent_tool": "observe_cipher_id_then_periodic_tools",
            "word_boundaries": False,
        },
        {
            "test_id": "kryptos_k2_keyed_vigenere",
            "track": "transcription2plaintext",
            "cipher_system": "kryptos_keyed_vigenere",
            "target_records": ["kryptos_k2"],
            "context_records": ["kryptos_k1"],
            "description": "Kryptos K2 solved keyed-Vigenere calibration record.",
            "known_cipher_type": "keyed_vigenere",
            "recommended_agent_tool": "observe_cipher_id_then_periodic_tools",
            "word_boundaries": False,
        },
    ] + rows
    split_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_unsolved_split() -> None:
    split_path = BENCHMARK / "unsolved" / "splits" / "kryptos_unsolved_tests.jsonl"
    split_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "test_id": "kryptos_k4_unsolved",
        "track": "transcription2plaintext",
        "cipher_system": "kryptos_unknown",
        "target_records": ["kryptos_k4"],
        "context_records": ["kryptos_k1", "kryptos_k2"],
        "description": "Kryptos K4 unsolved final section with optional related solved Kryptos context.",
        "known_cipher_type": "unknown",
        "recommended_agent_tool": "observe_cipher_id_then_hypothesis_search",
        "word_boundaries": False,
    }
    split_path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
