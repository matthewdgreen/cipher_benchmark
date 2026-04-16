#!/usr/bin/env python3
"""
Create Track A-only benchmark records from DECODE candidates via Gallica IIIF.

Downloads folio images from Gallica for DECODE triage candidates where the
Gallica scan index matches the manuscript folio number (confirmed-OK volumes).

These records support Track A (image→transcription) only until transcriptions
and plaintext become available from DECODE or manual transcription.
"""

import csv
import json
import os
import time
import urllib.request
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
BENCHMARK = BASE / "benchmark"
MAPPING = BASE / "data_staging" / "decode_gallica_mapping.json"
SCAN_COUNTS = BASE / "data_staging" / "gallica_scan_counts.json"
DETAIL_FILE = BASE / "data_staging" / "decode_decrypted_ciphers_detail.jsonl"

IMAGE_WIDTH = 1200


def load_decode_details():
    """Load DECODE detail records keyed by ID."""
    details = {}
    with open(DETAIL_FILE) as f:
        for line in f:
            rec = json.loads(line)["records"]
            details[rec["id"]] = rec
    return details


def get_ok_volumes():
    """Get set of volumes where folio number = scan index."""
    with open(MAPPING) as f:
        records = json.load(f)["records"]
    with open(SCAN_COUNTS) as f:
        scan_counts = json.load(f)

    vol_max_folio = {}
    for r in records:
        vol = r["volume"]
        folio = int(r["folio"])
        vol_max_folio[vol] = max(vol_max_folio.get(vol, 0), folio)

    ok = set()
    for vol, scans in scan_counts.items():
        if isinstance(scans, int) and vol_max_folio.get(vol, 9999) <= scans:
            ok.add(vol)
    return ok


def download_gallica_image(ark_id, folio_num, output_path, width=IMAGE_WIDTH):
    """Download a folio image from Gallica IIIF."""
    url = (
        f"https://gallica.bnf.fr/iiif/ark:/12148/{ark_id}"
        f"/f{folio_num}/full/{width},/0/native.jpg"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CipherBenchmark/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            output_path.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"    ERROR downloading f{folio_num}: {e}")
        if output_path.exists():
            output_path.unlink()
        return False


def decode_cipher_types(type_codes):
    """Map DECODE numeric cipher type codes to readable names."""
    TYPE_MAP = {
        "1": "simple_substitution",
        "2": "homophonic_substitution",
        "3": "polyalphabetic",
        "4": "transposition",
        "5": "nomenclator",
        "6": "code",
        "7": "other",
    }
    if not type_codes:
        return []
    codes = [c.strip() for c in str(type_codes).split(",") if c.strip()]
    return [TYPE_MAP.get(c, f"unknown_{c}") for c in codes]


def decode_symbol_sets(set_codes):
    """Map DECODE numeric symbol set codes to readable names."""
    SET_MAP = {
        "1": "alphabetic",
        "2": "numerical",
        "3": "symbolic",
        "4": "diacritical",
        "5": "mixed",
    }
    if not set_codes:
        return []
    codes = [c.strip() for c in str(set_codes).split(",") if c.strip()]
    return [SET_MAP.get(c, f"unknown_{c}") for c in codes]


def main():
    print("Loading data...")
    with open(MAPPING) as f:
        all_records = json.load(f)["records"]

    ok_volumes = get_ok_volumes()
    records = [r for r in all_records if r["volume"] in ok_volumes]
    print(f"OK volumes: {len(ok_volumes)}")
    print(f"Records to process: {len(records)}")

    details = load_decode_details()

    # Download images and create records
    print(f"\nDownloading images and creating records...")
    benchmark_records = []
    download_errors = []

    for i, r in enumerate(records):
        decode_id = r["decode_id"]
        vol = r["volume"]
        folio = r["folio"]
        ark = r["gallica_ark"].split("/")[-1]

        # Build record ID
        record_id = f"decode_{decode_id}"

        # Download image (one folio for now; multi-page records get first folio)
        img_path = BENCHMARK / "images" / f"{record_id}_f{folio}.jpg"
        if not img_path.exists():
            print(f"  [{i+1}/{len(records)}] Downloading {record_id} f{folio}...")
            success = download_gallica_image(ark, folio, img_path)
            if not success:
                download_errors.append(record_id)
            time.sleep(1.5)  # rate limit for Gallica
        else:
            print(f"  [{i+1}/{len(records)}] Already exists: {record_id}")

        # Get DECODE detail metadata
        detail = details.get(decode_id, {})
        cipher_types = decode_cipher_types(detail.get("cipher_types"))
        symbol_sets = decode_symbol_sets(detail.get("symbol_sets"))
        num_pages = int(detail.get("number_of_pages", 1) or 1)
        lang_code = {
            "French": "fr", "Spanish": "es", "Dutch": "nl",
            "Italian": "it", "Spanis": "es",
        }.get(r["language"], r["language"][:2].lower())
        date_str = detail.get("creation_date", "")
        # Extract year-ish from DECODE date field
        if date_str and len(date_str) >= 4:
            date_str = date_str[:10]  # "YYYY-MM-DD" or similar

        image_files = [f"images/{record_id}_f{folio}.jpg"]

        rec = {
            "id": record_id,
            "source": "decode_gallica",
            "source_record_id": f"DECODE_{decode_id}",
            "source_url": f"https://de-crypt.org/decrypt-web/RecordsView/{decode_id}",
            "task_tracks": ["image2transcription"],
            "rights_class": "open",  # Gallica: non-commercial reuse free with attribution
            "status": "solved_probable",  # DECODE says decrypted; we don't have plaintext yet
            "cipher_type": cipher_types or ["unknown"],
            "symbol_set": symbol_sets or ["unknown"],
            "plaintext_language": lang_code,
            "date_or_century": date_str,
            "page_count": 1,  # first folio only for now
            "provenance": detail.get("current_holder", "Bibliothèque nationale de France"),
            "solution_reference": "DECODE database (de-crypt.org). Cipher keys published by S. Tomokiyo, Cryptiana.",
            "image_files": image_files,
            "has_key": True,
            "manuscript_page": f"f{folio}",
            "curation_notes": (
                f"DECODE record {decode_id}: {r['name']}. "
                f"Volume {vol} ({num_pages} pages in DECODE record). "
                f"Track A only — transcription and plaintext pending DECODE access. "
                f"Image from Gallica IIIF. Source: gallica.bnf.fr / BnF."
            ),
        }
        benchmark_records.append(rec)

    print(f"\nCreated {len(benchmark_records)} records")
    if download_errors:
        print(f"Download errors: {len(download_errors)}: {download_errors[:10]}")

    # Append to manifest
    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    existing = []
    if manifest_path.exists():
        with open(manifest_path) as f:
            for line in f:
                rec = json.loads(line)
                if rec["source"] != "decode_gallica":
                    existing.append(rec)

    all_recs = existing + benchmark_records
    with open(manifest_path, "w", encoding="utf-8") as f:
        for rec in all_recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Manifest updated: {len(existing)} existing + {len(benchmark_records)} new = {len(all_recs)} total")

    # Validate
    print("\nValidating...")
    schema_path = BENCHMARK / "manifest" / "schema.json"
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        errors = 0
        for rec in benchmark_records:
            try:
                jsonschema.validate(rec, schema)
            except jsonschema.ValidationError as e:
                print(f"  INVALID: {rec['id']}: {e.message}")
                errors += 1
        if errors == 0:
            print(f"  All {len(benchmark_records)} records valid")
    except ImportError:
        print("  jsonschema not installed, skipping")

    print(f"\n=== DECODE/Gallica Track A Pilot ===")
    print(f"Records: {len(benchmark_records)}")
    print(f"Volumes: {len(ok_volumes)}")
    print(f"Track: A (image2transcription) only")
    print(f"Rights: open (Gallica non-commercial reuse with attribution)")
    print(f"Download errors: {len(download_errors)}")


if __name__ == "__main__":
    main()
