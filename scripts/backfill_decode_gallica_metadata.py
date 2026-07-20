#!/usr/bin/env python3
"""Backfill historical dates and structured Gallica image provenance.

This migration is intentionally idempotent. It uses the checked-in DECODE
detail snapshot and Gallica mapping/offset tables; it does not access the
network or redownload images.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backfill_context_layers import context_layers
from create_decode_gallica_pilot import decode_date_bounds, image_provenance, load_offsets


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "benchmark" / "manifest" / "records.jsonl"
MAPPING = REPO / "data_staging" / "decode_gallica_mapping.json"
DETAILS = REPO / "data_staging" / "decode_decrypted_ciphers_detail.jsonl"
HISTORICAL_FETCH_DATE = "2026-04-15"


def read_details() -> dict[str, dict[str, Any]]:
    result = {}
    for line in DETAILS.read_text().splitlines():
        if line.strip():
            record = json.loads(line)["records"]
            result[str(record["id"])] = record
    return result


def read_mapping() -> dict[str, dict[str, Any]]:
    data = json.loads(MAPPING.read_text())
    return {str(row["decode_id"]): row for row in data["records"]}


def migrate(*, check: bool = False) -> tuple[int, int]:
    details = read_details()
    mapping = read_mapping()
    offsets, _ = load_offsets()
    rows = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    changed = 0
    decode_count = 0

    for record in rows:
        if record.get("source") != "decode_gallica":
            continue
        decode_count += 1
        decode_id = record["id"].removeprefix("decode_")
        detail = details[decode_id]
        source = mapping[decode_id]
        ark = source["gallica_ark"].split("/")[-1]
        offset = offsets.get(source["volume"], 0)
        scan_index = int(source["folio"]) - offset
        display_date, earliest, latest = decode_date_bounds(detail)

        before = json.dumps(record, ensure_ascii=False, sort_keys=True)
        record["date_or_century"] = display_date
        if earliest is None:
            record.pop("date_earliest_year", None)
            record.pop("date_latest_year", None)
        else:
            record["date_earliest_year"] = earliest
            record["date_latest_year"] = latest
        record["image_provenance"] = image_provenance(
            ark, scan_index, offset, fetched_at=HISTORICAL_FETCH_DATE
        )
        record["context_layers"] = context_layers(record)
        after = json.dumps(record, ensure_ascii=False, sort_keys=True)
        changed += before != after

    if not check and changed:
        MANIFEST.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
        )
    return decode_count, changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="report records needing migration without writing"
    )
    args = parser.parse_args()
    total, changed = migrate(check=args.check)
    action = "would update" if args.check else "updated"
    print(f"DECODE/Gallica records: {total}; {action}: {changed}")


if __name__ == "__main__":
    main()
