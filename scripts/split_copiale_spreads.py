#!/usr/bin/env python3
"""
Split Copiale manuscript spread images into individual page images.

The manuscript PDFs contain 2-page spreads (open book scans). Each spread
shows a verso (left) and recto (right) page. This script splits each spread
at the midpoint to produce individual page images.

Page numbering:
- PDF part1 pages 1-29, part2 pages 1-29 = 58 spreads total
- Page 1 (part1-01) is the front cover (single page)
- Pages 2+ are two-page spreads
- Manuscript pages are numbered 1-105 in the transcription files

Input:  data_staging/copiale/pages/part{1,2}-{NN}.png  (spread images)
Output: data_staging/copiale/individual_pages/page_{NNN}.png
"""

import os
import sys
from pathlib import Path
from PIL import Image

INPUT_DIR = Path("data_staging/copiale/pages")
OUTPUT_DIR = Path("data_staging/copiale/individual_pages")


def split_spread(img_path, left_out, right_out):
    """Split a spread image into left (verso) and right (recto) halves."""
    with Image.open(img_path) as img:
        w, h = img.size
        mid = w // 2

        left = img.crop((0, 0, mid, h))
        right = img.crop((mid, 0, w, h))

        left.save(left_out, "PNG")
        right.save(right_out, "PNG")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all spread images in order
    spreads = sorted(INPUT_DIR.glob("part*-*.png"))
    if not spreads:
        print(f"No spread images found in {INPUT_DIR}")
        sys.exit(1)

    print(f"Found {len(spreads)} spread images")

    # The first image (part1-01) is the front cover — a single page.
    # After that, each spread contains two manuscript pages.
    # The last image in part2 may be the back cover (also single).
    #
    # We'll split all of them and let the user manually verify the mapping
    # to manuscript page numbers in a second pass.

    page_num = 0
    for i, spread_path in enumerate(spreads):
        name = spread_path.stem  # e.g., "part1-03"

        # Check if this looks like a single-page image (cover) or a spread
        with Image.open(spread_path) as img:
            w, h = img.size
            aspect = w / h

        if aspect < 1.2:
            # Likely a single page (portrait orientation), not a spread
            page_num += 1
            out_path = OUTPUT_DIR / f"page_{page_num:03d}.png"
            print(f"  {name} -> single page -> {out_path.name} ({w}x{h}, aspect={aspect:.2f})")
            # Just copy it
            with Image.open(spread_path) as img:
                img.save(out_path, "PNG")
        else:
            # Two-page spread
            page_num += 1
            left_out = OUTPUT_DIR / f"page_{page_num:03d}.png"
            page_num += 1
            right_out = OUTPUT_DIR / f"page_{page_num:03d}.png"
            print(f"  {name} -> spread -> {left_out.name}, {right_out.name} ({w}x{h}, aspect={aspect:.2f})")
            split_spread(spread_path, left_out, right_out)

    print(f"\nTotal individual pages produced: {page_num}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nNOTE: Page numbers are sequential from the PDF. You will need to")
    print("verify the mapping to manuscript page numbers (## PAGE N in the")
    print("transcription files). Some pages may be blank versos or covers.")


if __name__ == "__main__":
    main()
