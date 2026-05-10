#!/usr/bin/env python3
"""
bench.py — command-line explorer for the Classical Cipher Benchmark.

Subcommands
-----------
  list    List records, with optional filters
  show    Show metadata for a single record
  cat     Print the ciphertext (canonical transcription) for a record
  plain   Print the plaintext for a record (solved records only)
  diff    Show cipher tokens aligned with plaintext tokens, word by word
  stats   Summary counts broken down by source, status, and track

Quick examples
--------------
  python scripts/bench.py stats
  python scripts/bench.py list --source borg --limit 10
  python scripts/bench.py list --track transcription2plaintext --solved
  python scripts/bench.py list --area unsolved
  python scripts/bench.py show kryptos_k1
  python scripts/bench.py cat borg_0010r
  python scripts/bench.py cat borg_0010r --diplomatic
  python scripts/bench.py plain borg_0010r
  python scripts/bench.py diff borg_0010r
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_MANIFEST = REPO_ROOT / "benchmark" / "manifest" / "records.jsonl"
UNSOLVED_MANIFEST = REPO_ROOT / "benchmark" / "unsolved" / "manifest" / "records.jsonl"
MAIN_ROOT = REPO_ROOT / "benchmark"
UNSOLVED_ROOT = REPO_ROOT / "benchmark" / "unsolved"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_records(area: str = "all") -> list[tuple[dict, Path]]:
    """Return list of (record, area_root) for the requested area."""
    result = []
    if area in ("main", "all"):
        for rec in _load(MAIN_MANIFEST):
            result.append((rec, MAIN_ROOT))
    if area in ("unsolved", "all"):
        for rec in _load(UNSOLVED_MANIFEST):
            result.append((rec, UNSOLVED_ROOT))
    return result


def find_record(record_id: str) -> tuple[dict, Path] | None:
    """Look up a record by id across both manifests."""
    for rec, root in load_records("all"):
        if rec["id"] == record_id:
            return rec, root
    return None


# ---------------------------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------------------------

def filter_records(
    pairs: list[tuple[dict, Path]],
    *,
    source: str | None = None,
    status: str | None = None,
    track: str | None = None,
    solved: bool = False,
    unsolved_only: bool = False,
    has_image: bool = False,
    has_plaintext: bool = False,
    has_transcription: bool = False,
) -> list[tuple[dict, Path]]:
    out = []
    for rec, root in pairs:
        if source and rec.get("source") != source:
            continue
        if status and rec.get("status") != status:
            continue
        if track and track not in rec.get("task_tracks", []):
            continue
        if solved and rec.get("status") not in ("solved_verified", "solved_probable"):
            continue
        if unsolved_only and rec.get("status") not in ("unsolved", "disputed", "partial_solution"):
            continue
        if has_image and not rec.get("image_files"):
            continue
        if has_plaintext and not rec.get("plaintext_file"):
            continue
        if has_transcription and not rec.get("transcription_canonical_file"):
            continue
        out.append((rec, root))
    return out


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

_STATUS_SHORT = {
    "solved_verified":  "verified",
    "solved_probable":  "probable",
    "partial_solution": "partial",
    "unsolved":         "unsolved",
    "disputed":         "disputed",
}

_TRACK_SHORT = {
    "image2transcription":    "A",
    "transcription2plaintext": "B",
    "image2plaintext":        "C",
    "image2hypothesis":       "D",
}


def _fmt_tracks(tracks: list[str]) -> str:
    return "".join(_TRACK_SHORT.get(t, "?") for t in sorted(tracks))


def _fmt_cipher_type(ct) -> str:
    if not ct:
        return ""
    if isinstance(ct, list):
        return ", ".join(ct)
    return str(ct)


def _trunc(s: str, n: int) -> str:
    s = str(s) if s is not None else ""
    return s if len(s) <= n else s[: n - 1] + "…"


def _area_label(root: Path) -> str:
    return "unsolved" if "unsolved" in root.parts else "main"


# ---------------------------------------------------------------------------
# Subcommand: stats
# ---------------------------------------------------------------------------

def cmd_stats(_args) -> None:
    pairs = load_records("all")
    main_pairs = [(r, ro) for r, ro in pairs if _area_label(ro) == "main"]
    unsolved_pairs = [(r, ro) for r, ro in pairs if _area_label(ro) == "unsolved"]

    def _tally(lst, key_fn):
        counts: dict[str, int] = {}
        for r, _ in lst:
            k = key_fn(r)
            counts[k] = counts.get(k, 0) + 1
        return sorted(counts.items(), key=lambda x: -x[1])

    def _section(title, lst):
        print(f"\n{'─' * 52}")
        print(f"  {title}  ({len(lst)} records)")
        print(f"{'─' * 52}")

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║        Classical Cipher Benchmark — Statistics       ║")
    print(f"╚══════════════════════════════════════════════════════╝")

    _section("MAIN BENCHMARK", main_pairs)
    print("  By source:")
    for s, n in _tally(main_pairs, lambda r: r["source"]):
        print(f"    {n:4d}  {s}")
    print("\n  By status:")
    for s, n in _tally(main_pairs, lambda r: r.get("status", "?")):
        print(f"    {n:4d}  {s}")
    print("\n  By track:")
    all_tracks: dict[str, int] = {}
    for r, _ in main_pairs:
        for t in r.get("task_tracks", []):
            all_tracks[t] = all_tracks.get(t, 0) + 1
    for t, n in sorted(all_tracks.items(), key=lambda x: -x[1]):
        print(f"    {n:4d}  {t}")

    has_img = sum(1 for r, _ in main_pairs if r.get("image_files"))
    has_trans = sum(1 for r, _ in main_pairs if r.get("transcription_canonical_file"))
    has_plain = sum(1 for r, _ in main_pairs if r.get("plaintext_file"))
    print(f"\n  Coverage: {has_img} with images | {has_trans} with transcription | {has_plain} with plaintext")

    _section("UNSOLVED AREA", unsolved_pairs)
    print("  By source:")
    for s, n in _tally(unsolved_pairs, lambda r: r["source"]):
        print(f"    {n:4d}  {s}")
    print("\n  By status:")
    for s, n in _tally(unsolved_pairs, lambda r: r.get("status", "?")):
        print(f"    {n:4d}  {s}")
    print("\n  By partial evidence:")
    for s, n in _tally(unsolved_pairs, lambda r: r.get("partial_solution_evidence", "—")):
        print(f"    {n:4d}  {s}")
    has_img_u = sum(1 for r, _ in unsolved_pairs if r.get("image_files"))
    has_trans_u = sum(1 for r, _ in unsolved_pairs if r.get("transcription_canonical_file"))
    print(f"\n  Coverage: {has_img_u} with images | {has_trans_u} with transcription")
    print()


# ---------------------------------------------------------------------------
# Subcommand: list
# ---------------------------------------------------------------------------

def cmd_list(args) -> None:
    pairs = load_records(args.area)
    pairs = filter_records(
        pairs,
        source=args.source,
        status=args.status,
        track=args.track,
        solved=args.solved,
        unsolved_only=args.unsolved,
        has_image=args.has_image,
        has_plaintext=args.has_plaintext,
        has_transcription=args.has_transcription,
    )

    if args.limit:
        shown = pairs[: args.limit]
        truncated = len(pairs) - args.limit
    else:
        shown = pairs
        truncated = 0

    # Header
    fmt = "{:<30}  {:<14}  {:<10}  {:<6}  {:<10}  {:<8}  {}"
    header = fmt.format("ID", "SOURCE", "STATUS", "TRACKS", "AREA", "LANG", "DATE/CENTURY")
    print(header)
    print("─" * len(header))

    for rec, root in shown:
        tracks = _fmt_tracks(rec.get("task_tracks", []))
        status = _STATUS_SHORT.get(rec.get("status", ""), rec.get("status", "")[:10])
        area = _area_label(root)
        lang = rec.get("plaintext_language") or ""
        date = _trunc(rec.get("date_or_century") or "", 22)
        print(fmt.format(
            _trunc(rec["id"], 30),
            _trunc(rec.get("source", ""), 14),
            status,
            tracks,
            area,
            lang[:8],
            date,
        ))

    if truncated > 0:
        print(f"  … {truncated} more (use --limit or remove --limit to see all)")
    print(f"\n  {len(pairs)} record(s) matched.")


# ---------------------------------------------------------------------------
# Subcommand: show
# ---------------------------------------------------------------------------

def cmd_show(args) -> None:
    hit = find_record(args.id)
    if hit is None:
        print(f"Error: record '{args.id}' not found in either manifest.", file=sys.stderr)
        sys.exit(1)
    rec, root = hit

    def field(label: str, value, width: int = 72) -> None:
        if value is None or value == "" or value == [] or value == {}:
            return
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            value = json.dumps(value, indent=2)
        label_str = f"  {label}:"
        indent = " " * (len(label_str) + 1)
        lines = textwrap.wrap(str(value), width=width - len(indent))
        if not lines:
            return
        print(f"{label_str} {lines[0]}")
        for l in lines[1:]:
            print(f"{indent}{l}")

    area = _area_label(root)
    print(f"\n{'═' * 60}")
    print(f"  {rec['id']}  [{area}]")
    print(f"{'═' * 60}")

    field("Source",       rec.get("source"))
    field("Status",       rec.get("status"))
    field("Task tracks",  rec.get("task_tracks"))
    field("Rights class", rec.get("rights_class"))
    field("Cipher type",  _fmt_cipher_type(rec.get("cipher_type")))
    field("Symbol set",   rec.get("symbol_set"))
    field("Symbol count", rec.get("symbol_count"))
    field("Token count",  rec.get("token_count"))
    field("Language",     rec.get("plaintext_language"))
    field("Date",         rec.get("date_or_century"))
    field("Manuscript p.", rec.get("manuscript_page"))
    field("Word bounds",  rec.get("word_boundaries"))
    field("Synthetic",    rec.get("synthetic"))
    if area == "unsolved":
        field("Partial evidence", rec.get("partial_solution_evidence"))
        field("Notable attempts", rec.get("notable_attempts"))
    field("Provenance",   rec.get("provenance"))

    print()

    # File availability
    def file_status(label: str, rel_path: str | None) -> None:
        if not rel_path:
            print(f"  {label}: —")
            return
        full = root / rel_path
        exists = "✓" if full.exists() else "✗ MISSING"
        print(f"  {label}: {rel_path}  [{exists}]")

    print("  Files:")
    file_status("  Canonical transcription", rec.get("transcription_canonical_file"))
    file_status("  Diplomatic transcription", rec.get("transcription_diplomatic_file"))
    file_status("  Plaintext", rec.get("plaintext_file"))
    for img in rec.get("image_files", []):
        file_status("  Image", img)

    # Context layers
    layers = rec.get("context_layers", {})
    if layers:
        print()
        print("  Context layers available:", ", ".join(layers.keys()))

    # Associated documents
    assoc = rec.get("associated_documents", [])
    if assoc:
        print()
        print("  Associated documents:")
        for doc in assoc:
            print(f"    • {doc.get('id')} — {doc.get('title', '')}")

    # Notes / curation
    if rec.get("curation_notes"):
        print()
        note = rec["curation_notes"]
        wrapped = textwrap.fill(note, width=68, initial_indent="  ", subsequent_indent="  ")
        print("  Curation notes:")
        print(wrapped)

    print()


# ---------------------------------------------------------------------------
# Subcommand: cat  (show ciphertext)
# ---------------------------------------------------------------------------

def cmd_cat(args) -> None:
    hit = find_record(args.id)
    if hit is None:
        print(f"Error: record '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    rec, root = hit

    if args.diplomatic:
        rel = rec.get("transcription_diplomatic_file")
        label = "diplomatic"
    else:
        rel = rec.get("transcription_canonical_file")
        label = "canonical"

    if not rel:
        print(f"Error: record '{args.id}' has no {label} transcription file.", file=sys.stderr)
        sys.exit(1)

    path = root / rel
    if not path.exists():
        print(f"Error: file not found on disk: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text().strip()

    if not args.raw:
        area = _area_label(root)
        print(f"\n── {rec['id']}  [{label}]  [{area}] ──")
        source_info = rec.get("date_or_century") or ""
        if source_info:
            print(f"   {source_info}")
        print()

    print(text)
    if not args.raw:
        print()


# ---------------------------------------------------------------------------
# Subcommand: plain  (show plaintext)
# ---------------------------------------------------------------------------

def cmd_plain(args) -> None:
    hit = find_record(args.id)
    if hit is None:
        print(f"Error: record '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    rec, root = hit

    area = _area_label(root)
    if area == "unsolved":
        print(f"Warning: '{args.id}' is in the unsolved area — no verified plaintext.", file=sys.stderr)
        sys.exit(1)

    rel = rec.get("plaintext_file")
    if not rel:
        print(f"Error: record '{args.id}' has no plaintext file.", file=sys.stderr)
        sys.exit(1)

    path = root / rel
    if not path.exists():
        print(f"Error: plaintext file not found on disk: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text().strip()

    if not args.raw:
        print(f"\n── {rec['id']}  [plaintext] ──")
        print(f"   status: {rec.get('status', '?')}  |  language: {rec.get('plaintext_language', '?')}")
        print()

    print(text)
    if not args.raw:
        print()


# ---------------------------------------------------------------------------
# Subcommand: diff  (cipher vs plaintext, word-aligned)
# ---------------------------------------------------------------------------

def cmd_diff(args) -> None:
    hit = find_record(args.id)
    if hit is None:
        print(f"Error: record '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    rec, root = hit

    area = _area_label(root)
    if area == "unsolved":
        print(f"Error: '{args.id}' is in the unsolved area — no plaintext for diff.", file=sys.stderr)
        sys.exit(1)

    canon_rel = rec.get("transcription_canonical_file")
    plain_rel = rec.get("plaintext_file")

    if not canon_rel:
        print(f"Error: no canonical transcription for '{args.id}'.", file=sys.stderr)
        sys.exit(1)
    if not plain_rel:
        print(f"Error: no plaintext file for '{args.id}'.", file=sys.stderr)
        sys.exit(1)

    canon_path = root / canon_rel
    plain_path = root / plain_rel
    for p in (canon_path, plain_path):
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            sys.exit(1)

    # Parse canonical transcription into words (split on | boundaries)
    canon_raw = canon_path.read_text().strip()
    # The canonical format uses | as word separator; tokens within a word are space-separated
    # Flatten to a list of "words" where each word is a list of tokens
    cipher_words = []
    for word_chunk in canon_raw.replace("\n", " ").split("|"):
        tokens = word_chunk.split()
        if tokens:
            cipher_words.append(tokens)

    # Parse plaintext into words
    plain_raw = plain_path.read_text().strip()
    # Normalize punctuation and split
    import re
    plain_words = re.findall(r"\S+", plain_raw)

    # If no word boundaries in cipher (word_boundaries=False), fall back to token-per-token
    word_boundaries = rec.get("word_boundaries", True)

    print(f"\n── {rec['id']}  [cipher ↔ plaintext] ──")
    print(f"   {rec.get('date_or_century', '')}  |  {rec.get('plaintext_language', '')}  |  {rec.get('status', '')}")
    print()

    if not word_boundaries or not plain_words:
        # Token-by-token alignment (flatten cipher tokens)
        cipher_tokens = [t for w in cipher_words for t in w]
        pairs = list(zip(cipher_tokens, plain_words))
        remainder_c = cipher_tokens[len(plain_words):]
        remainder_p = plain_words[len(cipher_tokens):]

        col = max((len(t) for t in cipher_tokens[:50]), default=6) + 1
        col = min(col, 12)

        header = f"  {'CIPHER':<{col}}  PLAIN"
        print(header)
        print("  " + "─" * (col + 10))
        for ct, pt in pairs[:args.limit]:
            print(f"  {ct:<{col}}  {pt}")
        if len(pairs) > args.limit:
            print(f"  … {len(pairs) - args.limit} more tokens (use --limit N to see more)")
        if remainder_c:
            print(f"\n  [cipher has {len(remainder_c)} extra tokens]")
        if remainder_p:
            print(f"\n  [plaintext has {len(remainder_p)} extra words]")

    else:
        # Word-by-word alignment
        if len(cipher_words) != len(plain_words):
            print(f"  Note: cipher word count ({len(cipher_words)}) ≠ plaintext word count ({len(plain_words)}).")
            print(f"  Showing best-effort alignment up to shorter length.\n")

        pairs = list(zip(cipher_words, plain_words))
        # Column width: max cipher-word token string length
        col = max((sum(len(t) + 1 for t in w) for w, _ in pairs[:50]), default=12) + 1
        col = min(max(col, 12), 40)

        header = f"  {'CIPHER TOKENS':<{col}}  PLAINTEXT WORD"
        print(header)
        print("  " + "─" * (col + 20))
        for i, (ctoks, pword) in enumerate(pairs[: args.limit]):
            cipher_str = " ".join(ctoks)
            print(f"  {cipher_str:<{col}}  {pword}")
        if len(pairs) > args.limit:
            print(f"  … {len(pairs) - args.limit} more words (use --limit N to see more, or -1 for all)")

    print()


# ---------------------------------------------------------------------------
# Subcommand: context  (print context layer text)
# ---------------------------------------------------------------------------

_ALL_LAYERS = ("minimal", "standard", "historical", "max")

_LAYER_FLAGS = ("contains_solution", "contains_plaintext_hint", "contains_cipher_type_hint")


def cmd_context(args) -> None:
    hit = find_record(args.id)
    if hit is None:
        print(f"Error: record '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    rec, root = hit

    layers = rec.get("context_layers", {})
    if not layers:
        print(f"Error: record '{args.id}' has no context_layers field.", file=sys.stderr)
        sys.exit(1)

    # Determine which layers to show
    if args.layer == "all":
        wanted = [name for name in _ALL_LAYERS if name in layers]
        if not wanted:
            wanted = list(layers.keys())
    else:
        if args.layer not in layers:
            available = ", ".join(layers.keys())
            print(
                f"Error: layer '{args.layer}' not found for '{args.id}'. "
                f"Available: {available}",
                file=sys.stderr,
            )
            sys.exit(1)
        wanted = [args.layer]

    if args.raw:
        # Just the text, one layer after another, separated by a blank line
        for i, name in enumerate(wanted):
            if i:
                print()
            print(layers[name].get("text", "").strip())
        return

    # Formatted output
    area = _area_label(root)
    print(f"\n── {rec['id']}  [context layers]  [{area}] ──")

    for name in wanted:
        layer = layers[name]
        label = layer.get("label") or name
        text = layer.get("text", "").strip()

        # Collect active warning flags
        warnings = [f for f in _LAYER_FLAGS if layer.get(f)]
        warn_str = "  ⚠  " + ", ".join(warnings) if warnings else ""

        print(f"\n  ┌─ {name.upper()}  —  {label}{warn_str}")
        # Wrap and indent the text
        for para in text.split("\n"):
            wrapped = textwrap.fill(para, width=70, initial_indent="  │  ", subsequent_indent="  │  ")
            print(wrapped)
        print(f"  └{'─' * 58}")

    print()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bench",
        description="Classical Cipher Benchmark explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              bench stats
              bench list --source borg --limit 10
              bench list --track transcription2plaintext --solved
              bench list --area unsolved --has-image
              bench show kryptos_k1
              bench cat borg_0010r
              bench cat borg_0010r --diplomatic
              bench plain copiale_p050
              bench diff borg_0010r --limit 30
              bench context kryptos_k1
              bench context beale_1 --layer historical
              bench context borg_0010r --layer minimal --raw
        """),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # stats
    sub.add_parser("stats", help="Summary counts by source, status, and track")

    # list
    lp = sub.add_parser("list", help="List records with optional filters")
    lp.add_argument("--area", choices=["main", "unsolved", "all"], default="all",
                    help="Which manifest area to search (default: all)")
    lp.add_argument("--source", help="Filter by source name (e.g. borg, copiale, voynich)")
    lp.add_argument("--status", help="Filter by exact status value")
    lp.add_argument("--track", help="Filter to records that include this track "
                    "(image2transcription, transcription2plaintext, image2plaintext, image2hypothesis)")
    lp.add_argument("--solved", action="store_true",
                    help="Show only solved_verified and solved_probable records")
    lp.add_argument("--unsolved", action="store_true",
                    help="Show only unsolved/disputed/partial_solution records")
    lp.add_argument("--has-image", action="store_true",
                    help="Show only records with at least one image file")
    lp.add_argument("--has-plaintext", action="store_true",
                    help="Show only records with a plaintext file")
    lp.add_argument("--has-transcription", action="store_true",
                    help="Show only records with a canonical transcription file")
    lp.add_argument("--limit", type=int, default=50,
                    help="Max rows to display (default: 50; use 0 for all)")

    # show
    sp = sub.add_parser("show", help="Show metadata for a single record")
    sp.add_argument("id", help="Record ID (e.g. borg_0010r, kryptos_k1)")

    # cat
    cp = sub.add_parser("cat", help="Print the ciphertext for a record")
    cp.add_argument("id", help="Record ID")
    cp.add_argument("--diplomatic", action="store_true",
                    help="Use diplomatic transcription instead of canonical")
    cp.add_argument("--raw", action="store_true",
                    help="Suppress header; print file contents only")

    # plain
    pp = sub.add_parser("plain", help="Print the plaintext for a record (solved records only)")
    pp.add_argument("id", help="Record ID")
    pp.add_argument("--raw", action="store_true",
                    help="Suppress header; print file contents only")

    # diff
    dp = sub.add_parser("diff",
                        help="Show cipher tokens aligned with plaintext tokens, word by word")
    dp.add_argument("id", help="Record ID")
    dp.add_argument("--limit", type=int, default=40,
                    help="Max words/tokens to display (default: 40; use -1 for all)")

    # context
    xp = sub.add_parser("context", help="Print context layer text for a record")
    xp.add_argument("id", help="Record ID")
    xp.add_argument(
        "--layer",
        default="all",
        help=(
            "Which layer to print: minimal, standard, historical, max, or all "
            "(default: all). 'all' prints every layer present in order."
        ),
    )
    xp.add_argument(
        "--raw",
        action="store_true",
        help="Print only the text, no headers or warning flags (useful for piping to a solver)",
    )

    return p


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # --limit 0 or -1 → unlimited
    if hasattr(args, "limit") and args.limit <= 0:
        args.limit = 10 ** 9

    dispatch = {
        "stats":   cmd_stats,
        "list":    cmd_list,
        "show":    cmd_show,
        "cat":     cmd_cat,
        "plain":   cmd_plain,
        "diff":    cmd_diff,
        "context": cmd_context,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
