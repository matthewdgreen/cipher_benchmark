# Proposed patch to `benchmark/manifest/schema.json`

Draft: 2026-04-23. Review and apply after running `../decipher` validator
over the current manifest to establish a baseline; re-run after each change
to catch breakages.

Each change is labeled **S1–S7** and numbered independently so they can be
cherry-picked.

---

## S1. Refresh `source` examples to match reality

**Problem.** `source.examples` still lists `["copiale", "decode", "hcportal",
"icdar"]`, but the live manifest (per AGENTS.md, 2026-04-20) contains
`copiale`, `borg`, `decode_gallica`, a synthetic substitution source, and
`tool_builtins`.

**Change.**
```json
"source": {
  "type": "string",
  "description": "Source dataset or collection identifier",
  "examples": [
    "copiale",
    "borg",
    "decode_gallica",
    "synthetic_simple_substitution",
    "tool_builtins"
  ]
}
```

Non-breaking. `examples` is documentation, not constraint.

---

## S2. Distinguish synthetic from historical records

**Problem.** 240 synthetic simple-substitution records share the manifest
with historical records. The schema has no field distinguishing them, so
any "benchmark score" aggregated naïvely mixes synthetic and historical
performance.

**Change.** Add two optional fields:
```json
"synthetic": {
  "type": "boolean",
  "default": false,
  "description": "True if this record was generated programmatically rather than drawn from a historical manuscript. Consumers aggregating performance statistics should partition on this field."
},
"generation_config": {
  "type": "object",
  "description": "For synthetic records, captures the generator identity and parameters needed to reproduce. Omitted for historical records.",
  "properties": {
    "generator": {"type": "string"},
    "seed": {"type": ["integer", "string"]},
    "params": {"type": "object", "additionalProperties": true}
  },
  "additionalProperties": true
}
```

Non-breaking (both optional, `synthetic: false` by default). **Migration:**
backfill `synthetic: true` on the 240 existing synthetic records before
downstream tools start trusting the field; optionally fail closed once
backfilled.

---

## S3. Make `rights_class` required

**Problem.** `rights_class` is optional today, yet every release decision
depends on it. The Megyesi coordination draft also advertises it as
required; the schema and the outbound message disagree.

**Change.**
```diff
 "required": [
   "id",
   "source",
   "status",
-  "task_tracks"
+  "task_tracks",
+  "rights_class"
 ],
```

**Breaking** if any current record lacks it. Migration: audit first —
```
jq -c 'select(has("rights_class") | not)' benchmark/manifest/records.jsonl
```
— then either backfill or roll the change with a grace-period validator
warning.

---

## S4. Require at least one of `source_url` or `source_record_id`

**Problem.** Both optional today → a record with neither is unfindable in
source archives. For historical records, at least one provenance pointer
should exist. Synthetic records legitimately may have neither.

**Change.** Add at the top level:
```json
"allOf": [
  {
    "if": {
      "anyOf": [
        {"not": {"required": ["synthetic"]}},
        {"properties": {"synthetic": {"const": false}}}
      ]
    },
    "then": {
      "anyOf": [
        {"required": ["source_url"]},
        {"required": ["source_record_id"]}
      ]
    }
  }
]
```

Requires S2 to land first (uses the `synthetic` flag). **Breaking** for
historical records missing both fields.

---

## S5. Structured image provenance

**Problem.** Gallica IIIF fetch metadata (URL, requested width, applied
folio offset, fetch date) is currently embedded in free-text
`curation_notes`, which is unparseable downstream. A structured field
makes re-fetch, diff, and provenance audit trivial.

**Change.** Add optional field:
```json
"image_provenance": {
  "type": "object",
  "description": "Structured record of where/how the image was fetched. Populate for records whose images were pulled from a live archive (IIIF, HTTP).",
  "properties": {
    "iiif_service": {"type": "string", "format": "uri"},
    "request_url_template": {"type": "string"},
    "requested_width": {"type": "integer", "minimum": 1},
    "fetched_at": {"type": "string", "format": "date"},
    "folio_offset": {"type": "integer"},
    "offset_source": {"type": "string", "description": "e.g. 'gallica_folio_offsets.json'"}
  },
  "additionalProperties": true
}
```

Non-breaking. Migration: populate opportunistically. `scripts/create_decode_gallica_pilot.py`
already carries the data — one-line refactor to emit structured instead of
prose.

---

## S6. Normalize `manuscript_page` to string

**Problem.** Union type `integer | string` splits client code
unnecessarily.

**Change.**
```diff
 "manuscript_page": {
-  "type": ["integer", "string"],
+  "type": "string",
   "description": "Original manuscript page or folio identifier. String form: integer pages serialize as e.g. \"42\"; folio notation uses e.g. \"f3r\" or \"0001r\"."
 }
```

**Breaking** if current records use integer literals. Migration: one-line
manifest rewrite coercing `int → str(int)`.

---

## S7. Optional parseable date bounds

**Problem.** `date_or_century` is free text; temporal filtering requires
parsing.

**Change.** Add:
```json
"date_earliest_year": {
  "type": "integer",
  "description": "Earliest plausible year (inclusive) for the record's original composition. Optional; populated when date_or_century yields a parseable lower bound."
},
"date_latest_year": {
  "type": "integer",
  "description": "Latest plausible year (inclusive). Optional."
}
```

Non-breaking. Migration: opportunistic backfill from `date_or_century`.

---

## Summary

| ID | Change | Breaking? | Blocks on |
|----|--------|-----------|-----------|
| S1 | Refresh `source` examples | No | — |
| S2 | `synthetic` + `generation_config` | No (but migration needed before enforcement) | — |
| S3 | Require `rights_class` | Yes (after audit) | audit |
| S4 | Require at least one source pointer | Yes (for historical) | S2 |
| S5 | `image_provenance` struct | No | — |
| S6 | `manuscript_page` → string-only | Yes | one-line coercion |
| S7 | Optional year bounds | No | — |

## Suggested rollout order

1. S1 + S5 + S7 — pure additions, ship anytime.
2. S2 — ship, then backfill synthetic records, then optionally add a
   validator warning for unflagged synthetic-looking sources.
3. S6 — one-shot coercion + schema tighten in the same commit.
4. S3 — audit then require.
5. S4 — require after S2 ships and synthetic records are tagged.

Each step is independently revertable.
