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

Replace only:

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

## Prompt Shape

For exact remix, prompts should be camera-timeline first, not marketing-copy first:

```text
Vertical 9:16 realistic video, no on-screen text. Match the reference timing:
0.0-0.4s dark green overhead wide shot, subject tiny and centered, fast zoom begins.
0.4-0.8s overhead top of head grows larger, hand enters near hairline.
0.8-1.4s tighter scalp/top-head shot, fingers part hair.
1.4-2.2s extreme overhead scalp close-up, same screen position and zoom speed.
2.2-3.0s hard cut to shower medium shot, subject washing hair.
Replace the original character with a generic adult. Do not copy skeleton character, watermark, original captions, music, or original brand.
```

## Caption Rule

Video models should not render captions. Burned captions are controlled by ASS/ffmpeg after generation.

For one-word-per-frame captions:

- use uppercase words
- white bold text
- small dark shadow/outline
- keep the same screen anchor as the reference
- time each word with the reference frame/timestamp
