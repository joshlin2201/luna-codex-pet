# Luna Animation Spec

This is the working spec for preserving Luna's expanded behavior set.

## Iteration 2026-06-29

Luna v3 is a deterministic cute-illustration render pass. It replaces the earlier transformed semi-realistic sheet with directly rendered state poses grounded in Luna's private video references and the public behavior evidence contract.

The active renderer is `tools/render_luna_v3.py`. The older `tools/enrich_luna_iteration.py` command remains as a compatibility wrapper.

## Iteration 2026-06-28

Luna v2 fills all 8 atlas cells in every row. The first runtime-compatible frames still preserve the Codex state order, while the previously empty cells now contain Luna-consistent in-between or return-loop frames for richer showcase playback and future renderers that scan all columns.

## Runtime States

| Row | State | Frames | Capability |
| --- | --- | ---: | --- |
| 0 | `idle` | 8 | Compact tucked loaf with steep haunch, breathing, nose twitch, asymmetric blink, and small ear flick. |
| 1 | `running-right` | 8 | Rightward rabbit gait with forefeet reach, hind-foot kick/toe-off, flight, and recovery. |
| 2 | `running-left` | 8 | Mirrored/smoothed leftward rabbit gait with forefeet reach, hind-foot kick/toe-off, flight, and recovery. |
| 3 | `waving` | 8 | Friendly ear flick and head tilt instead of an inaccurate foreleg wave. |
| 4 | `jumping` | 8 | Binky-style compact crouch, hind-foot kick, flatter airborne stretch, and settle. |
| 5 | `failed` | 8 | Soft droop: ears lower, head dips, loaf compresses. |
| 6 | `waiting` | 8 | Alert input-needed loaf with perked ears and nose twitch. |
| 7 | `running` | 8 | In-place processing loop as low nose-down exploration, not literal sprinting. |
| 8 | `review` | 8 | Focused inspection loop with head tilt and Luna's quirky left-eye squint. |

## Accuracy Locks

- Resting states are rabbit loafs: legs underneath, dewlap and ruff covering the front leg area.
- In loaf states, Luna's head sits low into the dewlap/chest cushion; avoid a tall neck or perched head.
- Tucked long hind legs make the loaf shorter and the gray rear haunch steep/raised behind the low white front.
- In movement/jump extension frames, the body gets flatter/longer and hind feet kick or trail behind/to the side as long rabbit feet.
- Directional gait rows must show forefeet reach/land, hindquarters load, hind feet extend through toe-off, flight, and recovery.
- Preserve mottled gray saddle detail and irregular side patches; avoid smooth gray and simple stripe bands.
- Hidden feet are preferred in loaf states. If feet appear, they should be small rabbit feet tucked under the chest or pointing outward/downward.
- Never add paw pads, hand-like forelimbs, fingers, dog/cat feet, short generic back paws, props, text, shadows, scenery, or detached effects.
- Preserve the long body, gray saddle patches, white blaze, dark eye mask, subtle lionhead ruff, upright asymmetric ears, and quirky left eye.

## Video-Grounded Interaction Locks

- Chat/feed states should use the behavior vocabulary documented in `docs/LUNA-BEHAVIOR-EVIDENCE.md`: loaf, wait, inspect, sniff, hop, peek, and settle.
- `idle`, `waiting`, `review`, `failed`, and in-place `running` should stay grounded in low loaf or low exploration poses unless a future source clip explicitly supports a higher pose.
- `running-right`, `running-left`, and `jumping` are the only states that should regularly expose the long hind feet, because the videos show them extending during real locomotion.
- Hover/click feedback should be a sniff, tiny pivot, or approach/retreat cue, not a hand wave or floating effect.
- Completion should return to a low loaf. Error should lower and soften the loaf, not add symbols or props.

## Renderer Contract

- Source of truth: `tools/render_luna_v3.py`.
- Output files: `assets/spritesheet.webp`, `assets/contact-sheet.png`, `assets/previews/*.gif`, `qa/installed-validation.json`, `qa/qa-review.json`, and `qa/qa-summary.json`.
- Installed package: `~/.codex/pets/luna/pet.json` and `~/.codex/pets/luna/spritesheet.webp`.
- Any renderer change must preserve the 1536 x 1872 atlas, 8 x 9 grid, 192 x 208 cells, transparent background, and all nine Codex state rows.

## Repair Priority

1. Fix rabbit anatomy before style polish.
2. Fix Luna-specific markings before generic cuteness.
3. Use cuteness through proportions, softness, expression, and motion timing, not through humanized limbs.
4. Keep the silhouette readable at 192x208 pixels.
