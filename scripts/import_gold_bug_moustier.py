#!/usr/bin/env python3
"""
Import Gold Bug (Poe, 1843) into the main benchmark and
Moustier St Martin + Moustier Virgin into the unsolved area.

Run from repo root:
    python3 scripts/import_gold_bug_moustier.py

This script is idempotent: re-running it will update existing records in place
and leave all other records untouched.

Sources verified 2026-05:
  Gold Bug — Project Gutenberg #2147, poestories.com, AZdecrypt bundled cipher
  Moustier — Klaus Schmeh (2017 direct observation), Nick Pelling / Cipher
             Mysteries (2013), AZdecrypt bundled cipher (minor discrepancy noted)
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN_MANIFEST = REPO / "benchmark" / "manifest" / "records.jsonl"
UNSOLVED_MANIFEST = REPO / "benchmark" / "unsolved" / "manifest" / "records.jsonl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
# Gold Bug record
# ---------------------------------------------------------------------------

GOLD_BUG_RECORD = {
    "id": "gold_bug_poe",
    "source": "gold_bug",
    "source_url": "https://www.gutenberg.org/ebooks/2147",
    "status": "solved_verified",
    "task_tracks": ["transcription2plaintext"],
    "rights_class": "open",
    "cipher_type": ["simple_substitution"],
    "symbol_set": ["symbolic_mixed"],
    "symbol_count": 21,
    "token_count": 204,
    "plaintext_language": "en",
    "word_boundaries": False,
    "date_or_century": "1843",
    "page_count": 1,
    "provenance": (
        'Edgar Allan Poe, "The Gold-Bug", Dollar Newspaper, Philadelphia, 21 June 1843. '
        "Ciphertext from AZdecrypt community transcription (Windows-1252 re-encoded as UTF-8); "
        "cross-referenced against Project Gutenberg #2147 and poestories.com. "
        "Plaintext is the solution Legrand gives in the story, universally agreed across all editions."
    ),
    "transcription_canonical_file": "sources/gold_bug/transcriptions/gold_bug.canonical.txt",
    "transcription_diplomatic_file": "sources/gold_bug/transcriptions/gold_bug.diplomatic.txt",
    "plaintext_file": "sources/gold_bug/plaintext/gold_bug.txt",
    "solution_reference": "Poe, E.A. The Gold-Bug (1843). Solution given in the story text by Legrand.",
    "curation_notes": (
        "Famous literary cipher, fully solved within the story itself. "
        "The cipher uses 21 distinct symbols (digits, punctuation, special characters). "
        "Poe explicitly gives the substitution key through Legrand's frequency analysis. "
        "Different digital editions assign different Unicode code points to Poe's original "
        "Dollar Newspaper typeset characters. The AZdecrypt transcription (source for the "
        "ciphertext here) uses Windows-1252 encoding; seven cipher positions in the "
        "'forty-one' phrase region conflict when Poe's story-stated key is applied, "
        "indicating an edition-specific encoding variant. A conflict-free key for this "
        "specific transcription can be derived by aligning it against the known plaintext. "
        "Rights: public domain (US, published 1843)."
    ),
    "context_layers": {
        "minimal": {
            "label": "Minimal context",
            "text": (
                'Record gold_bug_poe is the cipher from Edgar Allan Poe\'s short story '
                '"The Gold-Bug," first published in the Dollar Newspaper, Philadelphia, '
                "21 June 1843. The cipher conceals directions to a buried treasure. "
                "This is a solved record; the plaintext is given in the story."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "provenance"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Cipher family: simple substitution. "
                "Symbol set: 21 distinct symbols (digits, punctuation, and special characters). "
                "Token count: 204. Language: English. No word boundaries in the ciphertext. "
                "Poe gives a detailed frequency-analysis solution in the story, making this a "
                "classic pedagogical example of monoalphabetic substitution."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "symbol_set", "symbol_count", "token_count", "word_boundaries"],
        },
        "historical": {
            "label": "Historical and literary context",
            "text": (
                "The Gold-Bug is widely credited with popularising cryptography in American literature. "
                "Poe had published a cryptography column in Alexander's Weekly Messenger (1839-1840) "
                "and the essay 'A Few Words on Secret Writing' (Graham's Magazine, 1841). "
                "Lt. Col. William F. Friedman credited the story as a significant influence on "
                "American cryptanalysis. The story won the Dollar Newspaper's 1843 prize of $100. "
                "The cipher is a straightforward monoalphabetic substitution solvable by letter "
                "frequency analysis, as Poe demonstrates through his character Legrand."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["source_url", "date_or_century", "provenance", "solution_reference"],
        },
    },
}


# ---------------------------------------------------------------------------
# Moustier records
# ---------------------------------------------------------------------------

_MOUSTIER_COMMON = {
    "source": "moustier",
    "source_url": "https://scienceblogs.de/klausis-krypto-kolumne/2017/11/07/the-top-50-unsolved-encrypted-messages-18-the-moustier-altar-inscriptions/",
    "status": "unsolved",
    "task_tracks": ["transcription2plaintext", "image2hypothesis"],
    "rights_class": "open",
    "cipher_type": ["simple_substitution", "unknown"],
    "symbol_set": ["alphabetic_extended"],
    "plaintext_language": "fr",
    "word_boundaries": False,
    "date_or_century": "c. 1838-1843 (church reconstruction)",
    "page_count": 1,
    "partial_solution_evidence": "none",
    "notable_attempts": [
        "Rudy Cambier claimed decipherment in December 1995 via an abjad (vowel-omitting) hypothesis, "
        "suggesting the inscriptions encode the Ten Commandments. Not widely accepted.",
        "The inscriptions were documented in the declassified NSA Cryptolog journal (September 1974).",
    ],
}

MOUSTIER_ST_MARTIN = {
    **_MOUSTIER_COMMON,
    "id": "moustier_st_martin",
    "symbol_count": 28,
    "token_count": 77,
    "manuscript_page": "St. Martin's Altar",
    "provenance": (
        "Inscription carved on the St. Martin's Altar, Saint-Martin's Church, "
        "Moustier (Frasnes-lez-Anvaing), eastern Belgium. "
        "Transcription from Klaus Schmeh (2017, direct observation during 2015 visit) "
        "and Cipher Mysteries / Menno Knul (2013, direct observation); both sources agree. "
        "Also present in AZdecrypt bundled unsolved ciphers (minor character-level discrepancies noted)."
    ),
    "transcription_canonical_file": "sources/moustier/transcriptions/moustier_st_martin.canonical.txt",
    "curation_notes": (
        "One of two paired altar inscriptions of unknown meaning. "
        "Character set includes 26 Latin uppercase letters plus ^ and [ as distinct cipher symbols. "
        "Letter-frequency distribution across both Moustier inscriptions is compatible with "
        "a monoalphabetic substitution in a European language (French or Latin most likely). "
        "The blank line in the transcription separates the two groups of five lines as they appear on the altar. "
        "AZdecrypt's bundled transcription matches except: the Virgin's transcription in AZdecrypt omits "
        "a [ character in line 5; the St. Martin's transcription agrees with both Schmeh and Cipher Mysteries. "
        "Rights: carved inscription on a public place of worship; transcription is scholarly documentation. open."
    ),
    "related_records": [
        {
            "record_id": "moustier_virgin",
            "relationship": "same_church_same_hand_probable",
            "area": "unsolved",
            "solution_available": False,
            "notes": "Companion inscription from the Virgin's Altar in the same church, same period.",
        }
    ],
    "context_layers": {
        "minimal": {
            "label": "Minimal archival context",
            "text": (
                "Record moustier_st_martin is an inscription carved on the St. Martin's Altar "
                "of Saint-Martin's Church, Moustier (Frasnes-lez-Anvaing), eastern Belgium. "
                "The altars date from the church's 1838-1843 reconstruction. "
                "The inscription remains undeciphered."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "manuscript_page"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Character set: 26 Latin uppercase letters plus ^ and [ as distinct cipher symbols (28 total). "
                "Token count: 77 characters arranged in two groups of five lines. "
                "Letter frequency distribution is compatible with monoalphabetic substitution "
                "in French or Latin. Both Moustier inscriptions share a similar frequency profile, "
                "suggesting the same cipher and probable same plaintext language."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "symbol_set", "symbol_count", "token_count"],
        },
        "historical": {
            "label": "Historical and archival context",
            "text": (
                "The Moustier church cryptograms have been unresolved for over 180 years. "
                "They were documented by the NSA Cryptolog (September 1974, declassified) "
                "and by Paul de Saint-Hilaire in La Belgique Mysterieuse (1973). "
                "Professor Jean Connart studied them from 1961 without conclusive results. "
                "Rudy Cambier published an abjad-based claimed solution in his 2002 book "
                "Nostradamus and the Lost Templar Legacy, asserting a connection to Knights Templar "
                "hidden knowledge; this interpretation is not accepted in the cryptographic community. "
                "The altars have been ranked among the top 50 unsolved encrypted messages by cryptohistorian "
                "Klaus Schmeh. The church is a publicly accessible place of worship."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": False,
            "source_fields": ["source_url", "date_or_century", "notable_attempts", "provenance"],
        },
    },
}

MOUSTIER_VIRGIN = {
    **_MOUSTIER_COMMON,
    "id": "moustier_virgin",
    "symbol_count": 28,
    "token_count": 82,
    "manuscript_page": "Virgin's Altar",
    "provenance": (
        "Inscription carved on the Virgin's Altar, Saint-Martin's Church, "
        "Moustier (Frasnes-lez-Anvaing), eastern Belgium. "
        "Transcription from Klaus Schmeh (2017, direct observation during 2015 visit) "
        "and Cipher Mysteries / Menno Knul (2013, direct observation). "
        "AZdecrypt bundled transcription omits one [ character in line 5 (LFN^BKP vs LFN^[BKP); "
        "the Schmeh/Cipher Mysteries version with the [ is used here."
    ),
    "transcription_canonical_file": "sources/moustier/transcriptions/moustier_virgin.canonical.txt",
    "curation_notes": (
        "One of two paired altar inscriptions of unknown meaning. "
        "Character set identical to the companion St. Martin inscription: 26 Latin uppercase letters "
        "plus ^ and [ as distinct cipher symbols. "
        "Frequency distribution closely resembles the St. Martin's Altar, supporting the hypothesis "
        "that both use the same cipher. "
        "Notable discrepancy: the AZdecrypt bundled version has 'LFN^BKP' in line 5; "
        "the Schmeh and Cipher Mysteries direct-observation versions have 'LFN^[BKP' (8 chars). "
        "The Schmeh version is used here as the more authoritative source. "
        "Rights: carved inscription on a public place of worship; transcription is scholarly documentation. open."
    ),
    "related_records": [
        {
            "record_id": "moustier_st_martin",
            "relationship": "same_church_same_hand_probable",
            "area": "unsolved",
            "solution_available": False,
            "notes": "Companion inscription from the St. Martin's Altar in the same church, same period.",
        }
    ],
    "context_layers": {
        "minimal": {
            "label": "Minimal archival context",
            "text": (
                "Record moustier_virgin is an inscription carved on the Virgin's Altar "
                "of Saint-Martin's Church, Moustier (Frasnes-lez-Anvaing), eastern Belgium. "
                "The altars date from the church's 1838-1843 reconstruction. "
                "The inscription remains undeciphered."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": False,
            "contains_cipher_type_hint": False,
            "source_fields": ["id", "source", "date_or_century", "manuscript_page"],
        },
        "standard": {
            "label": "Standard cipher context",
            "text": (
                "Character set: 26 Latin uppercase letters plus ^ and [ as distinct cipher symbols (28 total). "
                "Token count: 82 characters arranged in two groups of five lines. "
                "Letter frequency distribution is compatible with monoalphabetic substitution "
                "in French or Latin. Frequency profile closely matches the companion St. Martin "
                "inscription, supporting a shared cipher and probable same plaintext language."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": True,
            "source_fields": ["cipher_type", "symbol_set", "symbol_count", "token_count"],
        },
        "historical": {
            "label": "Historical and archival context",
            "text": (
                "The Moustier church cryptograms have been unresolved for over 180 years. "
                "See the St. Martin's record (moustier_st_martin) for full historical background. "
                "The Virgin's Altar transcription has a minor variant: the AZdecrypt community "
                "version omits a [ character in line 5; direct-observation sources (Schmeh 2015, "
                "Knul 2013) include it. This record uses the direct-observation version."
            ),
            "contains_solution": False,
            "contains_plaintext_hint": True,
            "contains_cipher_type_hint": False,
            "source_fields": ["source_url", "date_or_century", "notable_attempts", "provenance"],
        },
    },
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # --- Gold Bug → main benchmark ---
    print("Main benchmark:")
    main_records = load_manifest(MAIN_MANIFEST)
    main_records = upsert(main_records, GOLD_BUG_RECORD)
    save_manifest(MAIN_MANIFEST, main_records)
    print(f"  manifest written ({len(main_records)} records)")

    # --- Moustier → unsolved area ---
    print("\nUnsolved area:")
    unsolved_records = load_manifest(UNSOLVED_MANIFEST)
    unsolved_records = upsert(unsolved_records, MOUSTIER_ST_MARTIN)
    unsolved_records = upsert(unsolved_records, MOUSTIER_VIRGIN)
    save_manifest(UNSOLVED_MANIFEST, unsolved_records)
    print(f"  manifest written ({len(unsolved_records)} records)")

    # --- Validate files exist ---
    print("\nFile checks:")
    main_root = REPO / "benchmark"
    unsolved_root = REPO / "benchmark" / "unsolved"
    checks = [
        (main_root / GOLD_BUG_RECORD["transcription_canonical_file"], "Gold Bug canonical"),
        (main_root / GOLD_BUG_RECORD["transcription_diplomatic_file"], "Gold Bug diplomatic"),
        (main_root / GOLD_BUG_RECORD["plaintext_file"], "Gold Bug plaintext"),
        (unsolved_root / MOUSTIER_ST_MARTIN["transcription_canonical_file"], "Moustier St Martin"),
        (unsolved_root / MOUSTIER_VIRGIN["transcription_canonical_file"], "Moustier Virgin"),
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
