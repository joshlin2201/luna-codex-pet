# Luna Iteration 2026-06-29

This iteration implements the video-grounded Luna behavior pass as actual pet assets.

## What Changed

- Rebuilt Luna in a cleaner cute illustration style while preserving her real rabbit identity.
- Added `tools/render_luna_v3.py`, a deterministic renderer for the full 8 x 9 Codex pet atlas.
- Kept `tools/enrich_luna_iteration.py` as a compatibility wrapper.
- Regenerated `assets/spritesheet.webp`, `assets/contact-sheet.png`, every `assets/previews/*.gif`, and QA JSON.
- Installed the rebuilt package into `~/.codex/pets/luna`.

## Behavior Improvements

- `idle`: low tucked loaf with hidden feet, low head-on-dewlap silhouette, breathing, blink, and ear flick.
- `running-right` / `running-left`: rabbit hop cycle with compact load, forefeet reach, long hind-foot kick, airborne stretch, landing, and recovery.
- `waving`: greeting through ear flick and head tilt only, with no fake paw wave.
- `jumping`: longer binky-style airborne body and visible long hind feet only during motion.
- `failed`: lower, softer loaf with drooping posture and no symbols or props.
- `waiting`: front-facing attentive loaf with dewlap covering the legs and only tiny rabbit feet in select frames.
- `running`: nose-down exploration/processing loop instead of a generic run or typing animation.
- `review`: head tilt, asymmetric ears, and left-eye focus.

## Accuracy Locks Preserved

- Luna remains a white-and-gray lionhead-mix rabbit, not a generic round mascot.
- Head sits low into the dewlap/chest cushion.
- Loaf states hide the feet or show only tiny tucked rabbit feet.
- Directional and jump states expose long hind feet only when the legs are actually extending.
- No paw pads, hands, fingers, arm-like forelegs, props, shadows, speed lines, text, or floating effects.
- Public repo still excludes raw private photos, videos, extracted frames, and local media paths.

## Validation

The v3 render passes the local validator:

```json
{
  "ok": true,
  "width": 1536,
  "height": 1872,
  "errors": [],
  "warnings": [],
  "transparent_rgb_residue_pixels": 0
}
```
