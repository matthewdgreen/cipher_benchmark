#!/usr/bin/env python3
"""
Voynich Manuscript (Beinecke MS 408) intake for the unsolved-benchmark area.

Steps:
  1. Fetch the Beinecke IIIF manifest for MS 408.
  2. Parse canvases → (folio label, image service URL).
  3. Download one JPEG per folio at IMAGE_WIDTH.
  4. Emit one record per folio into benchmark/unsolved/manifest/records.jsonl
     (preserving any existing non-voynich records in the file).

Run with --dry-run to produce the records without downloading images.
Run with --limit N to fetch only the first N folios (sanity check).
"""

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
UNSOLVED = BASE / "benchmark" / "unsolved"
OUT_IMAGES = UNSOLVED / "sources" / "voynich" / "images"
OUT_METADATA = UNSOLVED / "sources" / "voynich" / "metadata"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
SCHEMA_PATH = UNSOLVED / "manifest" / "schema.json"
RECORDS_PATH = UNSOLVED / "manifest" / "records.jsonl"

IMAGE_WIDTH = 2000
USER_AGENT = "CipherBenchmark/1.0 (academic benchmark intake)"
RATE_LIMIT_SEC = 1.0


def http_get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read() if binary else resp.read().decode("utf-8")


def fetch_manifest():
    print(f"Fetching IIIF manifest: {MANIFEST_URL}")
    raw = http_get(MANIFEST_URL)
    return json.loads(raw)


def extract_folios(manifest):
    """Return list of (label, image_service_base) in manifest order.

    Handles both IIIF Presentation v2 (sequences[].canvases[]) and v3
    (items[]) shapes."""
    folios = []
    # v2
    for seq in manifest.get("sequences", []) or []:
        for canvas in seq.get("canvases", []) or []:
            label = canvas.get("label", "")
            label = label if isinstance(label, str) else json.dumps(label)
            for image in canvas.get("images", []) or []:
                resource = image.get("resource", {})
                service = resource.get("service", {})
                svc_id = service.get("@id") or service.get("id")
                if svc_id:
                    folios.append((label, svc_id))
                    break
    # v3 fallback
    if not folios:
        for canvas in manifest.get("items", []) or []:
            label_obj = canvas.get("label", {})
            if isinstance(label_obj, dict):
                label = " ".join(v[0] if v else "" for v in label_obj.values())
            else:
                label = str(label_obj)
            for ap in canvas.get("items", []) or []:
                for annot in ap.get("items", []) or []:
                    body = annot.get("body", {}) or {}
                    services = body.get("service", []) or []
                    if isinstance(services, dict):
                        services = [services]
                    for svc in services:
                        svc_id = svc.get("@id") or svc.get("id")
                        if svc_id:
                            folios.append((label, svc_id))
                            break
                    if folios and folios[-1][0] == label:
                        break
    return folios


_FOLIO_RE = re.compile(r"\bf?\s*0*(\d{1,3})\s*([rv])\s*(\d)?\b", re.IGNORECASE)


def normalize_folio_id(label):
    """Best-effort Beinecke-style folio ID from a manifest label.

    Returns (folio_id, is_folio_page). Non-folio items (covers, flyleaves)
    come back with a slugged id and is_folio_page=False so the caller can
    decide whether to skip them as benchmark records."""
    m = _FOLIO_RE.search(label or "")
    if m:
        n, side, sub = m.group(1), m.group(2).lower(), m.group(3)
        fid = f"f{int(n)}{side}" + (str(sub) if sub else "")
        return fid, True
    slug = re.sub(r"[^a-z0-9]+", "_", (label or "page").lower()).strip("_")
    return slug or "page", False


def download_image(service_base, dest, width=IMAGE_WIDTH):
    url = service_base.rstrip("/") + f"/full/{width},/0/default.jpg"
    try:
        data = http_get(url, binary=True)
        dest.write_bytes(data)
        return True, url
    except Exception as e:
        print(f"    ERROR {dest.name}: {e}")
        return False, url


def build_record(folio_id, label, image_rel_path, image_url, idx):
    return {
        "id": f"voynich_{folio_id}",
        "source": "voynich",
        "source_record_id": f"Beinecke_MS408_{folio_id}",
        "source_url": "https://collections.library.yale.edu/catalog/2002046",
        "task_tracks": [
            "image2transcription",
            "image2hypothesis",
        ],
        "rights_class": "open",
        "status": "unsolved",
        "partial_solution_evidence": "none",
        "cipher_type": ["unknown"],
        "symbol_set": ["symbolic"],
        "plaintext_language": "",
        "date_or_century": "early_15c",
        "page_count": 1,
        "provenance": "Beinecke Rare Book and Manuscript Library, Yale University, MS 408",
        "image_files": [image_rel_path],
        "manuscript_page": folio_id,
        "notable_attempts": [
            "Cheshire 2019 (proto-Romance) — widely rejected",
            "Gibbs 2017 (Latin abbreviation shorthand) — widely rejected",
            "Rugg 2004 (hoax/grille) — structural hypothesis, not a decipherment"
        ],
        "curation_notes": (
            f"Voynich folio {folio_id} (manifest label: {label!r}, order {idx}). "
            f"Image from Beinecke IIIF at width {IMAGE_WIDTH}. "
            f"IIIF request: {image_url}"
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Parse manifest and emit records but do not download images")
    ap.add_argument("--limit", type=int, default=None,
                    help="Only process the first N folio canvases")
    args = ap.parse_args()

    manifest = fetch_manifest()
    folios = extract_folios(manifest)
    print(f"Manifest canvases: {len(folios)}")

    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    OUT_METADATA.mkdir(parents=True, exist_ok=True)

    records = []
    errors = []
    skipped_nonfolio = 0

    for idx, (label, svc) in enumerate(folios):
        if args.limit is not None and len(records) >= args.limit:
            break
        folio_id, is_folio = normalize_folio_id(label)
        if not is_folio:
            skipped_nonfolio += 1
            continue
        img_name = f"voynich_{folio_id}.jpg"
        img_path = OUT_IMAGES / img_name
        image_url = svc.rstrip("/") + f"/full/{IMAGE_WIDTH},/0/default.jpg"

        if args.dry_run:
            print(f"  [{idx+1}] would download {folio_id}: {image_url}")
        else:
            if img_path.exists():
                print(f"  [{idx+1}] exists: {folio_id}")
            else:
                print(f"  [{idx+1}] downloading {folio_id}...")
                ok, image_url = download_image(svc, img_path)
                if not ok:
                    errors.append(folio_id)
                    continue
                time.sleep(RATE_LIMIT_SEC)

        rel = f"sources/voynich/images/{img_name}"
        records.append(build_record(folio_id, label, rel, image_url, idx))

    # Save canvas map as metadata (useful for anyone reconciling folio order).
    (OUT_METADATA / "voynich_canvas_map.json").write_text(
        json.dumps(
            {
                "_source": MANIFEST_URL,
                "_fetched": time.strftime("%Y-%m-%d"),
                "canvas_count": len(folios),
                "canvases": [{"label": l, "service": s} for l, s in folios],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    # Merge with existing records.jsonl, preserving non-voynich entries.
    existing = []
    if RECORDS_PATH.exists():
        with open(RECORDS_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("source") != "voynich":
                    existing.append(rec)

    all_recs = existing + records
    RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RECORDS_PATH, "w", encoding="utf-8") as f:
        for rec in all_recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print()
    print(f"Voynich records produced: {len(records)}")
    print(f"Skipped non-folio canvases: {skipped_nonfolio}")
    print(f"Download errors: {len(errors)}")
    print(f"records.jsonl: {len(existing)} existing + {len(records)} voynich = {len(all_recs)} total")

    # Validate if jsonschema available.
    try:
        import jsonschema
        schema = json.loads(SCHEMA_PATH.read_text())
        bad = 0
        for rec in records:
            try:
                jsonschema.validate(rec, schema)
            except jsonschema.ValidationError as e:
                print(f"  INVALID {rec['id']}: {e.message}")
                bad += 1
        if bad == 0:
            print(f"Validation: all {len(records)} records valid against unsolved schema")
    except ImportError:
        print("jsonschema not installed; skipping validation")


if __name__ == "__main__":
    main()
