#!/usr/bin/env python3
"""
Generate predefined test suite definitions (splits) for the benchmark.

Creates difficulty-tiered test definitions for each cipher source:
- single: 1 target page, 0 context (hardest)
- 10-page: 1 target page, 9 context pages
- full: 1 target page, all other pages as context (easiest)

Each tier is generated for Tracks A, B, and C, with 5 representative
target pages per cipher.
"""

import json
import random
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark")
MANIFEST = BASE / "benchmark" / "manifest" / "records.jsonl"
SPLITS_DIR = BASE / "benchmark" / "splits"

TRACKS = [
    ("image2transcription", "A"),
    ("transcription2plaintext", "B"),
    ("image2plaintext", "C"),
]

# Seed for reproducible context selection
random.seed(42)


def load_records():
    """Load all records from manifest, grouped by source."""
    sources = {}
    for line in open(MANIFEST):
        rec = json.loads(line)
        src = rec["source"]
        if src not in sources:
            sources[src] = []
        sources[src].append(rec)
    return sources


def select_targets(records, n=5, exclude_cleartext=True):
    """Pick n evenly-spaced target pages from clean records."""
    pool = records
    if exclude_cleartext:
        pool = [r for r in records if not r.get("has_inline_plaintext", False)]

    # Sort by ID for deterministic ordering
    pool = sorted(pool, key=lambda r: r["id"])

    if len(pool) <= n:
        return [r["id"] for r in pool]

    step = len(pool) // (n + 1)
    return [pool[step * (i + 1)]["id"] for i in range(n)]


def select_context(all_ids, target_id, n):
    """Pick n random context pages, excluding the target."""
    pool = [x for x in all_ids if x != target_id]
    if n >= len(pool):
        return sorted(pool)
    return sorted(random.sample(pool, n))


def make_test(test_id, track, cipher_system, target, context, description):
    return {
        "test_id": test_id,
        "track": track,
        "cipher_system": cipher_system,
        "target_records": [target],
        "context_records": context,
        "description": description,
    }


def generate_suite(source_name, cipher_system, records, context_sizes):
    """Generate a full test suite for one cipher source.

    context_sizes: dict mapping tier name -> number of context pages
        e.g. {"single": 0, "10page": 9, "full": "all"}
    """
    targets = select_targets(records)

    # All record IDs (including cleartext pages — valid as context)
    all_ids = sorted(r["id"] for r in records)

    tests = []
    for tier_name, ctx_size in context_sizes.items():
        for track_code, track_letter in TRACKS:
            for target_id in targets:
                if ctx_size == "all":
                    context = sorted(x for x in all_ids if x != target_id)
                    ctx_desc = f"all {len(context)} other pages"
                elif ctx_size == 0:
                    context = []
                    ctx_desc = "no context"
                else:
                    context = select_context(all_ids, target_id, ctx_size)
                    ctx_desc = f"{len(context)} context pages"

                test_id = f"{source_name}_{tier_name}_{track_letter}_{target_id}"
                desc = (
                    f"Track {track_letter}: {target_id} with {ctx_desc}"
                )

                tests.append(make_test(
                    test_id=test_id,
                    track=track_code,
                    cipher_system=cipher_system,
                    target=target_id,
                    context=context,
                    description=desc,
                ))

    return tests


def main():
    print("Loading manifest...")
    sources = load_records()

    all_tests = {}

    # --- Copiale ---
    copiale = sources.get("copiale", [])
    if copiale:
        print(f"\nCopiale: {len(copiale)} records")
        copiale_tests = generate_suite(
            source_name="copiale",
            cipher_system="copiale",
            records=copiale,
            context_sizes={
                "single": 0,
                "10page": 9,
                "full": "all",
            },
        )
        all_tests["copiale"] = copiale_tests
        print(f"  Generated {len(copiale_tests)} test definitions")
        targets = select_targets(copiale)
        print(f"  Target pages: {targets}")

    # --- Borg ---
    borg = sources.get("borg", [])
    if borg:
        print(f"\nBorg: {len(borg)} records ({sum(1 for r in borg if not r.get('has_inline_plaintext'))} without cleartext)")
        borg_tests = generate_suite(
            source_name="borg",
            cipher_system="borg_lat_898",
            records=borg,
            context_sizes={
                "single": 0,
                "10page": 9,
                "full": "all",
            },
        )
        all_tests["borg"] = borg_tests
        print(f"  Generated {len(borg_tests)} test definitions")
        targets = select_targets(borg)
        print(f"  Target pages: {targets}")

    # --- Write split files ---
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)

    # Write per-source files
    for source_name, tests in all_tests.items():
        outpath = SPLITS_DIR / f"{source_name}_tests.jsonl"
        with open(outpath, "w") as f:
            for t in tests:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(f"\nWrote {outpath.name}: {len(tests)} tests")

    # Write combined file
    combined = SPLITS_DIR / "all_tests.jsonl"
    total = 0
    with open(combined, "w") as f:
        for tests in all_tests.values():
            for t in tests:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
                total += 1
    print(f"Wrote all_tests.jsonl: {total} tests")

    # Summary
    print("\n=== Split Summary ===")
    for source_name, tests in all_tests.items():
        tiers = {}
        for t in tests:
            tier = t["test_id"].split("_")[1] if source_name == "copiale" else "_".join(t["test_id"].split("_")[1:2])
            # Extract tier from test_id: {source}_{tier}_{track}_{target}
            parts = t["test_id"].removeprefix(f"{source_name}_")
            tier = parts.split("_")[0]
            track = t["track"]
            key = (tier, track)
            tiers[key] = tiers.get(key, 0) + 1

        print(f"\n{source_name}:")
        for (tier, track), count in sorted(tiers.items()):
            print(f"  {tier:8s} × {track:30s} = {count} tests")


if __name__ == "__main__":
    main()
