#!/usr/bin/env python3
"""
Coerce integer-typed `manuscript_page` values to strings across the manifest.

Prepares the manifest for schema S6 which tightens manuscript_page to
`type: string` only. Idempotent.
"""

import json
from pathlib import Path

MANIFEST = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/benchmark/manifest/records.jsonl")


def main():
    records = [json.loads(line) for line in MANIFEST.open() if line.strip()]
    coerced = 0
    for rec in records:
        mp = rec.get("manuscript_page")
        if isinstance(mp, int):
            rec["manuscript_page"] = str(mp)
            coerced += 1

    with MANIFEST.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Records: {len(records)}; coerced manuscript_page int->str: {coerced}")


if __name__ == "__main__":
    main()
