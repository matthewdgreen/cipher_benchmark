#!/usr/bin/env python3
"""
Triage DECODE decrypted records to identify benchmark candidates.

Analyzes the 1,400 exported detail records for:
- Whether transcription data is accessible (private_ciphertext flag)
- Cipher type and symbol set distributions
- Language distribution
- Archive/holder distribution
- Image rights indicators
- Records with plaintext language specified
- Page count distribution
"""

import json
import re
from collections import Counter
from pathlib import Path

DETAIL_FILE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/data_staging/decode_decrypted_ciphers_detail.jsonl")


def clean_html(text):
    """Strip HTML tags."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def main():
    records = []
    with open(DETAIL_FILE) as f:
        for line in f:
            data = json.loads(line)
            if data.get("success"):
                records.append(data["records"])

    print(f"Total decrypted records: {len(records)}\n")

    # 1. Private ciphertext flag
    private = Counter(r.get("private_ciphertext") for r in records)
    print("=== Ciphertext Accessibility ===")
    for k, v in private.most_common():
        label = "PRIVATE (no access)" if k == "True" else "PUBLIC (accessible)" if k == "False" else f"Unknown ({k})"
        print(f"  {label}: {v}")

    public_records = [r for r in records if r.get("private_ciphertext") != "True"]
    print(f"\n  Publicly accessible records: {len(public_records)}")

    # 2. Language distribution (all records and public only)
    print("\n=== Cleartext Language (all records) ===")
    lang_all = Counter(r.get("cleartext_lang", "unknown") or "unknown" for r in records)
    for lang, count in lang_all.most_common(15):
        print(f"  {lang}: {count}")

    print("\n=== Cleartext Language (public records only) ===")
    lang_pub = Counter(r.get("cleartext_lang", "unknown") or "unknown" for r in public_records)
    for lang, count in lang_pub.most_common(15):
        print(f"  {lang}: {count}")

    # 3. Plaintext language (separate field — may indicate solution quality)
    has_plaintext_lang = [r for r in records if r.get("plaintext_lang")]
    print(f"\n=== Plaintext Language Field ===")
    print(f"  Records with plaintext_lang set: {len(has_plaintext_lang)}")
    if has_plaintext_lang:
        pt_lang = Counter(r["plaintext_lang"] for r in has_plaintext_lang)
        for lang, count in pt_lang.most_common(10):
            print(f"    {lang}: {count}")

    # 4. Cipher types
    print("\n=== Cipher Types (numeric codes) ===")
    ct = Counter()
    for r in records:
        types = r.get("cipher_types", "")
        if types:
            for t in str(types).split(","):
                ct[t.strip()] += 1
    for code, count in ct.most_common():
        print(f"  Type {code}: {count}")

    # 5. Symbol sets
    print("\n=== Symbol Sets (numeric codes) ===")
    ss = Counter()
    for r in records:
        sets = r.get("symbol_sets", "")
        if sets:
            for s in str(sets).split(","):
                ss[s.strip()] += 1
    for code, count in ss.most_common():
        print(f"  Set {code}: {count}")

    # 6. Country/city distribution
    print("\n=== Archive Country (all records) ===")
    country = Counter(r.get("current_country", "unknown") or "unknown" for r in records)
    for c, count in country.most_common(15):
        print(f"  {c}: {count}")

    print("\n=== Archive Country (public records only) ===")
    country_pub = Counter(r.get("current_country", "unknown") or "unknown" for r in public_records)
    for c, count in country_pub.most_common(15):
        print(f"  {c}: {count}")

    # 7. Page count distribution
    print("\n=== Page Count Distribution (public records) ===")
    page_counts = []
    for r in public_records:
        try:
            pages = int(r.get("number_of_pages", 0))
            page_counts.append(pages)
        except (ValueError, TypeError):
            pass
    if page_counts:
        buckets = Counter()
        for p in page_counts:
            if p <= 1:
                buckets["1 page"] += 1
            elif p <= 4:
                buckets["2-4 pages"] += 1
            elif p <= 10:
                buckets["5-10 pages"] += 1
            elif p <= 50:
                buckets["11-50 pages"] += 1
            else:
                buckets["50+ pages"] += 1
        for bucket in ["1 page", "2-4 pages", "5-10 pages", "11-50 pages", "50+ pages"]:
            print(f"  {bucket}: {buckets.get(bucket, 0)}")
        print(f"  Total pages across all public records: {sum(page_counts)}")

    # 8. Rights indicators in additional_information
    print("\n=== Rights Indicators in additional_information ===")
    rights_mentions = {"not in the public domain": 0, "public domain": 0,
                       "permission": 0, "creative commons": 0, "CC BY": 0,
                       "open access": 0, "no info": 0}
    for r in records:
        info = (r.get("additional_information") or "").lower()
        if not info:
            rights_mentions["no info"] += 1
            continue
        found = False
        if "not in the public domain" in info or "not public domain" in info:
            rights_mentions["not in the public domain"] += 1
            found = True
        elif "public domain" in info:
            rights_mentions["public domain"] += 1
            found = True
        if "permission" in info:
            rights_mentions["permission"] += 1
            found = True
        if "creative commons" in info or "cc by" in info or "cc-by" in info:
            rights_mentions["creative commons"] += 1
            found = True
        if "open access" in info:
            rights_mentions["open access"] += 1
            found = True
        if not found:
            rights_mentions["no info"] += 1
    for k, v in sorted(rights_mentions.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # 9. Best candidates: public, with cleartext language, reasonable page count
    print("\n=== TOP CANDIDATES ===")
    print("(Public access, known language, 1-20 pages)\n")

    candidates = []
    for r in public_records:
        lang = r.get("cleartext_lang") or "unknown"
        if lang == "unknown":
            continue
        try:
            pages = int(r.get("number_of_pages", 0))
        except (ValueError, TypeError):
            continue
        if pages < 1 or pages > 20:
            continue

        info = r.get("additional_information") or ""
        rights_ok = "not in the public domain" not in info.lower()

        candidates.append({
            "id": r["id"],
            "name": r.get("name", ""),
            "lang": lang,
            "pages": pages,
            "country": r.get("current_country", "?"),
            "holder": clean_html(r.get("current_holder", "")),
            "author": clean_html(r.get("author", "")),
            "cipher_types": r.get("cipher_types", ""),
            "rights_ok": rights_ok,
            "has_dates": bool(r.get("start_year")),
            "date": r.get("start_year", ""),
            "info_snippet": clean_html(info)[:120] if info else "",
        })

    # Sort: rights_ok first, then by language diversity value
    candidates.sort(key=lambda x: (not x["rights_ok"], x["lang"], -x["pages"]))

    print(f"Total candidates: {len(candidates)}")
    print(f"  Rights appear OK: {sum(1 for c in candidates if c['rights_ok'])}")
    print(f"  Rights may be restricted: {sum(1 for c in candidates if not c['rights_ok'])}")

    print(f"\n--- Candidates with no rights restrictions mentioned ({sum(1 for c in candidates if c['rights_ok'])}) ---")
    lang_groups = Counter(c["lang"] for c in candidates if c["rights_ok"])
    print(f"  By language: {dict(lang_groups.most_common())}")

    print(f"\n--- Sample candidates (rights OK, first 30) ---")
    print(f"{'ID':>6} {'Pages':>5} {'Lang':>10} {'Country':>12} {'Name':<25} {'Date':>6} {'Info snippet'}")
    print("-" * 120)
    shown = 0
    for c in candidates:
        if c["rights_ok"] and shown < 30:
            print(f"{c['id']:>6} {c['pages']:>5} {c['lang']:>10} {c['country']:>12} {c['name']:<25} {c['date']:>6} {c['info_snippet'][:50]}")
            shown += 1

    # 10. Dump full candidate list to CSV for manual review
    out_path = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/data_staging/decode_triage_candidates.csv")
    with open(out_path, "w") as f:
        f.write("id,name,language,pages,country,holder,cipher_types,rights_ok,date,info_snippet\n")
        for c in candidates:
            holder = c['holder'].replace('"', "'")
            snippet = c['info_snippet'].replace('"', "'")
            f.write(f'{c["id"]},"{c["name"]}",{c["lang"]},{c["pages"]},{c["country"]},"{holder}",{c["cipher_types"]},{c["rights_ok"]},{c["date"]},"{snippet}"\n')
    print(f"\n  Full candidate list written to: {out_path}")


if __name__ == "__main__":
    main()
