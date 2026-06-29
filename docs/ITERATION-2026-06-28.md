# Luna Iteration - 2026-06-28

## Goal

Enrich Luna by filling the remaining atlas cells and reducing state similarity without sacrificing her rabbit-specific anatomy.

## Changes

- Filled all 15 previously empty cells so every state row has 8 visible frames.
- Smoothed `running-left` by deriving it from the stronger rightward gait, preserving timing while reversing direction.
- Reworked the directional gait loop to avoid the awkward scale jump between long extension and recovery frames.
- Expanded `waving`, `jumping`, `waiting`, `running`, and `review` with return-loop or in-between frames.
- Kept loaf states grounded: low head on dewlap, hidden or tucked feet, steep haunch when the long hind legs are folded.
- Kept action states rabbit-specific: long hind feet only appear in movement, and no paw pads, hand-like forelimbs, or arm gestures were added.

## Runtime Note

The original hatch-pet contract uses shorter frame counts for some rows. Luna v2 keeps those first runtime-compatible frames intact while adding full-row bonus frames for richer showcase playback and renderers that scan all 8 columns.

## Rebuild

Run the deterministic enrichment builder from the repo root:

```bash
python3 tools/enrich_luna_iteration.py
```

It rewrites:

- `assets/spritesheet.webp`
- `assets/contact-sheet.png`
- `assets/previews/*.gif`
- `qa/installed-validation.json`
- `qa/qa-review.json`
- `qa/qa-summary.json`

The builder is idempotent. If the atlas already has all 72 cells filled, it regenerates the contact sheet, previews, and QA files without applying the enrichment transforms a second time.
