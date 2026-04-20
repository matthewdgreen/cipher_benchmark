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
OFFSETS_FILE = BASE / "data_staging" / "gallica_folio_offsets.json"
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


def load_offsets():
    """Load per-volume folio-to-scan offsets. Volumes with a known offset are
    included in the pilot; volumes listed under 'unresolved' are skipped."""
    if not OFFSETS_FILE.exists():
        return {}, {}
    with open(OFFSETS_FILE) as f:
        data = json.load(f)
    offsets = {vol: info["offset"] for vol, info in data.get("offsets", {}).items()}
    unresolved = set(data.get("unresolved", {}).keys())
    return offsets, unresolved


def get_ok_volumes(offsets=None, unresolved=None):
    """Get the set of volumes usable for the pilot.

    A volume is usable if either:
      (a) folio numbers align with scan indices (max_folio <= scan_count, offset=0), or
      (b) it has a known per-volume offset in gallica_folio_offsets.json that keeps
          every DECODE folio within [1, scan_count] after applying the offset.

    Volumes listed in gallica_folio_offsets.json 'unresolved' are excluded.
    """
    offsets = offsets or {}
    unresolved = unresolved or set()

    with open(MAPPING) as f:
        records = json.load(f)["records"]
    with open(SCAN_COUNTS) as f:
        scan_counts = json.load(f)

    vol_folios = {}
    for r in records:
        vol_folios.setdefault(r["volume"], []).append(int(r["folio"]))

    ok = set()
    for vol, folios in vol_folios.items():
        if vol in unresolved:
            continue
        scans = scan_counts.get(vol)
        if not isinstance(scans, int):
            continue
        off = offsets.get(vol, 0)
        # After applying the offset, every DECODE folio must map into [1, scans].
        # We treat the special sentinel 99999 as "HEAD-verified to work at each
        # requested folio" — accept any folio.
        if scans == 99999:
            ok.add(vol)
            continue
        scan_indices = [f - off for f in folios]
        if all(1 <= s <= scans for s in scan_indices):
            ok.add(vol)
    return ok


def folio_to_scan(folio, vol, offsets):
    """Convert a DECODE folio number to the corresponding Gallica scan index
    by applying the per-volume offset (0 if none)."""
    return int(folio) - offsets.get(vol, 0)


def download_gallica_image(ark_id, scan_index, output_path, width=IMAGE_WIDTH):
    """Download a folio image from Gallica IIIF. scan_index is the
    Gallica-sequential index (already offset-adjusted)."""
    url = (
        f"https://gallica.bnf.fr/iiif/ark:/12148/{ark_id}"
        f"/f{scan_index}/full/{width},/0/native.jpg"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CipherBenchmark/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            output_path.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"    ERROR downloading scan f{scan_index}: {e}")
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

    offsets, unresolved = load_offsets()
    ok_volumes = get_ok_volumes(offsets=offsets, unresolved=unresolved)
    records = [r for r in all_records if r["volume"] in ok_volumes]
    print(f"OK volumes: {len(ok_volumes)} (of which {sum(1 for v in ok_volumes if v in offsets)} use a folio-offset)")
    if offsets:
        print(f"  offset volumes: {sorted(v for v in ok_volumes if v in offsets)}")
    if unresolved:
        skipped = [r for r in all_records if r["volume"] in unresolved]
        print(f"Unresolved volumes (skipped): {sorted(unresolved)} — {len(skipped)} record(s) held for review")
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

        # Convert DECODE folio to Gallica scan index via per-volume offset (0 if none).
        scan_index = folio_to_scan(folio, vol, offsets)
        vol_offset = offsets.get(vol, 0)

        # Build record ID
        record_id = f"decode_{decode_id}"

        # Download image (one folio for now; multi-page records get first folio).
        # Filename still uses the DECODE folio number for human-readability;
        # Gallica URL uses the computed scan index.
        img_path = BENCHMARK / "sources" / "decode_gallica" / "images" / f"{record_id}_f{folio}.jpg"
        if not img_path.exists():
            if vol_offset:
                print(f"  [{i+1}/{len(records)}] Downloading {record_id} f{folio} (Gallica scan {scan_index}, offset {vol_offset})...")
            else:
                print(f"  [{i+1}/{len(records)}] Downloading {record_id} f{folio}...")
            success = download_gallica_image(ark, scan_index, img_path)
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

        image_files = [f"sources/decode_gallica/images/{record_id}_f{folio}.jpg"]

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
                + (
                    f" Folio-to-scan offset {vol_offset} applied (scan index = folio − {vol_offset}); "
                    f"see data_staging/gallica_folio_offsets.json."
                    if vol_offset else ""
                )
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
