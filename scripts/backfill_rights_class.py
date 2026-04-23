#!/usr/bin/env python3
"""
Backfill `rights_class` on manifest records that are missing it.

Policy:
  * synthetic == True  -> 'open' (generated from PD sources per provenance;
    the generator output itself carries no third-party rights).
  * otherwise          -> refuse to guess; print and exit nonzero so the
    curator can resolve by hand.

Idempotent: records that already have rights_class are untouched.
"""

import json
import sys
from pathlib import Path

MANIFEST = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/benchmark/manifest/records.jsonl")


def main():
    records = [json.loads(line) for line in MANIFEST.open() if line.strip()]
    backfilled = 0
    unresolved = []
    for rec in records:
        if rec.get("rights_class"):
            continue
        if rec.get("synthetic") is True:
            rec["rights_class"] = "open"
            backfilled += 1
        else:
            unresolved.append(rec["id"])

    if unresolved:
        print(f"ERROR: {len(unresolved)} non-synthetic records missing rights_class; "
              f"resolve manually before requiring the field.")
        for rid in unresolved[:10]:
            print(f"  {rid}")
        if len(unresolved) > 10:
            print(f"  ... and {len(unresolved) - 10} more")
        sys.exit(1)

    with MANIFEST.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Records: {len(records)}; backfilled rights_class (synthetic->open): {backfilled}")


if __name__ == "__main__":
    main()
