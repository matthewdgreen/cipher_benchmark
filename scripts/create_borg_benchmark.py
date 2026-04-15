#!/usr/bin/env python3
"""
Create benchmark records for the Borg cipher (MSS Borg.lat.898).

408-page 17th-century Latin medical/pharmaceutical text encrypted with
a 34-symbol monoalphabetic substitution cipher.

Data sources:
- Transcription: Stockholm University (Knight/Aldarrab/Megyesi)
- Plaintext: Corrected Latin + English translation by Urban Örneholm
- Images: Vatican Library IIIF (digi.vatlib.it)

Only pages with all three layers (image + transcription + plaintext) are included.
"""

import json
import os
import re
import time
import urllib.request
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
BORG_DIR = BASE / "data_staging" / "borg"
BENCHMARK = BASE / "benchmark"

# IIIF image width for downloads (px)
IMAGE_WIDTH = 1200


def parse_paged_file(filepath, encoding="utf-8"):
    """Parse a #page-delimited file into {page_name: content} dict."""
    pages = {}
    with open(filepath, encoding=encoding) as f:
        text = f.read()

    # Split on #page markers
    parts = re.split(r"^#page\s+", text, flags=re.MULTILINE)[1:]
    for part in parts:
        lines = part.split("\n")
        name = lines[0].strip()
        content = "\n".join(lines[1:]).strip()
        pages[name] = content
    return pages


def normalize_folio(name):
    """Normalize folio names to 4-digit format: 0001r, 0001v, etc."""
    m = re.match(r"^0*(\d+)(r|v)", name.strip())
    if m:
        return f"{int(m.group(1)):04d}{m.group(2)}"
    return name.strip()


def extract_latin_plaintext(combined_text):
    """Extract Latin plaintext from corrected-latin-translation format.

    The file interleaves corrected Latin and English translation.
    Latin lines typically contain | for line breaks and [...] for editorial notes.
    English lines are translations.

    Strategy: take lines that look like Latin (contain | separators or Latin
    pharmaceutical terms) and skip obvious English translations.
    """
    lines = combined_text.split("\n")
    latin_lines = []
    english_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Lines with | are Latin (manuscript line breaks)
        # Lines in [...] brackets alone are section headings (Latin)
        # English translations follow Latin blocks
        if "|" in line or (line.startswith("[") and line.endswith("]")):
            latin_lines.append(line)
        else:
            english_lines.append(line)
        i += 1

    # Join Latin, clean up | markers
    latin_text = " ".join(latin_lines)
    latin_text = re.sub(r"\s*\|\s*", " ", latin_text)
    latin_text = latin_text.strip()

    return latin_text


def build_symbol_map(trans_pages):
    """Build character-level symbol map for the Borg cipher.

    The Borg uses monoalphabetic substitution with ~34 symbols represented
    as single ASCII characters (a-y, 0-9, M) in the transcription.
    Characters are concatenated into word-groups separated by spaces.
    We map each distinct cipher character to an S### token.
    """
    import re
    all_chars = {}
    counter = 1

    for page_name in sorted(trans_pages.keys(), key=normalize_folio):
        text = trans_pages[page_name]
        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith("<CLEARTEXT"):
                continue
            # Remove editorial brackets and their content
            clean = re.sub(r"\[.*?\]", "", line)
            for ch in clean:
                if ch == " ":
                    continue  # spaces are word separators, not symbols
                if ch not in all_chars:
                    all_chars[ch] = f"S{counter:03d}"
                    counter += 1

    return all_chars


def diplomatic_to_canonical(text, symbol_map):
    """Convert diplomatic transcription to character-level canonical form.

    Each cipher character is mapped to its S### token. Word boundaries
    (spaces) are preserved as spaces between token groups. Each word
    becomes a space-separated sequence of S-tokens, with words separated
    by double-space or a special SPACE token.
    """
    import re
    canon_lines = []
    unknown = set()

    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("<CLEARTEXT"):
            continue

        # Remove editorial brackets
        clean = re.sub(r"\[.*?\]", "", line)

        # Process word by word, preserving word boundaries
        words = clean.split()
        canon_words = []
        for word in words:
            chars = []
            for ch in word:
                if ch in symbol_map:
                    chars.append(symbol_map[ch])
                else:
                    chars.append(f"UNKNOWN_{ch}")
                    unknown.add(ch)
            if chars:
                canon_words.append(" ".join(chars))

        if canon_words:
            # Join words with | delimiter for readability
            canon_lines.append(" | ".join(canon_words))

    return "\n".join(canon_lines), unknown


def download_iiif_image(iiif_base_url, output_path, width=IMAGE_WIDTH, timeout=30):
    """Download an image from IIIF at specified width."""
    import socket
    url = f"{iiif_base_url}/full/{width},/0/default.jpg"
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    ERROR downloading {url}: {e}")
        # Remove partial file
        if os.path.exists(output_path):
            os.remove(output_path)
        return False
    finally:
        socket.setdefaulttimeout(old_timeout)


def main():
    print("Parsing Borg cipher files...")

    trans_pages = parse_paged_file(BORG_DIR / "transcription.txt")
    print(f"  Transcription: {len(trans_pages)} pages")

    plain_pages = parse_paged_file(BORG_DIR / "corrected_latin_translation.txt")
    print(f"  Corrected Latin + translation: {len(plain_pages)} pages")

    # Load IIIF mapping
    with open(BORG_DIR / "iiif_mapping.json") as f:
        iiif_map = json.load(f)
    print(f"  IIIF image mapping: {len(iiif_map)} pages")

    # Build symbol map
    print("\nBuilding global symbol map...")
    symbol_map = build_symbol_map(trans_pages)
    print(f"  {len(symbol_map)} unique tokens")

    # Find pages with all three layers
    usable = []
    for page_name in sorted(trans_pages.keys(), key=normalize_folio):
        norm = normalize_folio(page_name)
        has_trans = bool(trans_pages.get(page_name, "").strip())
        has_plain = bool(plain_pages.get(page_name, "").strip()) or bool(plain_pages.get(norm, "").strip())
        has_image = page_name in iiif_map

        # Check if page has actual cipher content (not cleartext-only)
        # After removing CLEARTEXT markers, editorial brackets, and whitespace,
        # there should be actual cipher characters remaining
        page_text = trans_pages.get(page_name, "")
        cipher_chars = 0
        for line in page_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("<CLEARTEXT"):
                continue
            clean = re.sub(r"\[.*?\]", "", line).strip()
            cipher_chars += len(clean.replace(" ", ""))
        has_cipher = cipher_chars > 0

        if has_trans and has_plain and has_image and has_cipher:
            usable.append(page_name)

    print(f"\nUsable pages (image + transcription + plaintext): {len(usable)}")

    # Determine which pages have cleartext
    cleartext_pages = [p for p in usable if "<CLEARTEXT" in trans_pages[p]]
    print(f"Pages with mixed cleartext: {len(cleartext_pages)}")

    # Create benchmark records
    print(f"\nCreating {len(usable)} benchmark records...")
    print("(Downloading images from Vatican Library IIIF — this will take a while)")

    records = []
    all_unknown = set()
    download_errors = []

    for i, page_name in enumerate(usable):
        norm = normalize_folio(page_name)
        record_id = f"borg_{norm}"

        diplo_text = trans_pages[page_name]

        # Get plaintext (try both name formats)
        plain_text = plain_pages.get(page_name, "") or plain_pages.get(norm, "")
        latin_plain = extract_latin_plaintext(plain_text)

        # Write diplomatic transcription
        diplo_path = BENCHMARK / "transcriptions" / f"{record_id}.diplomatic.txt"
        diplo_path.write_text(diplo_text, encoding="utf-8")

        # Write canonical transcription
        canon_text, unknown = diplomatic_to_canonical(diplo_text, symbol_map)
        all_unknown.update(unknown)
        canon_path = BENCHMARK / "transcriptions" / f"{record_id}.canonical.txt"
        canon_path.write_text(canon_text, encoding="utf-8")

        # Write plaintext (Latin)
        plain_path = BENCHMARK / "plaintext" / f"{record_id}.txt"
        plain_path.write_text(latin_plain, encoding="utf-8")

        # Download image
        img_path = BENCHMARK / "images" / f"{record_id}.jpg"
        if not img_path.exists():
            iiif_base = iiif_map[page_name]
            success = download_iiif_image(iiif_base, img_path)
            if not success:
                download_errors.append(page_name)
            # Rate limit
            time.sleep(0.5)

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(usable)} records")

        # Count distinct cipher characters on this page
        page_symbols = set()
        has_cleartext = "<CLEARTEXT" in diplo_text
        for line in diplo_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("<CLEARTEXT"):
                continue
            clean = re.sub(r"\[.*?\]", "", line)
            for ch in clean:
                if ch != " ":
                    page_symbols.add(ch)

        record = {
            "id": record_id,
            "source": "borg",
            "source_record_id": f"MSS_Borg.lat.898_{norm}",
            "source_url": "https://digi.vatlib.it/view/MSS_Borg.lat.898",
            "task_tracks": ["image2transcription", "transcription2plaintext", "image2plaintext"],
            "rights_class": "linked_only",
            "status": "solved_verified",
            "cipher_type": ["simple_substitution"],
            "symbol_set": ["alphabetic", "numerical", "diacritical"],
            "symbol_count": len(page_symbols),
            "plaintext_language": "la",
            "date_or_century": "17th century",
            "page_count": 1,
            "provenance": "Biblioteca Apostolica Vaticana, MSS Borg.lat.898",
            "solution_reference": "Aldarrab, Knight, Megyesi. 'The Borg Cipher.' DECRYPT project, Stockholm University.",
            "image_files": [f"images/{record_id}.jpg"],
            "transcription_diplomatic_file": f"transcriptions/{record_id}.diplomatic.txt",
            "transcription_canonical_file": f"transcriptions/{record_id}.canonical.txt",
            "plaintext_file": f"plaintext/{record_id}.txt",
            "has_key": True,
            "has_inline_plaintext": has_cleartext,
            "manuscript_page": norm,
            "curation_notes": f"Folio {norm} of MSS Borg.lat.898 (408 folios). "
                            f"Monoalphabetic substitution, 34 cipher symbols. "
                            f"Plaintext is corrected Latin from Örneholm's interpretation. "
                            f"{'Contains cleartext passages. ' if has_cleartext else ''}"
                            f"Image from Vatican Library IIIF (personal/study use only)."
        }
        records.append(record)

    print(f"\n  Created {len(records)} records")
    if download_errors:
        print(f"  Image download errors: {len(download_errors)}: {download_errors[:10]}")
    if all_unknown:
        print(f"  WARNING: Unknown tokens: {all_unknown}")

    # Append to manifest (don't overwrite Copiale records)
    manifest_path = BENCHMARK / "manifest" / "records.jsonl"
    existing = []
    if manifest_path.exists():
        with open(manifest_path) as f:
            for line in f:
                rec = json.loads(line)
                if rec["source"] != "borg":
                    existing.append(rec)

    all_records = existing + records
    with open(manifest_path, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nManifest updated: {len(existing)} existing + {len(records)} new = {len(all_records)} total")

    # Write symbol map
    # Build the known key from the cipher key image
    cipher_key = {
        "a": "V", "b": "Z", "c": "G", "d": "U", "h": "T",
        "i": "C", "k": "Y", "m": "H", "n": "S", "o": "O",
        "q": "R", "v": "D", "w": "E", "x": "I", "y": "X",
        "0": "P", "1": "M", "4": "F", "5": "B", "6": "A",
        "8": "L", "9": "N",
    }

    symmap_path = BENCHMARK / "metadata" / "borg_symbol_map.json"
    with open(symmap_path, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Mapping from Borg cipher diplomatic transcription tokens to canonical S### identifiers",
            "source": "Aldarrab/Knight/Megyesi transcription via Stockholm University",
            "cipher_system": "borg_lat_898",
            "total_symbols": len(symbol_map),
            "mapping": symbol_map,
            "cipher_key": cipher_key,
            "notes": "Monoalphabetic substitution with 34 symbols. Transcription uses ASCII "
                     "characters (a-y, 0-9) with diacritics (^.., ^__, etc.). Some pages have "
                     "cleartext passages marked with <CLEARTEXT>. Editorial notes in [brackets] "
                     "are excluded from canonical form."
        }, f, indent=2, ensure_ascii=False)
    print(f"Symbol map written: {symmap_path} ({len(symbol_map)} symbols)")

    # Validate
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
    cleartext_count = sum(1 for r in records if r["has_inline_plaintext"])
    print(f"\n=== Borg Benchmark Summary ===")
    print(f"Total records:        {len(records)}")
    print(f"Global symbol count:  {len(symbol_map)}")
    print(f"Per-page symbols:     min={min(symbol_counts)}, max={max(symbol_counts)}, avg={sum(symbol_counts)/len(symbol_counts):.0f}")
    print(f"Mixed cleartext:      {cleartext_count} pages")
    print(f"Plaintext language:   Latin")
    print(f"Cipher type:          simple_substitution (monoalphabetic)")
    print(f"Rights class:         linked_only (Vatican Library: personal/study use only)")
    print(f"Image download errors: {len(download_errors)}")


if __name__ == "__main__":
    main()
