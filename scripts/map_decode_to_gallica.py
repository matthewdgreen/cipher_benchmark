#!/usr/bin/env python3
"""
Map DECODE triage candidates (BnF records) to Gallica IIIF ARK identifiers.

Uses manually verified ARKs + Gallica IIIF manifest to resolve folio numbers
to downloadable image URLs.

Output: data_staging/decode_gallica_mapping.json
"""

import csv
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
CANDIDATES = BASE / "data_staging" / "decode_triage_candidates.csv"
OUTPUT = BASE / "data_staging" / "decode_gallica_mapping.json"
SAMPLE_DIR = BASE / "data_staging" / "gallica_samples"

# Manually verified Gallica ARK identifiers for BnF volumes.
# Mapped via Biblissima Wikibase API and Gallica catalog searches.
VOLUME_ARKS = {
    # Mélanges de Colbert (resolved via Biblissima Wikibase P197)
    "Mel101": "btv1b10035513z",
    "Mel108": "btv1b10035507b",
    "Mel109": "btv1b10035493w",
    "Mel120": "btv1b10035558v",
    "Mel127bis": "btv1b100355703",
    "Mel133": "btv1b100319205",
    "Mel134bis": "btv1b100356263",
    "Mel136": "btv1b10035629f",
    "Mel137": "btv1b10035630t",
    "Mel137bis": "btv1b100356318",
    "Mel138": "btv1b10035618k",
    "Mel140": "btv1b10035621v",
    "Mel142": "btv1b100356335",
    "Mel142bis": "btv1b100356246",
    "Mel144": "btv1b10035611f",
    "Mel149": "btv1b100340145",
    "Mel155": "btv1b100340323",
    "Mel157bis": "btv1b10035600k",
    "Mel158": "btv1b100356011",
    "Mel159": "btv1b10035602g",
    "Mel160": "btv1b10035566c",
    "Mel161": "btv1b10035567t",
    "Mel162": "btv1b100355688",
    "Mel163": "btv1b10035569q",
    "Mel164": "btv1b100350812",
    "Mel165": "btv1b10034950f",
    "Mel165bis": "btv1b10034951w",
    "Mel166": "btv1b10034952b",
    "Mel166bis": "btv1b10034953s",
    "Mel167": "btv1b100349547",
    "Mel171bis": "btv1b100340073",
    "Mel176bis": "btv1b100349653",
    # Collection Baluze
    "Baluze103": "btv1b9001389d",
    "Baluze155": "btv1b9001401d",
    "Baluze163": "btv1b9001517m",
    "Baluze167": "btv1b9001489r",
    "Baluze168": "btv1b9001503k",
    "Baluze169": "btv1b9001488b",
    "Baluze170": "btv1b90015040",
    "Baluze171": "btv1b90014126",
    "Baluze172": "btv1b9001505d",
    "Baluze178": "btv1b9001581s",
    "Baluze188": "btv1b90014586",
    "Baluze329": "btv1b90027915",
    "Baluze331": "btv1b10721731w",
    "Baluze332": "btv1b10721661r",
    "Baluze343": "btv1b9001465b",
    # Cinq cents de Colbert
    "500Colbert33": "btv1b10033958p",
    # Espagnol
    "es132": "btv1b10032556x",
    # Clairambault
    "Clair325": "btv1b90006916",
    "Clair328": "btv1b90007637",
    # Français — not found on Gallica; may not be digitized
    "fr6885": None,
    "fr20974": None,
}


def parse_record_name(name):
    """Parse BnF_Collection_fFolio from DECODE record name.

    Returns (volume_key, folio_str) or (None, None).
    """
    # Standard pattern: BnF_Mel136_f209 or BNF_es132_f17
    m = re.match(r'[Bb][Nn][Ff]_(\w+?)(\d+(?:bis)?)_f\.?(\d+)', name)
    if m:
        vol = m.group(1) + m.group(2)
        folio = m.group(3)
        return vol, folio

    # Page pattern: BnF_Mel160_p188
    m = re.match(r'[Bb][Nn][Ff]_(\w+?)(\d+(?:bis)?)_p(\d+)', name)
    if m:
        vol = m.group(1) + m.group(2)
        page = m.group(3)
        return vol, page

    # Compound folio: BNF_es132_f17&amp;f22 -> take first folio
    m = re.match(r'[Bb][Nn][Ff]_(\w+?)(\d+(?:bis)?)_f(\d+)', name)
    if m:
        vol = m.group(1) + m.group(2)
        folio = m.group(3)
        return vol, folio

    return None, None


def build_gallica_iiif_url(ark_id, folio_num, width=1200):
    """Build Gallica IIIF image URL for a specific folio."""
    return (
        f"https://gallica.bnf.fr/iiif/ark:/12148/{ark_id}"
        f"/f{folio_num}/full/{width},/0/native.jpg"
    )


def fetch_manifest_page_count(ark_id):
    """Fetch IIIF manifest to get total page count."""
    url = f"https://gallica.bnf.fr/iiif/ark:/12148/{ark_id}/manifest.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CipherBenchmark/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            canvases = data.get("sequences", [{}])[0].get("canvases", [])
            return len(canvases)
    except Exception as e:
        print(f"  Warning: Could not fetch manifest for {ark_id}: {e}")
        return None


def main():
    print("Loading triage candidates...")
    with open(CANDIDATES) as f:
        rows = list(csv.DictReader(f))

    bnf = [r for r in rows if "nationale de France" in r["holder"]]
    print(f"BnF candidates: {len(bnf)}")

    # Parse and map each record
    mapped = []
    unmapped = []
    no_ark = []

    for r in bnf:
        vol, folio = parse_record_name(r["name"])
        if vol is None:
            unmapped.append(r)
            continue

        ark = VOLUME_ARKS.get(vol)
        if ark is None:
            no_ark.append((r, vol, folio))
            continue

        iiif_url = build_gallica_iiif_url(ark, folio)
        mapped.append({
            "decode_id": r["id"],
            "name": r["name"],
            "language": r["language"],
            "pages": r["pages"],
            "volume": vol,
            "folio": folio,
            "gallica_ark": f"ark:/12148/{ark}",
            "gallica_url": f"https://gallica.bnf.fr/ark:/12148/{ark}",
            "iiif_image_url": iiif_url,
            "iiif_manifest_url": f"https://gallica.bnf.fr/iiif/ark:/12148/{ark}/manifest.json",
        })

    print(f"\nMapped to Gallica IIIF: {len(mapped)}")
    print(f"Name parse failures: {len(unmapped)}")
    print(f"No ARK available: {len(no_ark)}")

    if unmapped:
        print("\nUnmapped records:")
        for r in unmapped:
            print(f"  [{r['id']}] {r['name']}")

    if no_ark:
        from collections import Counter
        vols = Counter(v for _, v, _ in no_ark)
        print(f"\nVolumes without ARKs ({len(no_ark)} records):")
        for v, n in vols.most_common():
            print(f"  {v}: {n} records")

    # Group by volume for summary
    from collections import Counter
    vol_counts = Counter(m["volume"] for m in mapped)
    print(f"\nMapped volumes ({len(vol_counts)}):")
    for vol, n in vol_counts.most_common():
        ark = VOLUME_ARKS[vol]
        print(f"  {vol}: {n} records -> ark:/12148/{ark}")

    # Save mapping
    with open(OUTPUT, "w") as f:
        json.dump({
            "description": "Mapping from DECODE triage candidates to Gallica IIIF",
            "generated": "2026-04-15",
            "total_mapped": len(mapped),
            "total_unmapped": len(unmapped) + len(no_ark),
            "records": mapped,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nMapping saved to {OUTPUT}")

    # Download a few sample images to verify the IIIF URLs work
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    print("\nDownloading sample images to verify IIIF URLs...")

    # Pick one record from each of the top 3 volumes
    sampled_vols = set()
    samples = []
    for m in mapped:
        if m["volume"] not in sampled_vols and len(samples) < 5:
            samples.append(m)
            sampled_vols.add(m["volume"])

    for s in samples:
        fname = f"sample_{s['decode_id']}_{s['volume']}_f{s['folio']}.jpg"
        outpath = SAMPLE_DIR / fname
        if outpath.exists():
            print(f"  Already exists: {fname}")
            continue
        print(f"  Downloading {fname}...")
        url = s["iiif_image_url"]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CipherBenchmark/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                outpath.write_bytes(resp.read())
            size_kb = outpath.stat().st_size / 1024
            print(f"    OK ({size_kb:.0f} KB)")
            time.sleep(1)  # rate limit
        except Exception as e:
            print(f"    FAILED: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
