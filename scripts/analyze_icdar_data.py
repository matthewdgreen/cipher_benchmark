#!/usr/bin/env python3
"""
Analyze ICDAR 2024 HR-Ciphers competition data.

The competition has 5 tasks at line-level (image → transcription):
  Task 1:  Vatican ciphers (digits + diacritics, ~76 symbols, "Easy")
  Task 2A: Borg cipher (17th-c, 34 symbols, "Medium")
  Task 2B: Copiale cipher (18th-c, ~100 symbols, "Medium")
  Task 3A: BNF cipher (symbols, few training pages, "Difficult")
  Task 3B: Ramanacoil cipher (symbols, few training pages, "Difficult")

Data is line-level: each image is a cropped line of cipher text with a
corresponding transcription in a text file (train) or JSON (train ground truth).
Test sets have images only (no ground truth released).

This script analyzes the data to understand what we can use for our benchmark.
"""

import json
import os
from collections import Counter
from pathlib import Path

BASE = Path("/Users/mgreen/Dropbox/src2/cipher_benchmark/data_staging/rrc_hr_ciphers/extracted")

TASKS = {
    "task1": {"name": "Vatican", "dir": "task1", "json": "task1/task1.json",
              "difficulty": "Easy", "symbols": "digits + diacritics (~76)"},
    "task2A": {"name": "Borg", "dir": "Borg", "json": "Borg/task2A.json",
               "difficulty": "Medium", "symbols": "graphic signs, Latin letters, diacritics (34)"},
    "task2B": {"name": "Copiale", "dir": "Copiale", "json": "Copiale/task2B.json",
               "difficulty": "Medium", "symbols": "Latin, Greek, ideograms (~100)"},
    "task3A": {"name": "BNF", "dir": "BNF", "json": "BNF/task3A.json",
               "difficulty": "Difficult", "symbols": "symbols (few training)"},
    "task3B": {"name": "Ramanacoil", "dir": "Ramanacoil", "json": "Ramanacoil/task3B.json",
               "difficulty": "Difficult", "symbols": "symbols (few training)"},
}


def analyze_task(task_id, info):
    task_dir = BASE / info["dir"]
    json_path = BASE / info["json"]

    with open(json_path) as f:
        gt = json.load(f)

    img_dir = task_dir / "img"
    txt_dir = task_dir / "txt"

    all_images = set(os.path.splitext(f)[0] for f in os.listdir(img_dir))
    all_texts = set(os.path.splitext(f)[0] for f in os.listdir(txt_dir)) if txt_dir.exists() else set()
    gt_ids = set(gt.keys())

    train_ids = gt_ids & all_texts
    test_ids = all_images - all_texts

    # Analyze symbol vocabulary from ground truth
    all_tokens = Counter()
    line_lengths = []
    for line_id, text in gt.items():
        tokens = text.split()
        all_tokens.update(tokens)
        line_lengths.append(len(tokens))

    # Check for <SPACE> tokens (word boundaries)
    has_spaces = "<SPACE>" in all_tokens

    print(f"\n{'='*60}")
    print(f"Task {task_id}: {info['name']} ({info['difficulty']})")
    print(f"{'='*60}")
    print(f"  Symbol description: {info['symbols']}")
    print(f"  Train lines (with GT): {len(train_ids)}")
    print(f"  Test lines (no GT):    {len(test_ids)}")
    print(f"  Total images:          {len(all_images)}")
    print(f"  Unique tokens in GT:   {len(all_tokens)}")
    print(f"  Has <SPACE> tokens:    {has_spaces}")
    print(f"  Line length (tokens):  min={min(line_lengths)}, max={max(line_lengths)}, avg={sum(line_lengths)/len(line_lengths):.1f}")
    print(f"  Total tokens in GT:    {sum(line_lengths)}")

    # Top 20 most common tokens
    print(f"\n  Top 20 tokens:")
    for token, count in all_tokens.most_common(20):
        print(f"    {token:30s} {count:>6}")

    return {
        "task_id": task_id,
        "name": info["name"],
        "train": len(train_ids),
        "test": len(test_ids),
        "vocab": len(all_tokens),
        "total_tokens": sum(line_lengths),
        "has_spaces": has_spaces,
    }


def main():
    print("ICDAR 2024 HR-Ciphers Data Analysis")
    print("=" * 60)

    results = []
    for task_id, info in TASKS.items():
        results.append(analyze_task(task_id, info))

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Task':<8} {'Name':<12} {'Train':>6} {'Test':>6} {'Vocab':>6} {'Tokens':>8} {'Spaces':>7}")
    print("-" * 60)
    total_train = total_test = total_tokens = 0
    for r in results:
        print(f"{r['task_id']:<8} {r['name']:<12} {r['train']:>6} {r['test']:>6} {r['vocab']:>6} {r['total_tokens']:>8} {str(r['has_spaces']):>7}")
        total_train += r["train"]
        total_test += r["test"]
        total_tokens += r["total_tokens"]
    print("-" * 60)
    print(f"{'TOTAL':<8} {'':<12} {total_train:>6} {total_test:>6} {'':>6} {total_tokens:>8}")

    print(f"\n\nBENCHMARK RELEVANCE:")
    print(f"  - All data is LINE-LEVEL (image crops + transcription)")
    print(f"  - This maps to our Track A (image → transcription)")
    print(f"  - No plaintext/decipherment data — Track B/C not supported")
    print(f"  - Test sets have NO ground truth (competition held back)")
    print(f"  - Usable train lines with ground truth: {total_train}")
    print(f"  - The Copiale task2B overlaps with our existing Copiale records")
    print(f"  - BNF task3A may overlap with DECODE French candidates")


if __name__ == "__main__":
    main()
