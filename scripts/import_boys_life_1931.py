#!/usr/bin/env python3
"""
Import Boys' Life 1931 Hood Treasure Hunt ciphers into the unsolved benchmark.

Four ciphers (April/May/June/July) from full-page Hood Rubber Company
advertisement contests published in Boys' Life magazine, 1931. Ciphertexts
sourced from AZdecrypt's Substitution/ and Transposition/ folders and
cross-checked against archive.org magazine scans. Solutions not independently
verified; AZdecrypt's placement in non-Unsolved folders suggests community
solutions exist but have not been located in public archives.

Run from repo root:
    python3 scripts/import_boys_life_1931.py
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UNSOLVED_MANIFEST = REPO / "benchmark" / "unsolved" / "manifest" / "records.jsonl"


def load_manifest(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def save_manifest(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def upsert(records: list[dict], new_rec: dict) -> list[dict]:
    rid = new_rec["id"]
    for i, r in enumerate(records):
        if r["id"] == rid:
            records[i] = new_rec
            print(f"  updated: {rid}")
            return records
    records.append(new_rec)
    print(f"  inserted: {rid}")
    return records


# ---------------------------------------------------------------------------
# Shared context
# ---------------------------------------------------------------------------

_HOOD_POINTS = (
    "The five Hood Points (advertising claims on each cipher ad): "
    "(1) COMFORT TOE, (2) STURDY UPPERS, (3) SURE-FOOTED SOLES, "
    "(4) HYGIENIC INSOLE, (5) FIRM ARCH SUPPORT. "
    "The contest rules required that the plaintext contain ≥ 2 keywords "
    "from one of these five points."
)

_HOOD_HISTORICAL = (
    "The Hood Treasure Hunt was a paid advertisement contest series run by "
    "Hood Rubber Company (Watertown, Mass.) in Boys' Life magazine from April "
    "through July 1931. Each month's ad displayed a cipher message, invited "
    "readers to solve it and mail their solution to Hood before a deadline, "
    "and offered prizes (American Kent Radio, camp supplies, sports equipment). "
    "Hood distributed a free booklet titled 'Secret Writing' that explained "
    "the cipher systems used. This booklet is not known to survive in any "
    "public archive; it is the most likely source of the substitution keys "
    "used in the May and July ciphers. Prize winners for all four months were "
    "listed in the October 1931 issue of Boys' Life, but the plaintext "
    "solutions were not published. AZdecrypt catalogues all four in its "
    "Substitution/ or Transposition/ (non-Unsolved) folders, indicating "
    "community solutions exist, but they have not been independently located."
)

_COMMON = {
    "source": "boys_life_1931",
    "status": "unsolved",
    "task_tracks": ["transcription2plaintext"],
    "rights_class": "open",
    "plaintext_language": "en",
    "word_boundaries": False,
    "date_or_century": "1931",
    "page_count": 1,
    "partial_solution_evidence": "none",
}


# ---------------------------------------------------------------------------
# April 1931 — columnar transposition, 5 × 18 = 90 chars
# ---------------------------------------------------------------------------

APRIL = {
    **_COMMON,
    "id": "boys_life_apr_1931",
    "source_url": "https://archive.org/details/sim_boys-life_1931-04_21_4",
    "cipher_type": ["columnar_transposition"],
    "symbol_set": ["alphabetic_uppercase"],
    "symbol_count": 18,   # distinct letters in this cipher
    "token_count": 90,
    "provenance": (
        "Hood Rubber Company advertisement, Boys' Life, April 1931, p. 31. "
        "Ciphertext from AZdecrypt 'Ciphers/Transposition/Boys' Life April "
        "1931 page 31.txt', cross-checked against archive.org scan "
        "(sim_boys-life_1931-04_21_4, image 0030). "
        "Magazine displays cipher as 10 groups of 9 characters."
    ),
    "transcription_canonical_file": (
        "sources/boys_life_1931/transcriptions/boys_life_apr_1931.canonical.txt"
    ),
    "curation_notes": (
        "Columnar transposition cipher; same 90 letters appear in the plaintext "
        "but reordered. The magazine presents the text as 10 groups of 9 characters, "
        "strongly suggesting a key length of 9 or 10. "
        "Letter M is absent from the ciphertext, ruling out 'FIRM', 'COMFORT', "
        "and 'HYGIENIC' as Hood-Point keyword sources; 'SURE-FOOTED SOLES' is "
        "the most feasible match on letter availability. "
        "AZdecrypt Transposition/ folder (considered solved); no verified "
        "plaintext located in any public archive. "
        "Rights: public domain (Boys' Life 1931, Boy Scouts of America)."
    ),
    "context_layers": {
        "minimal": {
            "label": "Minimal context",
            "text": (
                "Record boys_life_apr_1931 is a cipher puzzle from a full-page "
                "advertisement published in Boys' Life magazine, April 1931, page 31. "
                "It was part of the 'April Hood Treasure Hunt' contest run by Hood "
                "Rubber Company. The cipher encodes a message describing where to "
                "look for a buried treasure. The solution has not been independently "
                "verified."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Cipher family: columnar transposition. "
                "The ciphertext is presented as a 5-row × 18-column grid (90 characters "
                "total); the magazine groups it as 10 groups of 9 characters, "
                "suggesting a keyword of length 9 or 10. "
                "Language: English. No word boundaries. "
                "The plaintext contains the same 90 letters in a different order."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "token_count", "symbol_count"],
        },
        "historical": {
            "label": "Historical and advertising context",
            "text": _HOOD_HISTORICAL + " " + _HOOD_POINTS,
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["source_url", "date_or_century", "provenance", "curation_notes"],
        },
    },
}


# ---------------------------------------------------------------------------
# May 1931 — monoalphabetic substitution, 83 chars
# ---------------------------------------------------------------------------

MAY = {
    **_COMMON,
    "id": "boys_life_may_1931",
    "source_url": "https://archive.org/details/sim_boys-life_1931-05_21_5",
    "cipher_type": ["simple_substitution"],
    "symbol_set": ["alphabetic_uppercase"],
    "symbol_count": 19,   # 19 distinct cipher letters
    "token_count": 83,
    "provenance": (
        "Hood Rubber Company advertisement, Boys' Life, May 1931, p. 35. "
        "Ciphertext from AZdecrypt 'Ciphers/Substitution/Boys' Life May "
        "1931 page 35.txt', cross-checked against archive.org scan "
        "(sim_boys-life_1931-05_21_5, image 0034)."
    ),
    "transcription_canonical_file": (
        "sources/boys_life_1931/transcriptions/boys_life_may_1931.canonical.txt"
    ),
    "curation_notes": (
        "Monoalphabetic substitution using 19 distinct uppercase Latin letters "
        "as cipher symbols. Most frequent cipher letter: R (13×, 15.7%), suggesting "
        "R → E. Simulated-annealing attacks on the 83-character ciphertext find "
        "fragments 'SURE' and 'SOLE' consistent with the Hood Point "
        "'SURE-FOOTED SOLES', but full English plaintext has not been recovered "
        "without the original key. The key was distributed in Hood's 'Secret "
        "Writing' booklet; that booklet is not known to survive. "
        "AZdecrypt Substitution/ folder (considered solved); no verified "
        "plaintext located in any public archive. "
        "Rights: public domain (Boys' Life 1931)."
    ),
    "context_layers": {
        "minimal": {
            "label": "Minimal context",
            "text": (
                "Record boys_life_may_1931 is a cipher puzzle from a full-page "
                "advertisement published in Boys' Life magazine, May 1931, page 35. "
                "It was part of the 'May Hood Treasure Hunt' contest run by Hood "
                "Rubber Company. The cipher encodes a message describing where to "
                "look for a buried treasure. The solution has not been independently "
                "verified."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Cipher family: monoalphabetic substitution. "
                "19 distinct uppercase Latin letters used as cipher symbols, 83 "
                "characters total. Most frequent cipher symbol: R (13 occurrences, "
                "15.7%). Language: English. No word boundaries."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "token_count", "symbol_count"],
        },
        "historical": {
            "label": "Historical and advertising context",
            "text": _HOOD_HISTORICAL + " " + _HOOD_POINTS,
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["source_url", "date_or_century", "provenance", "curation_notes"],
        },
    },
}


# ---------------------------------------------------------------------------
# June 1931 — columnar transposition, 5 × 20 = 100 chars
# ---------------------------------------------------------------------------

JUNE = {
    **_COMMON,
    "id": "boys_life_jun_1931",
    "source_url": "https://archive.org/details/sim_boys-life_1931-06_21_6",
    "cipher_type": ["columnar_transposition"],
    "symbol_set": ["alphabetic_uppercase"],
    "symbol_count": 19,
    "token_count": 100,
    "provenance": (
        "Hood Rubber Company advertisement, Boys' Life, June 1931, p. 35. "
        "Ciphertext from AZdecrypt 'Ciphers/Transposition/Boys' Life June "
        "1931 page 35.txt', cross-checked against archive.org scan "
        "(sim_boys-life_1931-06_21_6, image 0034). "
        "Magazine presents the cipher as 10 groups of 10 characters."
    ),
    "transcription_canonical_file": (
        "sources/boys_life_1931/transcriptions/boys_life_jun_1931.canonical.txt"
    ),
    "curation_notes": (
        "Columnar transposition cipher; same 100 letters appear in the plaintext "
        "but reordered. The magazine presents the text as 10 groups of 10 characters, "
        "suggesting a keyword of length 10. "
        "All five Hood Points are letter-feasible for this cipher (M is present). "
        "AZdecrypt Transposition/ folder (considered solved); no verified "
        "plaintext located in any public archive. "
        "Rights: public domain (Boys' Life 1931)."
    ),
    "context_layers": {
        "minimal": {
            "label": "Minimal context",
            "text": (
                "Record boys_life_jun_1931 is a cipher puzzle from a full-page "
                "advertisement published in Boys' Life magazine, June 1931, page 35. "
                "It was part of the 'June Hood Treasure Hunt' contest run by Hood "
                "Rubber Company. The cipher encodes a message describing where to "
                "look for a buried treasure. The solution has not been independently "
                "verified."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Cipher family: columnar transposition. "
                "The ciphertext is presented as a 5-row × 20-column grid (100 "
                "characters total); the magazine groups it as 10 groups of 10 "
                "characters, suggesting a keyword of length 10. "
                "Language: English. No word boundaries."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "token_count", "symbol_count"],
        },
        "historical": {
            "label": "Historical and advertising context",
            "text": _HOOD_HISTORICAL + " " + _HOOD_POINTS,
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["source_url", "date_or_century", "provenance", "curation_notes"],
        },
    },
}


# ---------------------------------------------------------------------------
# July 1931 — monoalphabetic substitution with symbols, 156 chars
# ---------------------------------------------------------------------------

JULY = {
    **_COMMON,
    "id": "boys_life_jul_1931",
    "source_url": "https://archive.org/details/sim_boys-life_1931-07_21_7",
    "cipher_type": ["simple_substitution"],
    "symbol_set": ["symbolic_mixed"],
    "symbol_count": 19,   # 19 distinct symbols
    "token_count": 156,
    "provenance": (
        "Hood Rubber Company advertisement, Boys' Life, July 1931, p. 29. "
        "Ciphertext from AZdecrypt 'Ciphers/Substitution/Boys' Life July "
        "1931 page 29.txt', cross-checked against archive.org scan "
        "(sim_boys-life_1931-07_21_7, image 0028). "
        "Symbols are standard ASCII: digits (0-9), punctuation, and uppercase "
        "letters (A, B, K, M, X, Z)."
    ),
    "transcription_canonical_file": (
        "sources/boys_life_1931/transcriptions/boys_life_jul_1931.canonical.txt"
    ),
    "curation_notes": (
        "Monoalphabetic substitution using 19 distinct symbols (mix of ASCII "
        "digits, punctuation, and 6 uppercase Latin letters). Most frequent "
        "symbols: '5' (21×, 13.5%) and ')' (20×, 12.8%). The trigram ')X5' "
        "appears 8 times, providing strong evidence for the assignment )=T, "
        "X=H, 5=E (i.e., )X5 = THE). The symbol set partially overlaps with "
        "Poe's Gold Bug (1843) cipher alphabet. Partial frequency-based "
        "decoding recovers fragments consistent with the Hood Points but full "
        "English text has not been recovered without the original key from "
        "Hood's 'Secret Writing' booklet. "
        "AZdecrypt Substitution/ folder (considered solved); no verified "
        "plaintext located in any public archive. "
        "Rights: public domain (Boys' Life 1931)."
    ),
    "context_layers": {
        "minimal": {
            "label": "Minimal context",
            "text": (
                "Record boys_life_jul_1931 is a cipher puzzle from a full-page "
                "advertisement published in Boys' Life magazine, July 1931, page 29. "
                "It was part of the 'July Hood Treasure Hunt' contest run by Hood "
                "Rubber Company. The cipher encodes a message describing where to "
                "look for a buried treasure. The solution has not been independently "
                "verified."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Cipher family: monoalphabetic substitution with mixed symbol alphabet. "
                "19 distinct symbols drawn from ASCII digits, punctuation characters, "
                "and uppercase Latin letters (A, B, K, M, X, Z); 156 characters total. "
                "Most frequent symbols: '5' (13.5%) and ')' (12.8%). "
                "The trigram ')X5' appears 8 times — strong evidence for )=T, X=H, 5=E. "
                "Language: English. No word boundaries."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "token_count", "symbol_count"],
        },
        "historical": {
            "label": "Historical and advertising context",
            "text": _HOOD_HISTORICAL + " " + _HOOD_POINTS,
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["source_url", "date_or_century", "provenance", "curation_notes"],
        },
    },
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Unsolved area — Boys' Life 1931:")
    records = load_manifest(UNSOLVED_MANIFEST)
    for rec in [APRIL, MAY, JUNE, JULY]:
        records = upsert(records, rec)
    save_manifest(UNSOLVED_MANIFEST, records)
    print(f"  manifest written ({len(records)} records)")

    print("\nFile checks:")
    root = REPO / "benchmark" / "unsolved"
    checks = [
        (root / APRIL["transcription_canonical_file"], "April canonical"),
        (root / MAY["transcription_canonical_file"],   "May canonical"),
        (root / JUNE["transcription_canonical_file"],  "June canonical"),
        (root / JULY["transcription_canonical_file"],  "July canonical"),
        (root / "sources/boys_life_1931/metadata/boys_life_1931_source_note.md", "Source note"),
    ]
    all_ok = True
    for path, label in checks:
        status = "✓" if path.exists() else "✗ MISSING"
        print(f"  {status}  {label}  ({path.name})")
        if not path.exists():
            all_ok = False
    if not all_ok:
        sys.exit(1)
    print("\nDone.")


if __name__ == "__main__":
    main()
