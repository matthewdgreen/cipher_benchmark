#!/usr/bin/env python3
"""
Fetch Beale Papers page images from Wikimedia Commons.

Source: File:Beale_Papers.djvu on Wikimedia Commons
  https://commons.wikimedia.org/wiki/File:Beale_Papers.djvu

The 1885 pamphlet is public domain in the US (published before 1931).
Images are freely redistributable with attribution to Wikimedia Commons.

Page map (confirmed by visual inspection, 2026-05):
  p.20  Cipher 2 "No. 2" — solved via Declaration of Independence; NOT
          an unsolved target (Beale 2 is intentionally excluded from
          the unsolved benchmark as it has a traditional accepted solution)
  p.21  Cipher 1 "The Locality of the Vault" → beale_1 image
  p.22  Cipher 3 "Names and Residences"      → beale_3 image

Run this script once from the repo root to download the two images and
update the unsolved manifest records (beale_1, beale_3) with image_files
and image2transcription track support.
"""

import json
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = REPO_ROOT / "benchmark/unsolved/sources/famous_short/images"
MANIFEST = REPO_ROOT / "benchmark/unsolved/manifest/records.jsonl"
SCHEMA_PATH = REPO_ROOT / "benchmark/unsolved/manifest/schema.json"

# Confirmed URL template (hash 8/82 verified 2026-05)
WIKIMEDIA_TMPL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/"
    "Beale_Papers.djvu/page{n}-{w}px-Beale_Papers.djvu.jpg"
)
WIDTH = 960    # Wikimedia Commons allowed thumbnail step; confirmed working

PAGE_MAP = {
    "beale_1": {
        "page": 21,
        "label": "Cipher 1 — The Locality of the Vault",
        "manuscript_page_label": "p.21 (pamphlet)",
    },
    "beale_3": {
        "page": 22,
        "label": "Cipher 3 — Names and Residences",
        "manuscript_page_label": "p.22 (pamphlet)",
    },
}


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(
        url, headers={"User-Agent": "CipherBenchmark/1.0 (academic benchmark intake)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"  ERROR {dest.name}: {e}")
        if dest.exists():
            dest.unlink()
        return False


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Download images
    downloaded: dict[str, str] = {}
    for record_id, info in PAGE_MAP.items():
        n = info["page"]
        url = WIKIMEDIA_TMPL.format(n=n, w=WIDTH)
        dest = IMG_DIR / f"{record_id}_pamphlet_p{n}.jpg"
        if dest.exists():
            print(f"  already exists: {dest.name}")
        else:
            print(f"  downloading {record_id} (p.{n}) …")
            if not download(url, dest):
                continue
            time.sleep(1.0)
        downloaded[record_id] = f"sources/famous_short/images/{dest.name}"
        print(f"    → {downloaded[record_id]}")

    if not downloaded:
        print("No images downloaded; manifest unchanged.")
        return

    # Update manifest records
    records = [json.loads(l) for l in MANIFEST.open() if l.strip()]
    changed = 0
    for rec in records:
        rid = rec.get("id")
        if rid not in downloaded:
            continue
        img_rel = downloaded[rid]
        info = PAGE_MAP[rid]

        # Add image_files if not present or empty
        if not rec.get("image_files"):
            rec["image_files"] = [img_rel]
        elif img_rel not in rec["image_files"]:
            rec["image_files"].append(img_rel)

        # Add image2transcription track if not present
        if "image2transcription" not in rec.get("task_tracks", []):
            rec.setdefault("task_tracks", []).append("image2transcription")

        # Add image_provenance
        rec["image_provenance"] = {
            "source": "Wikimedia Commons — File:Beale_Papers.djvu",
            "source_url": "https://commons.wikimedia.org/wiki/File:Beale_Papers.djvu",
            "page": info["page"],
            "label": info["label"],
            "request_url_template": WIKIMEDIA_TMPL,
            "requested_width": WIDTH,
            "fetched_at": "2026-05",
            "rights": "public domain (US, published 1885)",
        }

        # Note: Track A for typeset printed text is essentially trivial OCR.
        # We include image2transcription for provenance verification and
        # visual context, not as a meaningful HTR challenge.  The curation_notes
        # field records this.
        note_tag = (
            "Image from Wikimedia Commons (File:Beale_Papers.djvu, "
            f"{info['label']}, page {info['page']}). "
            "Source is typeset printed text (1885 pamphlet), so "
            "image2transcription is trivially solvable by OCR — included "
            "for provenance verification and Track D visual context only."
        )
        existing_notes = rec.get("curation_notes", "")
        if "Wikimedia Commons" not in existing_notes:
            rec["curation_notes"] = (existing_notes + "  " + note_tag).strip()

        changed += 1
        print(f"  updated record: {rid}")

    with MANIFEST.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nManifest updated: {changed} record(s) modified.")

    # Validate
    try:
        import jsonschema
        schema = json.loads(SCHEMA_PATH.read_text())
        errors = 0
        for rec in records:
            if rec.get("id") in downloaded:
                try:
                    jsonschema.validate(rec, schema)
                except jsonschema.ValidationError as e:
                    print(f"  INVALID {rec['id']}: {e.message}")
                    errors += 1
        if errors == 0:
            print(f"Validation: updated records pass unsolved schema.")
    except ImportError:
        print("jsonschema not installed; skipping validation.")


if __name__ == "__main__":
    main()
