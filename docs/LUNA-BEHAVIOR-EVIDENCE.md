# Luna Behavior Evidence

This document turns Luna's private photo and video references into public-safe interaction rules for the Codex pet. Source media and sampled frames are intentionally not included in this repo.

## Evidence Intake

The current behavior pass is grounded in private Luna videos sampled on 2026-06-29, plus the still-photo anatomy pass already captured in `docs/LUNA-REFERENCE-ANALYSIS.md`.

Private source video labels used for behavior analysis:

- `IMG_6465`
- `IMG_6458`
- `IMG_6090`
- `IMG_6464`
- `IMG_5969`
- `IMG_5358`
- `IMG_3776`
- `IMG_1385`
- `IMG_0734_A`
- `IMG_1009`
- `IMG_0734_B`
- `IMG_0697`
- `IMG_0231`
- `D8F25B9E`

## Grounded Behavior Families

### Low Loaf / Idle

Evidence: `IMG_3776`, `IMG_6458`, `IMG_0734_A`, `IMG_0734_B`, `IMG_6465`.

Use a low, grounded loaf as Luna's default. Her head sits into the dewlap/chest cushion, the subtle lionhead ruff spreads around the cheeks and neck, and the front feet are hidden or barely visible below the dewlap. The rear reads steeper when long hind legs are tucked.

Do not make idle Luna upright, round, long-necked, or perched above the chest.

### Waiting / Attention

Evidence: `IMG_6464`, `IMG_6465`, `IMG_0734_A`, `IMG_0734_B`, `D8F25B9E`.

Waiting should be quiet and rabbit-like: ears perk or adjust, the nose points forward or slightly down, and the head lifts only a little from the dewlap. Food-attention clips show that the body stays planted while the head and ears do most of the work.

Do not make waiting into a humanized wave, bounce, or raised-arm pose.

### Review / Focus

Evidence: `IMG_6090`, `IMG_6464`, `IMG_6465`.

Review should use Luna's face, not props. The signature cues are a small head turn, asymmetric ears, the white blaze, dark mask, and slightly quirky left eye. Visible forefeet, when present, stay small and tucked below the chest.

Do not add glasses, magnifiers, typing, pointing, or paw gestures.

### Processing / Active Work

Evidence: `IMG_5358`, `IMG_5969`, `IMG_0231`.

Processing can borrow from Luna's nose-down exploration: long low body, forward reach, cautious scan, then return toward a loaf. This is a better task-running metaphor than fake typing or tool use because it matches how Luna actually investigates.

Do not turn the in-place `running` state into a dog/cat run cycle or a human work animation.

### Directional Hop / Tool Running

Evidence: `IMG_5969`, `IMG_0697`, `IMG_0231`.

Directional movement should use a rabbit hop sequence: compact load, forefeet reach, body extends long and low, hind feet kick or trail, then the haunch catches up. Luna's long back legs matter here. When tucked, the silhouette is shorter and steeper; when extended, the body becomes flatter and longer.

Do not create halfway anatomy where the rear is neither steep/tucked nor flat/extended.

### Social Interaction / Hover Or Click

Evidence: `IMG_0697`.

For interactive moments, Luna should approach, sniff, pivot, or make a small orientation change. She may circle toward the user, turn her head, or settle back. These are grounded, recognizable rabbit responses.

Do not use hand waves, high-fives, arm gestures, hearts, sparkles, or unrelated cartoon reactions.

### Peek / Edge Interaction

Evidence: `IMG_1385`, `IMG_1009`.

Peek behavior can be inspired by Luna looking around cardboard or tunnel edges: partial face, ears forward, white blaze leading, then a retreat or settle. This can work for feed expansion or a message-edge reveal, but the sprite itself should remain Luna-only unless a future renderer explicitly supports scene props.

Do not bake cardboard, tunnel fabric, labels, or household objects into the core pet sprite.

### Settle / Recovery

Evidence: `IMG_6465`, `IMG_1009`, `IMG_3776`.

After completion or error, Luna should compress back into a low loaf. Failed states should read as a softer, lower posture with ears and head carrying the mood.

Do not use cartoon sadness symbols, text, props, or dramatic collapse.

## Chat Feed Interaction Map

| Feed condition | Luna behavior | Evidence |
| --- | --- | --- |
| Idle chat | Low loaf, breathing, tiny nose and ear motion | `IMG_3776`, `IMG_6458`, `IMG_0734_A`, `IMG_0734_B` |
| User typing | Quiet waiting: ears forward, low body, slight head lift | `IMG_6464`, `IMG_6465`, `D8F25B9E` |
| Assistant streaming | Nose-down exploration or focused low-body processing | `IMG_5358`, `IMG_5969` |
| Tool call / navigation | Short directional hop with real rabbit load-kick-recover timing | `IMG_5969`, `IMG_0697`, `IMG_0231` |
| Needs input | Still attentive loaf, face forward, dewlap covering feet | `IMG_6465`, `IMG_0734_A`, `IMG_0734_B` |
| Review or verification | Head turn, asymmetric ears, left-eye focus | `IMG_6090`, `IMG_6464` |
| Success / done | Small lift or glance, then settle back into loaf | `IMG_6464`, `D8F25B9E`, `IMG_6465` |
| Error / failed | Lower head and softer ears, then compact recovery | `IMG_3776`, `IMG_1009` |
| Hover / click | Sniff, pivot, small approach, or small retreat | `IMG_0697`, `IMG_1385`, `IMG_1009` |

## Interaction Design Rules

- Every new animation row or chat-feed behavior must cite one or more Luna reference labels and an anatomy rule before generation.
- Prefer Luna's real behavior vocabulary: loaf, sniff, peek, head turn, ear flick, nose twitch, hop, settle.
- Keep the body low unless a real reference shows a higher sit or hop phase.
- Keep feet rabbit-specific: tucked under the chest, pointing outward/downward when visible, or long and trailing/kicking during movement.
- Preserve coat identity during motion: white blaze, dark eye mask, mottled gray saddle, irregular side patches, subtle lionhead ruff, and quirky left eye.
- Use cuteness through proportions, softness, timing, face, ears, and tiny motion, not through human props or arms.

## Explicit Non-Goals

- No paw pads.
- No hands, fingers, or arm-like front legs.
- No raised foreleg waving.
- No typing, tools, speech bubbles, status icons, hearts, sparkles, or props in the core pet.
- No generic bunny hop cycle that ignores Luna's long body and long hind feet.
- No published raw source photos, videos, extracted frames, or private local paths.
