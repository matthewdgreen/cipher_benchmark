#!/usr/bin/env python3
"""
Export all 'Decrypted' cipher records from the DECODE database API.

Outputs a CSV file with full metadata for all records with status=1 (Decrypted)
and record_type=1 (Cipher).

API endpoint: https://de-crypt.org/decrypt-web/api/list/Records
No authentication required for read access.
"""

import csv
import json
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://de-crypt.org/decrypt-web/api"
OUTPUT_FILE = "data_staging/decode_decrypted_ciphers.csv"
DETAIL_OUTPUT = "data_staging/decode_decrypted_ciphers_detail.jsonl"

# Status 1 = Decrypted, record_type 1 = Cipher
LIST_URL = f"{API_BASE}/list/Records?cmd=resetall&x_status=1&x_record_type=1&recperpage=100&start={{}}"
VIEW_URL = f"{API_BASE}/view/Records/{{}}"


def fetch_json(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise


def fetch_list_page(start):
    url = LIST_URL.format(start)
    data = fetch_json(url)
    return data.get("records", []), data.get("totalRecordCount", 0)


def fetch_record_detail(record_id):
    url = VIEW_URL.format(record_id)
    return fetch_json(url)


def main():
    print("Fetching decrypted cipher records from DECODE API...")

    # Phase 1: Get all record IDs and basic info via list endpoint
    all_records = []
    start = 0
    total = None

    while True:
        records, total_count = fetch_list_page(start)
        if total is None:
            total = total_count
            print(f"Total decrypted cipher records: {total}")

        if not records:
            break

        all_records.extend(records)
        start += len(records)
        print(f"  Fetched {len(all_records)}/{total} records...")

        if len(all_records) >= total:
            break

        time.sleep(0.5)  # Be polite to the server

    print(f"\nPhase 1 complete: {len(all_records)} records from list API.")

    # Write basic CSV from list data
    if all_records:
        fields = list(all_records[0].keys())
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_records)
        print(f"Basic CSV written to {OUTPUT_FILE}")

    # Phase 2: Fetch detailed records (slower, be polite)
    print(f"\nPhase 2: Fetching detailed records...")
    detail_count = 0
    error_count = 0

    with open(DETAIL_OUTPUT, "w", encoding="utf-8") as f:
        for i, rec in enumerate(all_records):
            try:
                detail = fetch_record_detail(rec["id"])
                f.write(json.dumps(detail, ensure_ascii=False) + "\n")
                detail_count += 1
            except Exception as e:
                print(f"  Error fetching record {rec['id']}: {e}")
                error_count += 1

            if (i + 1) % 50 == 0:
                print(f"  Detailed: {i+1}/{len(all_records)} (errors: {error_count})")
                time.sleep(1)  # Rate limiting
            else:
                time.sleep(0.3)

    print(f"\nPhase 2 complete: {detail_count} detailed records, {error_count} errors.")
    print(f"Detail JSONL written to {DETAIL_OUTPUT}")

    # Summary stats
    print("\n=== Summary ===")
    langs = {}
    countries = {}
    for rec in all_records:
        lang = rec.get("c_lang", "unknown") or "unknown"
        langs[lang] = langs.get(lang, 0) + 1
        holder = rec.get("c_holder", "")
        if holder:
            # Extract archive/country from holder string
            country = holder.split(",")[0].strip() if "," in holder else holder[:50]
            countries[country] = countries.get(country, 0) + 1

    print(f"Total records: {len(all_records)}")
    print(f"\nLanguage distribution:")
    for lang, count in sorted(langs.items(), key=lambda x: -x[1])[:15]:
        print(f"  {lang}: {count}")
    print(f"\nTop archives/holders:")
    for country, count in sorted(countries.items(), key=lambda x: -x[1])[:15]:
        print(f"  {country}: {count}")


if __name__ == "__main__":
    main()
