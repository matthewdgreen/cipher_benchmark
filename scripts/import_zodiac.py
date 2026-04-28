#!/usr/bin/env python3
"""Import curated Zodiac cipher records and shared glyph IDs.

This importer intentionally separates two kinds of Zodiac material:

* solved/parity records in benchmark/sources/zodiac, using Zenith's symbolic
  transcriptions plus published/plaintext fixture solutions;
* unsolved or diagnostic variants in benchmark/unsolved/sources/zodiac, using
  source-preserving byte transcriptions from zkdecrypto where no vetted visual
  glyph crosswalk is available.

The global glyph map is generated deterministically. Zenith symbolic glyphs
are the canonical source of real Zodiac glyph IDs. zkdecrypto byte encodings
are crosswalked per source file by position against matching Zenith records
when possible; artificial variant-only bytes receive ZV### IDs.
"""
from __future__ import annotations

import json
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
ZENITH_CONFIG = (
    DECIPHER
    / "other_tools"
    / "zenith-src"
    / "zenith-inference"
    / "src"
    / "main"
    / "resources"
    / "config"
    / "zenith.json"
)
ZK_CIPHERS = (
    DECIPHER
    / "other_tools"
    / "zkdecrypto-src"
    / "zkdecrypto-lite"
    / "cipher"
)
Z340_PLAINTEXT = (
    DECIPHER
    / "fixtures"
    / "benchmarks"
    / "zodiac340_known_replay"
    / "sources"
    / "zodiac340"
    / "plaintexts"
    / "zodiac340_solution.txt"
)


SOLVED_IMPORTS = [
    {
        "id": "zodiac408_zenith_global",
        "zenith_file": "zodiac408.json",
        "cipher_type": ["homophonic_substitution", "zodiac"],
        "solution": "known_solution_key",
        "notes": "Zodiac 408 reference cipher, re-tokenized with global Zodiac glyph IDs.",
    },
    {
        "id": "zodiac340_zenith_original",
        "zenith_file": "zodiac340-original.json",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340"],
        "solution": "z340_plaintext_fixture",
        "notes": (
            "Zodiac 340 original-order cipher from Zenith, re-tokenized with "
            "global Zodiac glyph IDs. Requires transposition plus homophonic solving."
        ),
    },
]


UNSOLVED_VARIANTS = [
    {
        "id": "zodiac340_zkdecrypto_unsolved",
        "source_file": "340.zodiac.unsolved.txt",
        "description": "Zodiac 340 in zkdecrypto byte encoding.",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340"],
    },
    {
        "id": "zodiac340_zkdecrypto_noplus",
        "source_file": "340.zodiac.noplus.txt",
        "description": "Zodiac 340 variant with plus signs removed; length is 316.",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340_variant"],
    },
    {
        "id": "zodiac340_zkdecrypto_uniplus",
        "source_file": "340.zodiac.uniplus.txt",
        "description": "Zodiac 340 variant with plus signs replaced by unique symbols.",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340_variant"],
    },
    {
        "id": "zodiac340_zkdecrypto_oxcart",
        "source_file": "340.zodiac.oxcart.txt",
        "description": "Zodiac 340 oxcart-route variant from zkdecrypto.",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340_variant"],
    },
    {
        "id": "zodiac153_zkdecrypto_unsolved",
        "source_file": "153.zodiac.unsolved.txt",
        "description": "First 153 symbols of Zodiac 340 in zkdecrypto byte encoding.",
        "cipher_type": ["homophonic_substitution", "transposition", "zodiac340_fragment"],
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_zenith_cipher(name: str) -> dict[str, Any]:
    path = ZENITH_CIPHERS / name
    if not path.exists():
        raise FileNotFoundError(path)
    return load_json(path)


def read_zk_tokens(name: str) -> list[int]:
    path = ZK_CIPHERS / name
    if not path.exists():
        raise FileNotFoundError(path)
    return [byte for byte in path.read_bytes() if byte not in (10, 13)]


def load_manifest(path: Path) -> tuple[OrderedDict[str, dict[str, Any]], list[str]]:
    records: OrderedDict[str, dict[str, Any]] = OrderedDict()
    order: list[str] = []
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            records[rec["id"]] = rec
            order.append(rec["id"])
    return records, order


def write_manifest(path: Path, records: OrderedDict[str, dict[str, Any]], order: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    rows = []
    for record_id in order:
        if record_id in records and record_id not in seen:
            rows.append(records[record_id])
            seen.add(record_id)
    for record_id, record in records.items():
        if record_id not in seen:
            rows.append(record)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def compact_transform_steps() -> list[dict[str, Any]]:
    """Extract Zenith's applied ciphertext transformers without UI form noise."""
    if not ZENITH_CONFIG.exists():
        return []
    config = load_json(ZENITH_CONFIG)
    for cipher_config in config.get("cipherConfigurations", []):
        if cipher_config.get("cipherName") != "zodiac340-transformed":
            continue
        steps = []
        for step in cipher_config.get("appliedCiphertextTransformers", []):
            form = step.get("form") or {}
            steps.append(
                {
                    "transformer_name": step.get("name"),
                    "data": form.get("model") or {},
                }
            )
        return steps
    return []


def add_global_id(
    symbol_to_id: OrderedDict[str, str],
    glyph_ids: OrderedDict[str, dict[str, Any]],
    symbol: str,
    *,
    source: str,
    source_symbol: str,
    display: str | None = None,
) -> str:
    if symbol not in symbol_to_id:
        glyph_id = f"Z{len(symbol_to_id) + 1:03d}"
        symbol_to_id[symbol] = glyph_id
        glyph_ids[glyph_id] = {
            "display": display or symbol,
            "canonical_zenith_symbol": symbol,
            "sources": [],
        }
    glyph_id = symbol_to_id[symbol]
    source_entry = {"source": source, "symbol": source_symbol}
    if source_entry not in glyph_ids[glyph_id]["sources"]:
        glyph_ids[glyph_id]["sources"].append(source_entry)
    return glyph_id


def build_glyph_map() -> dict[str, Any]:
    symbol_to_id: OrderedDict[str, str] = OrderedDict()
    glyph_ids: OrderedDict[str, dict[str, Any]] = OrderedDict()
    source_symbol_to_id: dict[str, dict[str, str]] = {}

    zenith_sources = ["zodiac408.json", "zodiac340-original.json"]
    for name in zenith_sources:
        data = read_zenith_cipher(name)
        source_key = f"zenith:{name}"
        source_symbol_to_id[source_key] = {}
        for symbol in map(str, data["ciphertext"]):
            glyph_id = add_global_id(
                symbol_to_id,
                glyph_ids,
                symbol,
                source=source_key,
                source_symbol=symbol,
            )
            source_symbol_to_id[source_key][symbol] = glyph_id

    # Crosswalk zkdecrypto byte encodings per source file by positional
    # alignment. The same byte can denote different glyphs across Zodiac files,
    # so this mapping is deliberately source-scoped.
    aligned = [
        ("408.zodiac.solved.txt", "zodiac408.json"),
        ("340.zodiac.unsolved.txt", "zodiac340-original.json"),
    ]
    for zk_name, zenith_name in aligned:
        zk_tokens = read_zk_tokens(zk_name)
        zenith_tokens = list(map(str, read_zenith_cipher(zenith_name)["ciphertext"]))
        if len(zk_tokens) != len(zenith_tokens):
            raise ValueError(f"cannot align {zk_name} to {zenith_name}: length mismatch")
        source_key = f"zkdecrypto:{zk_name}:byte"
        source_symbol_to_id[source_key] = {}
        for byte, zenith_symbol in zip(zk_tokens, zenith_tokens):
            byte_symbol = f"0x{byte:02X}"
            glyph_id = source_symbol_to_id[f"zenith:{zenith_name}"][zenith_symbol]
            source_symbol_to_id[source_key][byte_symbol] = glyph_id
            source_entry = {"source": source_key, "symbol": byte_symbol}
            if source_entry not in glyph_ids[glyph_id]["sources"]:
                glyph_ids[glyph_id]["sources"].append(source_entry)

    variant_id_count = 0
    for spec in UNSOLVED_VARIANTS:
        zk_name = spec["source_file"]
        source_key = f"zkdecrypto:{zk_name}:byte"
        if source_key in source_symbol_to_id:
            continue
        base_map = source_symbol_to_id.get("zkdecrypto:340.zodiac.unsolved.txt:byte", {})
        source_symbol_to_id[source_key] = {}
        for byte in sorted(set(read_zk_tokens(zk_name))):
            byte_symbol = f"0x{byte:02X}"
            if byte_symbol in base_map:
                glyph_id = base_map[byte_symbol]
            else:
                variant_id_count += 1
                glyph_id = f"ZV{variant_id_count:03d}"
                glyph_ids[glyph_id] = {
                    "display": byte_symbol,
                    "canonical_zenith_symbol": None,
                    "variant_only": True,
                    "sources": [],
                    "notes": (
                        "Variant-only byte not crosswalked to a real Zodiac glyph. "
                        "This commonly occurs in synthetic zkdecrypto variants such "
                        "as uniplus."
                    ),
                }
            source_symbol_to_id[source_key][byte_symbol] = glyph_id
            source_entry = {"source": source_key, "symbol": byte_symbol}
            if source_entry not in glyph_ids[glyph_id]["sources"]:
                glyph_ids[glyph_id]["sources"].append(source_entry)

    return {
        "schema": "zodiac_glyph_map_v1",
        "id_policy": (
            "Z### IDs denote real Zodiac glyphs as represented by Zenith symbolic "
            "tokens. ZV### IDs denote variant-only/artificial symbols that do not "
            "yet have a vetted visual glyph identity."
        ),
        "normalization_caveat": (
            "zkdecrypto byte values are source-scoped. The same byte can denote "
            "different Zenith glyph tokens in different files, so consumers must "
            "use source_symbol_to_id with the full source key."
        ),
        "glyph_ids": glyph_ids,
        "source_symbol_to_id": source_symbol_to_id,
    }


def ids_for_zenith_tokens(glyph_map: dict[str, Any], zenith_name: str, tokens: list[str]) -> list[str]:
    mapping = glyph_map["source_symbol_to_id"][f"zenith:{zenith_name}"]
    return [mapping[token] for token in tokens]


def ids_for_zk_tokens(glyph_map: dict[str, Any], zk_name: str, tokens: list[int]) -> list[str]:
    mapping = glyph_map["source_symbol_to_id"][f"zkdecrypto:{zk_name}:byte"]
    return [mapping[f"0x{token:02X}"] for token in tokens]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def import_solved(glyph_map: dict[str, Any]) -> list[str]:
    source_root = BENCHMARK / "sources" / "zodiac"
    transcriptions = source_root / "transcriptions"
    plaintexts = source_root / "plaintext"
    metadata = source_root / "metadata"
    for directory in (transcriptions, plaintexts, metadata):
        directory.mkdir(parents=True, exist_ok=True)

    write_json(metadata / "zodiac_glyph_map.json", glyph_map)
    # Keep the generic Decipher BenchmarkLoader convention working for this
    # source family: sources/<source>/metadata/<source>_symbol_map.json.
    write_json(metadata / "zodiac_symbol_map.json", glyph_map)
    write_json(metadata / "zodiac340_zenith_transform_pipeline.json", compact_transform_steps())

    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    records, order = load_manifest(manifest_path)

    imported = []
    for spec in SOLVED_IMPORTS:
        record_id = spec["id"]
        zenith_name = spec["zenith_file"]
        data = read_zenith_cipher(zenith_name)
        original_tokens = [str(token) for token in data["ciphertext"]]
        global_tokens = ids_for_zenith_tokens(glyph_map, zenith_name, original_tokens)
        (transcriptions / f"{record_id}.canonical.txt").write_text(
            " ".join(global_tokens) + "\n"
        )

        if spec["solution"] == "known_solution_key":
            key = data.get("knownSolutionKey")
            if not key:
                raise ValueError(f"{zenith_name} has no knownSolutionKey")
            solved = "".join(key.get(token, "?") for token in original_tokens).upper()
            solution_reference = "Known solution key bundled in Zenith cipher JSON."
            has_key = True
        elif spec["solution"] == "z340_plaintext_fixture":
            solved = Z340_PLAINTEXT.read_text().strip().upper()
            solution_reference = (
                "Published Zodiac 340 solution text, mirrored in Decipher's "
                "zodiac340_known_replay fixture."
            )
            has_key = False
        else:
            raise ValueError(f"unknown solution mode: {spec['solution']}")
        (plaintexts / f"{record_id}.txt").write_text(solved + "\n")

        metadata_payload = {
            "source": "Zodiac curated import",
            "source_file": str(ZENITH_CIPHERS / zenith_name),
            "global_glyph_map": "zodiac_glyph_map.json",
            "source_symbol_map_key": f"zenith:{zenith_name}",
            "rows": data.get("rows"),
            "columns": data.get("columns"),
            "original_source_tokens": original_tokens,
            "global_glyph_tokens": global_tokens,
        }
        if record_id == "zodiac340_zenith_original":
            metadata_payload["known_transform_pipeline_file"] = (
                "zodiac340_zenith_transform_pipeline.json"
            )
            metadata_payload["known_transform_pipeline_note"] = (
                "Zenith config names this selected cipher zodiac340-transformed, "
                "but the checked-in zodiac340 original/transformed ciphertext JSONs "
                "are identical. This pipeline is therefore recorded as solver "
                "provenance, not as a separate transformed transcription file."
            )
        write_json(metadata / f"{record_id}.json", metadata_payload)

        preserved = {
            key: records.get(record_id, {}).get(key)
            for key in ("context_layers", "related_records", "associated_documents")
            if records.get(record_id, {}).get(key) is not None
        }

        if record_id not in records:
            order.append(record_id)
        records[record_id] = {
            "id": record_id,
            "source": "zodiac",
            "source_record_id": f"zenith:{zenith_name}",
            "task_tracks": ["transcription2plaintext"],
            "rights_class": "linked_only",
            "status": "solved_verified",
            "cipher_type": spec["cipher_type"],
            "symbol_set": ["zodiac_global_glyph_id"],
            "symbol_count": len(set(global_tokens)),
            "plaintext_language": "en",
            "date_or_century": "1969",
            "provenance": "Curated from Zenith Zodiac cipher JSONs for parity testing.",
            "solution_reference": solution_reference,
            "transcription_canonical_file": (
                f"sources/zodiac/transcriptions/{record_id}.canonical.txt"
            ),
            "plaintext_file": f"sources/zodiac/plaintext/{record_id}.txt",
            "has_key": has_key,
            "has_inline_plaintext": False,
            "word_boundaries": False,
            "token_count": len(global_tokens),
            "word_count": 0,
            "notes": spec["notes"],
        }
        records[record_id].update(preserved)
        imported.append(record_id)

    write_manifest(manifest_path, records, order)
    return imported


def import_unsolved_variants(glyph_map: dict[str, Any]) -> list[str]:
    source_root = BENCHMARK / "unsolved" / "sources" / "zodiac"
    transcriptions = source_root / "transcriptions"
    metadata = source_root / "metadata"
    for directory in (transcriptions, metadata):
        directory.mkdir(parents=True, exist_ok=True)
    write_json(metadata / "zodiac_glyph_map.json", glyph_map)

    manifest_path = BENCHMARK / "unsolved" / "manifest" / "records.jsonl"
    records, order = load_manifest(manifest_path)

    imported = []
    for spec in UNSOLVED_VARIANTS:
        record_id = spec["id"]
        zk_name = spec["source_file"]
        raw_tokens = read_zk_tokens(zk_name)
        global_tokens = ids_for_zk_tokens(glyph_map, zk_name, raw_tokens)
        (transcriptions / f"{record_id}.canonical.txt").write_text(
            " ".join(global_tokens) + "\n"
        )
        write_json(
            metadata / f"{record_id}.json",
            {
                "source": "zkdecrypto-lite cipher directory",
                "source_file": str(ZK_CIPHERS / zk_name),
                "global_glyph_map": "zodiac_glyph_map.json",
                "source_symbol_map_key": f"zkdecrypto:{zk_name}:byte",
                "normalization": (
                    "Byte tokens were mapped through the source-scoped Zodiac "
                    "glyph map. Variant-only bytes use ZV### IDs."
                ),
                "raw_byte_tokens_hex": [f"0x{byte:02X}" for byte in raw_tokens],
                "global_glyph_tokens": global_tokens,
            },
        )

        preserved = {
            key: records.get(record_id, {}).get(key)
            for key in ("context_layers", "related_records", "associated_documents")
            if records.get(record_id, {}).get(key) is not None
        }

        if record_id not in records:
            order.append(record_id)
        records[record_id] = {
            "id": record_id,
            "source": "zodiac",
            "source_record_id": f"zkdecrypto:{zk_name}",
            "task_tracks": ["transcription2plaintext"],
            "rights_class": "linked_only",
            "status": "unsolved",
            "partial_solution_evidence": (
                "partial_plaintext_published"
                if record_id == "zodiac153_zkdecrypto_unsolved"
                else "none"
            ),
            "cipher_type": spec["cipher_type"],
            "symbol_set": ["zodiac_global_glyph_id"],
            "symbol_count": len(set(global_tokens)),
            "plaintext_language": "en",
            "date_or_century": "1969",
            "page_count": 1,
            "provenance": "Curated from the zkdecrypto-lite bundled cipher files.",
            "transcription_canonical_file": (
                f"sources/zodiac/transcriptions/{record_id}.canonical.txt"
            ),
            "length_chars": len(global_tokens),
            "notable_attempts": [
                "Zodiac 340 was solved in 2020 by Oranchak, Van Eycke, and Blake.",
            ],
            "curation_notes": spec["description"],
        }
        records[record_id].update(preserved)
        imported.append(record_id)

    write_manifest(manifest_path, records, order)
    return imported


def write_splits() -> None:
    splits = BENCHMARK / "splits"
    splits.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "test_id": "zodiac_408_global_parity",
            "track": "transcription2plaintext",
            "cipher_system": "zodiac408",
            "target_records": ["zodiac408_zenith_global"],
            "context_records": [],
            "description": "Zodiac 408 using benchmark-global Zodiac glyph IDs.",
            "parity_family": "zodiac_homophonic",
            "recommended_agent_tool": "search_homophonic_anneal",
            "baseline_solvers": ["zenith", "zkdecrypto-lite"],
            "expected_baseline_status": "solved",
            "expected_min_char_accuracy": 0.95,
            "known_cipher_type": "homophonic_substitution",
            "word_boundaries": False,
        },
        {
            "test_id": "zodiac_340_original_parity",
            "track": "transcription2plaintext",
            "cipher_system": "zodiac340_transposition_homophonic",
            "target_records": ["zodiac340_zenith_original"],
            "context_records": [],
            "description": (
                "Zodiac 340 original-order benchmark record using global Zodiac "
                "glyph IDs."
            ),
            "parity_family": "zodiac_transposition_homophonic",
            "recommended_agent_tool": "transform_search_then_homophonic_anneal",
            "baseline_solvers": ["decipher"],
            "expected_baseline_status": "solved",
            "expected_min_char_accuracy": 0.90,
            "known_cipher_type": "transposition_homophonic",
            "word_boundaries": False,
            "known_transform_pipeline_file": (
                "sources/zodiac/metadata/zodiac340_zenith_transform_pipeline.json"
            ),
        },
    ]
    (splits / "parity_zodiac340.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )


def write_readme() -> None:
    readme = BENCHMARK / "sources" / "zodiac" / "README.md"
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text(
        """# Zodiac Source Family

This source family holds curated Zodiac benchmark records that use global
Zodiac glyph IDs (`Z001`, `Z002`, ...). The ID map is generated by
`scripts/import_zodiac.py` and stored at
`sources/zodiac/metadata/zodiac_glyph_map.json`. A loader-convention alias is
also written to `sources/zodiac/metadata/zodiac_symbol_map.json`.

`Z###` IDs denote real Zodiac glyphs as represented by Zenith symbolic cipher
tokens. `ZV###` IDs denote variant-only/artificial symbols, currently used for
zkdecrypto variants such as `uniplus` where plus signs were replaced with
unique non-historical placeholders.

Important caveat: zkdecrypto byte encodings are source-scoped. The same byte
value can represent different Zenith glyph tokens in different source files.
Consumers should therefore use the `source_symbol_to_id` table with the full
source key, not a global byte-to-glyph table.
"""
    )


def main() -> None:
    glyph_map = build_glyph_map()
    solved = import_solved(glyph_map)
    unsolved = import_unsolved_variants(glyph_map)
    write_splits()
    write_readme()
    print(f"Imported solved Zodiac records: {', '.join(solved)}")
    print(f"Imported unsolved Zodiac variants: {', '.join(unsolved)}")


if __name__ == "__main__":
    main()
