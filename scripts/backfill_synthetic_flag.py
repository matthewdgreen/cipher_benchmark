#!/usr/bin/env python3
"""
Backfill `synthetic: true` and `generation_config` on manifest records
produced by the synthetic-substitution generator.

Identifies synthetic records by `source` ending in `_synth` or `_synth_nb`
(the naming convention used by the simple-substitution generator). Leaves
all other records untouched.

Idempotent: re-running produces no diff once backfill has completed.
"""

import json
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
MANIFEST = BASE / "benchmark" / "manifest" / "records.jsonl"


def is_synthetic_source(source: str) -> bool:
    return source.endswith("_synth") or source.endswith("_synth_nb")


def derive_generation_config(rec: dict) -> dict:
    """Infer minimal generation_config from the record's own fields.

    The original generator params aren't stored per-record, so we record
    what's knowable from the source name and record content. When the
    generator is re-run with richer provenance, this can be overwritten.
    """
    src = rec["source"]
    # Example source names: de_ss_synth, de_ss_synth_nb
    parts = src.split("_")
    lang = parts[0] if parts else ""
    word_boundaries = not src.endswith("_nb")
    return {
        "generator": "synthetic_simple_substitution",
        "params": {
            "language": lang,
            "cipher_family": "simple_substitution",
            "word_boundaries": word_boundaries,
            "source_tag": src,
        },
    }


def main():
    records = [json.loads(line) for line in MANIFEST.open() if line.strip()]
    changed = 0
    for rec in records:
        if not is_synthetic_source(rec.get("source", "")):
            continue
        if rec.get("synthetic") is True and "generation_config" in rec:
            continue
        rec["synthetic"] = True
        if "generation_config" not in rec:
            rec["generation_config"] = derive_generation_config(rec)
        changed += 1

    with MANIFEST.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    total = len(records)
    print(f"Manifest records: {total}")
    print(f"Synthetic records backfilled: {changed}")
    synthetic_total = sum(1 for r in records if r.get("synthetic") is True)
    print(f"Total records flagged synthetic: {synthetic_total}")


if __name__ == "__main__":
    main()
