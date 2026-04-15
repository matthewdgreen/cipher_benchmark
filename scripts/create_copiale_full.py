#!/usr/bin/env python3
"""
Create benchmark records for ALL usable Copiale cipher pages.

Expands the pilot (10 pages) to the full set (~98 pages) where we have
aligned image + transcription + deciphered plaintext.

Known missing pages (from PAGE_MAPPING.md):
- Missing from BOTH transcription and deciphered: 19, 33, 46, 100
- Missing from transcription only: 32, 55, 92
"""

import json
import os
import re
import shutil
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
COPIALE_DIR = BASE / "data_staging" / "copiale"
BENCHMARK = BASE / "benchmark"
IMAGE_OFFSET = 5  # image page_NNN = manuscript page NNN + 5


def parse_pages(filepath, page_marker_re, encoding="utf-8"):
    """Parse a page-delimited file into {page_num: text} dict."""
    pages = {}
    current_page = None
    current_lines = []

    with open(filepath, "r", encoding=encoding) as f:
        for line in f:
            match = page_marker_re.search(line)
            if match:
                if current_page is not None:
                    pages[current_page] = "\n".join(current_lines).strip()
                current_page = int(match.group(1))
                current_lines = []
            elif current_page is not None:
                if line.startswith("##="):
                    continue
                current_lines.append(line.rstrip())

    if current_page is not None:
        pages[current_page] = "\n".join(current_lines).strip()

    return pages


def build_global_symbol_map(trans_pages):
    """Build a global symbol map across ALL pages, ordered by first appearance."""
    all_tokens = {}
    token_counter = 1
    for page_num in sorted(trans_pages.keys()):
        text = trans_pages[page_num]
        lines = [l for l in text.split("\n")
                 if l.strip() and not l.startswith("##") and not l.startswith("#")]
        for line in lines:
            for token in line.split():
                token = token.strip()
                if token and token != "#" and token not in all_tokens:
                    all_tokens[token] = f"S{token_counter:03d}"
                    token_counter += 1
    return all_tokens


def diplomatic_to_canonical(diplo_text, symbol_map):
    """Convert diplomatic transcription to canonical form using a global symbol map."""
    canon_lines = []
    unknown_tokens = set()
    for line in diplo_text.split("\n"):
        if not line.strip() or line.startswith("##") or line.startswith("#"):
            continue
        tokens = []
        for t in line.split():
            t = t.strip()
            if t == "#":
                continue
            if t in symbol_map:
                tokens.append(symbol_map[t])
            else:
                tokens.append(f"UNKNOWN_{t}")
                unknown_tokens.add(t)
        if tokens:
            canon_lines.append(" ".join(tokens))
    return "\n".join(canon_lines), unknown_tokens


def main():
    print("Parsing Copiale files...")

    trans_pages = parse_pages(
        COPIALE_DIR / "copiale-transcription.txt",
        re.compile(r"^## PAGE (\d+)", re.MULTILINE)
    )
    print(f"  Transcription: {len(trans_pages)} pages")

    deci_pages = parse_pages(
        COPIALE_DIR / "copiale-deciphered.txt",
        re.compile(r"## PAGE (\d+)")
    )
    print(f"  Deciphered: {len(deci_pages)} pages")

    # Build global symbol map
    print("\nBuilding global symbol map...")
    symbol_map = build_global_symbol_map(trans_pages)
    print(f"  {len(symbol_map)} unique symbols")

    # Find all usable pages (have transcription + deciphered + image)
    usable_pages = []
    skipped = {"no_trans": [], "no_deci": [], "no_image": []}

    for page_num in range(1, 106):
        has_trans = page_num in trans_pages
        has_deci = page_num in deci_pages
        img_page = page_num + IMAGE_OFFSET
        img_path = COPIALE_DIR / "individual_pages" / f"page_{img_page:03d}.png"
        has_img = img_path.exists()

        if not has_trans:
            skipped["no_trans"].append(page_num)
        if not has_deci:
            skipped["no_deci"].append(page_num)
        if not has_img:
            skipped["no_image"].append(page_num)

        if has_trans and has_deci and has_img:
            usable_pages.append(page_num)

    print(f"\nUsable pages: {len(usable_pages)}")
    print(f"Skipped — no transcription: {skipped['no_trans']}")
    print(f"Skipped — no deciphered:    {skipped['no_deci']}")
    print(f"Skipped — no image:         {skipped['no_image']}")

    # Create benchmark records
    print(f"\nCreating {len(usable_pages)} benchmark records...")
    records = []
    all_unknown = set()

    for page_num in usable_pages:
        record_id = f"copiale_p{page_num:03d}"
        img_page = page_num + IMAGE_OFFSET
        diplo_text = trans_pages[page_num]

        # Diplomatic transcription
        diplo_path = BENCHMARK / "transcriptions" / f"{record_id}.diplomatic.txt"
        diplo_path.write_text(diplo_text, encoding="utf-8")

        # Canonical transcription
        canon_text, unknown = diplomatic_to_canonical(diplo_text, symbol_map)
        all_unknown.update(unknown)
        canon_path = BENCHMARK / "transcriptions" / f"{record_id}.canonical.txt"
        canon_path.write_text(canon_text, encoding="utf-8")

        # Plaintext
        plain_path = BENCHMARK / "plaintext" / f"{record_id}.txt"
        plain_path.write_text(deci_pages[page_num], encoding="utf-8")

        # Image
        src_img = COPIALE_DIR / "individual_pages" / f"page_{img_page:03d}.png"
        dst_img = BENCHMARK / "images" / f"{record_id}.png"
        shutil.copy2(src_img, dst_img)

        # Count symbols on this page
        page_symbols = set()
        for line in diplo_text.split("\n"):
            if not line.strip() or line.startswith("##") or line.startswith("#"):
                continue
            for t in line.split():
                t = t.strip()
                if t and t != "#":
                    page_symbols.add(t)

        record = {
            "id": record_id,
            "source": "copiale",
            "source_record_id": f"copiale_manuscript_page_{page_num}",
            "source_url": "https://www.su.se/english/research/research-catalogue/research-projects/d/decipherment-of-historical-manuscripts/the-copiale-cipher",
            "task_tracks": ["image2transcription", "transcription2plaintext", "image2plaintext"],
            "rights_class": "linked_only",
            "status": "solved_verified",
            "cipher_type": ["homophonic_substitution", "nomenclator"],
            "symbol_set": ["alphabetic", "diacritical", "logographic"],
            "symbol_count": len(page_symbols),
            "plaintext_language": "de",
            "date_or_century": "mid-18th century",
            "page_count": 1,
            "provenance": "Private collection; scans hosted by Stockholm University",
            "solution_reference": "Knight, Megyesi, Schaefer (2011). 'The Copiale Cipher.' ACL Workshop. https://aclanthology.org/W11-1202/",
            "image_files": [f"images/{record_id}.png"],
            "transcription_diplomatic_file": f"transcriptions/{record_id}.diplomatic.txt",
            "transcription_canonical_file": f"transcriptions/{record_id}.canonical.txt",
            "plaintext_file": f"plaintext/{record_id}.txt",
            "has_key": True,
            "has_inline_plaintext": False,
            "manuscript_page": page_num,
            "curation_notes": f"Page {page_num} of 105. Diplomatic transcription uses ASCII symbol mnemonics from Knight/Megyesi/Schaefer (2011). Canonical form uses global symbol map (S001-S{len(symbol_map):03d})."
        }
        records.append(record)

    print(f"  Created {len(records)} records")

    if all_unknown:
        print(f"\n  WARNING: Unknown tokens not in symbol map: {all_unknown}")

    # Write manifest
    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nManifest written: {manifest_path} ({len(records)} records)")

    # Write global symbol map with logogram glossary
    symmap_path = BENCHMARK / "metadata" / "copiale_symbol_map.json"
    logogram_glossary = {
        "nee": "master",
        "tri": "lodge",
        "lip": "oculist (eye)",
        "star": "secret",
        "bigx": "freemason",
        "sci": "God",
        "toe": "power"
    }
    with open(symmap_path, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Mapping from Copiale diplomatic transcription tokens to canonical S### identifiers",
            "source": "Knight/Megyesi/Schaefer 2011 transcription",
            "cipher_system": "copiale",
            "total_symbols": len(symbol_map),
            "mapping": symbol_map,
            "logogram_glossary": logogram_glossary,
            "notes": "Tokens assigned in order of first appearance across all 105 manuscript pages. ASCII mnemonics (e.g., 'grr', 'bar', 'nee') represent handwritten cipher glyphs."
        }, f, indent=2, ensure_ascii=False)
    print(f"Symbol map written: {symmap_path} ({len(symbol_map)} symbols)")

    # Validate against schema
    print("\nValidating records against schema...")
    schema_path = BENCHMARK / "manifest" / "schema.json"
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        errors = 0
        for rec in records:
            try:
                jsonschema.validate(rec, schema)
            except jsonschema.ValidationError as e:
                print(f"  INVALID: {rec['id']}: {e.message}")
                errors += 1
        if errors == 0:
            print(f"  All {len(records)} records valid")
        else:
            print(f"  {errors} validation errors")
    except ImportError:
        print("  jsonschema not installed, skipping validation")

    # Summary
    symbol_counts = [r["symbol_count"] for r in records]
    print(f"\n=== Copiale Benchmark Summary ===")
    print(f"Total records:       {len(records)}")
    print(f"Global symbol count: {len(symbol_map)}")
    print(f"Per-page symbols:    min={min(symbol_counts)}, max={max(symbol_counts)}, avg={sum(symbol_counts)/len(symbol_counts):.0f}")
    print(f"Skipped pages:       {105 - len(records)}")
    print(f"Files generated:     {len(records)} images + {len(records)*2} transcriptions + {len(records)} plaintexts")
    print(f"Rights class:        linked_only (pending clarification from Megyesi)")


if __name__ == "__main__":
    main()
