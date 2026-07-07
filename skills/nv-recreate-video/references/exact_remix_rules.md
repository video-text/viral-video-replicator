# Exact Remix Rules

Use this mode when the user asks for near-identical scene/camera/caption replication.

## Goal

Copy the reference video's:

- shot timing
- camera angle and framing
- subject scale and screen position
- color palette and lighting mood
- transition rhythm
- burned-in caption timing and position

Replace only when appropriate:

- character/person identity
- user product
- claim-safe caption copy

Do not copy:

- watermark
- creator identity
- music
- original brand/product
- exact protected captions when the user requests a changed language/product

## Required Workflow

1. Run analyze with dense frames:

```bash
python skills/nv-analyze-video/scripts/run.py \
  --video_path <reference.mp4> \
  --run_id <id> \
  --exact_remix \
  --exact_fps 4
```

2. Read:

```text
.artifacts/<id>/outputs/exact_remix_manifest.json
.artifacts/<id>/outputs/caption_timeline_template.csv
.artifacts/<id>/vision/exact_sheets/
```

3. Fill the `word` column in `caption_timeline_template.csv` from visible burned-in words.

4. Generate clean clips without subtitles. Prompts must include:

```text
Do not generate any on-screen text or subtitles. Captions will be added in post.
```

5. Burn one-word captions in post:

```bash
python skills/nv-generate-video/scripts/burn_word_captions.py \
  --input_video <clean_generated.mp4> \
  --timeline_csv <caption_timeline.csv> \
  --output_video <captioned_generated.mp4>
```

## Duration Rule

The script must adapt to the selected model's native duration support. Do not ask a model for unsupported durations.

Examples:

- `seedance_2_0`: write 4s, 5s, 8s, 12s, or 15s style prompts. For a 3s reference hook, generate 4s with `0.0-3.0s match reference; 3.0-4.0s editing handle`, then trim in post if needed.
- `kling3_0` / `kling3_0_turbo`: can be used for exact 3s hook attempts.
- `veo3_1`: use 4 / 6 / 8 only.
- `gemini_omni`: use 4 / 6 / 8 / 10 only.

For long-form exact remix, the final output duration must match the reference video duration.

- If the reference is 42.214s, the final captioned remix should be 42.214s, or the same rounded delivery duration when the export format requires frame rounding.
- Do not shorten a 43s reference to 40s unless the user explicitly asks for a shorter edit.
- Because video models do not support arbitrary 43s single requests, split the reference timeline into model-native clips, then trim/extend edit handles and concatenate to match the original total duration.
- Segment durations may be model-native values such as 4s, 5s, 6s, 8s, 10s, 12s, or 15s, but every segment must map back to an exact reference time range.
- Each segment prompt should state both the generated segment duration and the reference time range it covers.
- For batch editing, you may generate extra alternate takes, but the primary reconstruction timeline must preserve the reference duration.

Example for a 42.214s reference:

```text
Reference duration: 42.214s.
Primary reconstruction target: 42.214s.
Plan:
- Clip 01: generate 4s, covers reference 0.000-3.000, trim final 1s handle if needed.
- Clip 02: generate 5s, covers reference 3.000-8.000.
- ...
- Final assembly: concatenate trimmed clips and force final duration to 42.214s.
```

## Product / Character Consistency Rule

Before writing exact-remix prompts, decide whether the user product is visually consistent with the reference product.

Use these checks:

- same product category
- same packaging silhouette
- same usage mode
- same scene logic
- same prop role in the story

If the uploaded product is **not consistent** with the reference product:

- do not change the reference character type aggressively
- preserve the same character archetype, camera staging, pose rhythm, and action logic
- replace the product role only where it naturally appears
- keep a generic, non-identical version of the reference character style; do not copy watermark, creator identity, or exact proprietary assets

If the uploaded product **is consistent** with the reference product:

- product can be swapped more directly
- the character may be lightly varied
- camera, action, color palette, and caption rhythm should remain almost unchanged

For the skeleton-style reference:

- if the user's product differs from the original spray/product category, keep a generic skeleton-like mascot/character archetype and the same action rhythm
- change only enough details to avoid direct character copying
- do not switch to an unrelated realistic human unless the user explicitly asks for a looser adaptation

## Prompt Shape

For exact remix, prompts should be camera-timeline first, not marketing-copy first:

```text
Vertical 9:16 realistic video, no on-screen text. Match the reference timing and model-native duration:
0.0-0.4s dark green overhead wide shot, subject tiny and centered, fast zoom begins.
0.4-0.8s overhead top of head grows larger, hand enters near hairline.
0.8-1.4s tighter scalp/top-head shot, fingers part hair.
1.4-2.2s extreme overhead scalp close-up, same screen position and zoom speed.
2.2-3.0s hard cut to shower medium shot, subject washing hair.
3.0-4.0s editing handle if the selected model requires 4 seconds.
Keep a generic skeleton-like character archetype when product mismatch requires preserving reference role continuity. Do not copy watermark, creator identity, original captions, music, or original brand.
```

## Caption Rule

Video models should not render captions. Burned captions are controlled by ASS/ffmpeg after generation.

For one-word-per-frame captions:

- use uppercase words
- white bold text
- small dark shadow/outline
- keep the same screen anchor as the reference
- time each word with the reference frame/timestamp
