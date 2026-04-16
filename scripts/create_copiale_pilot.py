#!/usr/bin/env python3
"""
Create 10 pilot benchmark records from the Copiale cipher.

Parses the transcription and deciphered files into per-page segments,
selects 10 diverse pages, and outputs benchmark-format files.

Pilot pages chosen for diversity:
- Pages 1, 10, 20, 30, 45, 50, 65, 80, 95, 105
- Spread across the manuscript (early, middle, late)
- All present in both transcription and deciphered files
"""

import json
import os
import re
import shutil
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
COPIALE_DIR = BASE / "data_staging" / "copiale"
BENCHMARK = BASE / "benchmark"
IMAGE_OFFSET = 5  # image page_NNN = manuscript page NNN-5

PILOT_PAGES = [1, 10, 20, 30, 45, 50, 65, 80, 95, 105]


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
                # Skip header comment lines
                if line.startswith("##="):
                    continue
                current_lines.append(line.rstrip())

    if current_page is not None:
        pages[current_page] = "\n".join(current_lines).strip()

    return pages


def extract_symbol_inventory(transcription_text):
    """Extract unique symbols from a diplomatic transcription page."""
    # Remove page markers and comments
    lines = [l for l in transcription_text.split("\n")
             if l.strip() and not l.startswith("##") and not l.startswith("#")]
    text = " ".join(lines)
    # Tokens are space-separated
    tokens = text.split()
    # Filter out catch-word markers and punctuation-only tokens
    symbols = set()
    for t in tokens:
        t = t.strip()
        if t and t != "#":
            symbols.add(t)
    return sorted(symbols)


def diplomatic_to_canonical(transcription_text):
    """
    Convert diplomatic transcription to canonical token form.

    The Copiale transcription uses ASCII mnemonics for cipher symbols.
    For the canonical form, we remap each unique token to S### format.

    Returns (canonical_text, symbol_map).
    """
    # Build a deterministic mapping from diplomatic tokens to canonical IDs
    lines = [l for l in transcription_text.split("\n")
             if l.strip() and not l.startswith("##") and not l.startswith("#")]

    # Collect all unique tokens across this page in order of first appearance
    seen = {}
    counter = 1
    for line in lines:
        for token in line.split():
            token = token.strip()
            if token and token != "#" and token not in seen:
                seen[token] = f"S{counter:03d}"
                counter += 1

    # Convert each line
    canonical_lines = []
    for line in lines:
        tokens = line.split()
        canonical_tokens = []
        for t in tokens:
            t = t.strip()
            if t == "#":
                continue
            if t in seen:
                canonical_tokens.append(seen[t])
            else:
                canonical_tokens.append(t)
        if canonical_tokens:
            canonical_lines.append(" ".join(canonical_tokens))

    return "\n".join(canonical_lines), seen


def main():
    print("Parsing Copiale files...")

    # Parse transcription (page markers: "## PAGE N" at start of line)
    trans_pages = parse_pages(
        COPIALE_DIR / "copiale-transcription.txt",
        re.compile(r"^## PAGE (\d+)", re.MULTILINE)
    )
    print(f"  Transcription: {len(trans_pages)} pages parsed")

    # Parse deciphered text (page markers: " ## PAGE N " with leading space)
    deci_pages = parse_pages(
        COPIALE_DIR / "copiale-deciphered.txt",
        re.compile(r"## PAGE (\d+)")
    )
    print(f"  Deciphered: {len(deci_pages)} pages parsed")

    # Parse translation (ISO-8859-1 encoded with CRLF)
    transl_pages = parse_pages(
        COPIALE_DIR / "copiale-translation.txt",
        re.compile(r"## PAGE (\d+)"),
        encoding="iso-8859-1"
    )
    print(f"  Translation: {len(transl_pages)} pages parsed")

    # Check pilot page availability
    print(f"\nPilot pages: {PILOT_PAGES}")
    for p in PILOT_PAGES:
        has_trans = p in trans_pages
        has_deci = p in deci_pages
        has_transl = p in transl_pages
        img_page = p + IMAGE_OFFSET
        img_path = COPIALE_DIR / "individual_pages" / f"page_{img_page:03d}.png"
        has_img = img_path.exists()
        status = "OK" if (has_trans and has_deci and has_img) else "MISSING"
        print(f"  Page {p:3d}: trans={has_trans} deci={has_deci} transl={has_transl} img={has_img} -> {status}")

    # Build a global symbol map across ALL pages for consistency
    print("\nBuilding global symbol inventory...")
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
    print(f"  {len(all_tokens)} unique symbols across all pages")

    # Create benchmark records
    print("\nCreating pilot benchmark records...")
    records = []

    for page_num in PILOT_PAGES:
        if page_num not in trans_pages or page_num not in deci_pages:
            print(f"  SKIPPING page {page_num} (missing data)")
            continue

        record_id = f"copiale_p{page_num:03d}"
        img_page = page_num + IMAGE_OFFSET

        # Write diplomatic transcription
        diplo_path = BENCHMARK / "sources" / "copiale" / "transcriptions" / f"{record_id}.diplomatic.txt"
        diplo_text = trans_pages[page_num]
        diplo_path.write_text(diplo_text, encoding="utf-8")

        # Write canonical transcription (using global symbol map)
        canon_lines = []
        for line in diplo_text.split("\n"):
            if not line.strip() or line.startswith("##") or line.startswith("#"):
                continue
            tokens = []
            for t in line.split():
                t = t.strip()
                if t == "#":
                    continue
                if t in all_tokens:
                    tokens.append(all_tokens[t])
                else:
                    tokens.append(t)
            if tokens:
                canon_lines.append(" ".join(tokens))
        canon_text = "\n".join(canon_lines)
        canon_path = BENCHMARK / "sources" / "copiale" / "transcriptions" / f"{record_id}.canonical.txt"
        canon_path.write_text(canon_text, encoding="utf-8")

        # Write plaintext (deciphered German)
        plain_path = BENCHMARK / "sources" / "copiale" / "plaintext" / f"{record_id}.txt"
        plain_path.write_text(deci_pages[page_num], encoding="utf-8")

        # Copy image
        src_img = COPIALE_DIR / "individual_pages" / f"page_{img_page:03d}.png"
        dst_img = BENCHMARK / "sources" / "copiale" / "images" / f"{record_id}.png"
        if src_img.exists():
            shutil.copy2(src_img, dst_img)
        else:
            print(f"  WARNING: image not found for page {page_num}")

        # Count symbols on this page
        page_symbols = set()
        for line in diplo_text.split("\n"):
            if not line.strip() or line.startswith("##") or line.startswith("#"):
                continue
            for t in line.split():
                t = t.strip()
                if t and t != "#":
                    page_symbols.add(t)

        # Build record
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
            "image_files": [f"sources/copiale/images/{record_id}.png"],
            "transcription_diplomatic_file": f"sources/copiale/transcriptions/{record_id}.diplomatic.txt",
            "transcription_canonical_file": f"sources/copiale/transcriptions/{record_id}.canonical.txt",
            "plaintext_file": f"sources/copiale/plaintext/{record_id}.txt",
            "has_key": True,
            "has_inline_plaintext": False,
            "manuscript_page": page_num,
            "curation_notes": f"Pilot record. Page {page_num} of 105. Diplomatic transcription uses ASCII symbol mnemonics from Knight/Megyesi/Schaefer. Canonical form uses global symbol map (S001-S{len(all_tokens):03d})."
        }
        records.append(record)
        print(f"  Created {record_id}")

    # Write manifest
    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nManifest written: {manifest_path} ({len(records)} records)")

    # Write global symbol map
    symmap_path = BENCHMARK / "sources" / "copiale" / "metadata" / "copiale_symbol_map.json"
    with open(symmap_path, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Mapping from Copiale diplomatic transcription tokens to canonical S### identifiers",
            "source": "Knight/Megyesi/Schaefer 2011 transcription",
            "total_symbols": len(all_tokens),
            "mapping": all_tokens
        }, f, indent=2, ensure_ascii=False)
    print(f"Symbol map written: {symmap_path} ({len(all_tokens)} symbols)")

    # Summary
    print(f"\n=== Pilot Summary ===")
    print(f"Records created: {len(records)}")
    print(f"Global symbol inventory: {len(all_tokens)} unique tokens")
    print(f"Files per record: image (.png) + diplomatic (.txt) + canonical (.txt) + plaintext (.txt)")
    print(f"All records marked rights_class='linked_only' pending image rights clarification")


if __name__ == "__main__":
    main()
