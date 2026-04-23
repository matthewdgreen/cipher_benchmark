#!/usr/bin/env python3
"""
Relabel Copiale records from rights_class='linked_only' to 'open'.

Basis: Megyesi (DECRYPT, Stockholm University) confirmed on 2026-04-18 that
the Copiale scans may be freely reused. See
Emails_TODO/received/2026-04-18_megyesi_beata.txt.

Idempotent: only rewrites records where source == 'copiale' AND
rights_class != 'open'.
"""

import json
from pathlib import Path

MANIFEST = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/benchmark/manifest/records.jsonl")


def main():
    records = [json.loads(line) for line in MANIFEST.open() if line.strip()]
    changed = 0
    for rec in records:
        if rec.get("source") == "copiale" and rec.get("rights_class") != "open":
            rec["rights_class"] = "open"
            changed += 1

    with MANIFEST.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Records: {len(records)}; Copiale records relabeled to open: {changed}")


if __name__ == "__main__":
    main()
