#!/usr/bin/env python3
"""Import selected external-tool bundled ciphers as benchmark parity records.

This script intentionally imports only ciphers with an explicit known key in the
source JSON. Unsolved or partly solved famous ciphers belong in diagnostic
metadata, not solved parity splits.
"""
from __future__ import annotations

import json
from pathlib import Path


BENCHMARK = Path(__file__).resolve().parents[1] / "benchmark"
DECIPHER = Path(__file__).resolve().parents[2] / "decipher"
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

IMPORTS = [
    {
        "source_file": "zodiac408.json",
        "id": "tool_zenith_zodiac408",
        "cipher_type": ["homophonic_substitution"],
        "language": "en",
        "description": "Zenith bundled Zodiac 408 reference cipher.",
    },
    {
        "source_file": "goldbug.json",
        "id": "tool_zenith_goldbug",
        "cipher_type": ["simple_substitution"],
        "language": "en",
        "description": "Zenith bundled Gold-Bug reference cipher.",
    },
    {
        "source_file": "horacemann.json",
        "id": "tool_zenith_horacemann",
        "cipher_type": ["simple_substitution"],
        "language": "en",
        "description": "Zenith bundled Horace Mann reference cipher.",
    },
]


def main() -> None:
    source_root = BENCHMARK / "sources" / "tool_builtins"
    transcriptions = source_root / "transcriptions"
    plaintext = source_root / "plaintext"
    metadata = source_root / "metadata"
    transcriptions.mkdir(parents=True, exist_ok=True)
    plaintext.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)

    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    existing = {}
    order = []
    if manifest_path.exists():
        for line in manifest_path.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                existing[rec["id"]] = rec
                order.append(rec["id"])

    imported = []
    for spec in IMPORTS:
        src = ZENITH_CIPHERS / spec["source_file"]
        if not src.exists():
            print(f"missing source: {src}")
            continue
        data = json.loads(src.read_text())
        key = data.get("knownSolutionKey")
        if not key:
            print(f"skipping {src.name}: no knownSolutionKey")
            continue

        record_id = spec["id"]
        ciphertext = [str(sym) for sym in data["ciphertext"]]
        solved = "".join(key.get(sym, "?") for sym in ciphertext).upper()
        canonical = " ".join(ciphertext)

        (transcriptions / f"{record_id}.canonical.txt").write_text(canonical + "\n")
        (plaintext / f"{record_id}.txt").write_text(solved + "\n")
        (metadata / f"{record_id}.json").write_text(
            json.dumps(
                {
                    "source": "Zenith bundled cipher JSON",
                    "source_file": str(src),
                    "rows": data.get("rows"),
                    "columns": data.get("columns"),
                    "known_solution_key": key,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )

        if record_id not in existing:
            order.append(record_id)
        prior = existing.get(record_id, {})
        updated = {
            "id": record_id,
            "source": "tool_builtins",
            "source_record_id": f"zenith:{spec['source_file']}",
            "task_tracks": ["transcription2plaintext"],
            "rights_class": "linked_only",
            "status": "solved_verified",
            "cipher_type": spec["cipher_type"],
            "symbol_set": ["tool_builtin"],
            "symbol_count": len(set(ciphertext)),
            "plaintext_language": spec["language"],
            "date_or_century": "tool_builtin",
            "provenance": "Bundled with Zenith source checkout for parity testing.",
            "solution_reference": "Known solution key bundled in Zenith cipher JSON.",
            "transcription_canonical_file": (
                f"sources/tool_builtins/transcriptions/{record_id}.canonical.txt"
            ),
            "plaintext_file": f"sources/tool_builtins/plaintext/{record_id}.txt",
            "has_key": True,
            "has_inline_plaintext": False,
            "word_boundaries": False,
            "token_count": len(ciphertext),
            "word_count": 0,
            "notes": spec["description"],
            "source_file": f"zenith-inference/src/main/resources/ciphers/{spec['source_file']}",
            "upstream_provenance": "Zenith GPLv3 source distribution",
            "baseline_solvers": ["zenith"],
            "scorable": True,
            "transform_applied": False,
        }
        # Preserve curated context/relationship metadata added after the first
        # import rather than erasing it on an idempotent refresh.
        for field in ("context_layers", "related_records", "associated_documents"):
            if field in prior:
                updated[field] = prior[field]
        existing[record_id] = updated
        imported.append(record_id)

    rows = [existing[record_id] for record_id in order]
    manifest_path.write_text(
        "".join(json.dumps(rec, ensure_ascii=False) + "\n" for rec in rows)
    )
    print(f"Imported/updated {len(imported)} records: {', '.join(imported)}")


if __name__ == "__main__":
    main()
