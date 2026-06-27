# Luna Pet Feature Map

Showcase package: `luna-codex-pet`

## Loadable Codex Files

- `pet.json` - Codex custom pet manifest.
- `assets/spritesheet.webp` - Fixed 8x9 Codex pet atlas, 192x208 cells.

## Expanded State Behaviors

- `idle`: compact tucked loaf with steep raised haunch, nose twitch, asymmetric blink, ear flick, and subtle breathing.
- `running-right`: rightward rabbit hopping gait with forefeet reach, hind-leg load, long hind-foot kick/toe-off, flight, and recovery.
- `running-left`: separately generated leftward rabbit hopping gait with forefeet reach, hind-leg load, long hind-foot kick/toe-off, flight, and recovery.
- `waving`: greeting through ear flick and head tilt, not a fake paw wave.
- `jumping`: binky-style jump with compact crouch, hind-foot kick, flatter long airborne extension, and settle.
- `failed`: soft deflation through ear droop, head lowering, and eye expression.
- `waiting`: alert input-needed loop with perked ears, head lift, nose twitch, and blink.
- `running`: active task-processing loop in place through ear, nose, eye, and head motion.
- `review`: careful inspection loop through head tilt, focused left-eye squint, blink, and ear adjustment.

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
