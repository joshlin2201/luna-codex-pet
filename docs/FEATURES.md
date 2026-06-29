# Luna Pet Feature Map

Showcase package: `luna-codex-pet`

## Loadable Codex Files

- `pet.json` - Codex custom pet manifest.
- `assets/spritesheet.webp` - Fixed 8x9 Codex pet atlas, 192x208 cells.
- Luna v3 renders all 8 cells in every row; older runtime-compatible frame counts are still represented by the first frames in each row.

## Expanded State Behaviors

- `idle`: compact tucked loaf with steep raised haunch, nose twitch, asymmetric blink, ear flick, and subtle breathing.
- `running-right`: rightward rabbit hopping gait with forefeet reach, hind-leg load, long hind-foot kick/toe-off, flight, and recovery.
- `running-left`: smoother mirrored leftward rabbit hopping gait with forefeet reach, hind-leg load, long hind-foot kick/toe-off, flight, and recovery.
- `waving`: eight-frame greeting through ear flick and head tilt, not a fake paw wave.
- `jumping`: eight-frame binky-style jump with compact crouch, hind-foot kick, flatter long airborne extension, and settle.
- `failed`: soft deflation through ear droop, head lowering, and eye expression.
- `waiting`: alert input-needed loop with perked ears, head lift, nose twitch, and blink.
- `running`: active task-processing loop as low nose-down exploration; distinct from directional hopping.
- `review`: careful inspection loop through head tilt, focused left-eye squint, blink, and ear adjustment.

## V3 Implementation

- `tools/render_luna_v3.py` deterministically renders the full atlas, contact sheet, GIF previews, QA JSON, and installed Codex package.
- `tools/enrich_luna_iteration.py` remains as a compatibility wrapper around the v3 renderer.
- The art style is a cleaner cute illustration rather than the earlier semi-realistic transformed sheet.
- The renderer encodes Luna's markings directly: white blaze, dark mask, mottled gray saddle, side patches, subtle ruff, and asymmetric ears.
- The renderer keeps private video/photo references out of public assets and uses only distilled behavior labels in docs/metadata.

## Chat Feed Interaction Contract

The chat/feed behavior layer should map plugin conditions to real Luna behaviors documented in `docs/LUNA-BEHAVIOR-EVIDENCE.md`:

- Idle chat: low tucked loaf with head cushioned into the dewlap.
- User typing or needs input: quiet attentive loaf with ears forward and only a slight head lift.
- Assistant streaming: nose-down exploration/focused low-body processing.
- Tool calls or directional transitions: short rabbit hop with compact load, forefeet reach, long hind-foot kick, and recovery.
- Review or verification: head turn, asymmetric ears, and Luna's quirky left-eye focus.
- Success: small lift or glance, then settle back into loaf.
- Error: lower head and softer ears, then compact recovery.
- Hover or click: sniff, pivot, tiny approach, or retreat.

Any new interaction should cite source behavior labels before generation and should avoid ungrounded cartoon gestures.

## QA Artifacts

- `assets/contact-sheet.png` - Full visual sheet for all 9 rows.
- `assets/previews/*.gif` - Per-state motion previews.
- `qa/qa-summary.json` - Public-safe validation summary.

## Current Accuracy Rules

- Normal resting states use Luna's tucked rabbit loaf anatomy: legs underneath, dewlap/ruff covering the front legs, feet hidden.
- Luna's head sits low on the dewlap: chin/lower muzzle sinks into the white chest cushion rather than perching above a tall neck.
- Tucked long hind legs create a compact, shorter loaf with a steep raised gray haunch/rump behind the low front.
- Extended hind legs make the body flatter/longer and kick or trail behind/to the side as long rabbit feet, never short generic paws.
- Directional running rows must show the rabbit gait cycle: forefeet reach/land, hindquarters load, hind feet kick through toe-off, flight, and recovery.
- Action states may show feet only when required by realistic rabbit movement.
- No paw pads, hand-like forelimbs, forward arm shapes, props, text, scenery, shadows, or detached effects.
- Preserve Luna's white blaze, dark mask, mottled gray saddle and irregular side patches, lionhead cheek/neck ruff, asymmetric ears, and quirky left eye.
