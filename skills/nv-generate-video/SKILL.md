---
name: nv-generate-video
version: "1.2.0"
description: Generate TikTok-style ecommerce video clips through Higgsfield Cloud models by default, with APIMart as an optional legacy provider, and burn one-word captions in post for exact-remix workflows.
---

# generate-video (Higgsfield Cloud)

## Constraints

- Uses **Higgsfield CLI / Cloud** by default (`higgsfield auth login`), not CreatOK.
- APIMart remains available with `--provider apimart` and `HIGGSFIELD_API_KEY`.
- Ask for confirmation before paid generation unless user passed `--yes`.
- Follow `references/generate_rules.md`.

## Default models

| Use case | Model | Duration |
|----------|-------|----------|
| default ecommerce / UGC | `seedance_2_0` | 5 |
| product hero / cinematic | `kling3_0` | 5-15 |
| fast product broll | `kling3_0_turbo` | 5 |
| detail broll | `wan2_7` | 5 |
| audio/video native | `gemini_omni` | 8 |
| premium physics | `veo3_1` | 4-8 |

Models load from `config/models.json`.

## Runtime

One-time local setup:

```bash
python scripts/setup_higgsfield.py
```

This installs `~/.codex/bin/higgsfield.exe` if missing, starts browser login when needed, and automatically selects the only available Higgsfield workspace.

Submit new generation:

```bash
python scripts/run.py \
  --run_id <id> \
  --prompt "<english prompt>" \
  [--provider higgsfield] \
  [--model seedance_2_0] \
  [--orientation 9:16] \
  [--seconds 5] \
  [--definition 720p] \
  [--reference_images d:/path/person.png,d:/path/product.png] \
  [--yes]
```

Poll existing task:

```bash
python scripts/run.py --run_id <id> --task_id <task_id> [--provider higgsfield] [--wait]
```

Burn one-word captions after generation:

```bash
python scripts/burn_word_captions.py \
  --input_video <clean_generated.mp4> \
  --timeline_csv <caption_timeline.csv> \
  --output_video <captioned_generated.mp4>
```

Legacy APIMart example:

```bash
python scripts/run.py \
  --provider apimart \
  --run_id <id> \
  --prompt "<english prompt>" \
  --model doubao-seedance-1-0-pro-fast \
  --seconds 3 \
  --yes
```

## Workflow

1. Resolve model/duration from recreate shot prompt or user request.
2. Pass reference images to Higgsfield CLI when product/person images are available.
3. Confirm with user unless they already approved.
4. Run script, poll task, download `outputs/generated.mp4`.
5. Report `task_id`, `video_url`, and local path.

## Prompt rules

Each shot prompt should include:

- vertical 9:16 and exact duration
- scene, subject, camera move, lighting
- product stability language when product appears
- negative: watermark, distorted product, unreadable text, copied identity
- exact-remix shots must say: `Do not generate any on-screen text or subtitles. Captions will be added in post.`

For Higgsfield models with two refs, keep role binding in the prompt: first image is the person/scene start frame, second image is the product/end frame when the selected model supports it.

## Artifacts

```text
.artifacts/<run_id>/outputs/result.json
.artifacts/<run_id>/outputs/result.md
.artifacts/<run_id>/outputs/generated.mp4
```

## Post-production handoff

For hook + body splice, subtitles, and voiceover, hand off to project scripts:

- `scripts/hybrid_remix.py` - splice, subtitles, round1 builds
- `scripts/elevenlabs_tts.py` - voiceover

## Errors

- Missing Higgsfield CLI -> run `python scripts/setup_higgsfield.py`
- Not authenticated -> run `python scripts/setup_higgsfield.py`
- No workspace selected -> generation auto-selects the only workspace; if multiple exist, select one manually with `higgsfield workspace set <id>`
- APIMart auth errors -> check `.env` / `HIGGSFIELD_API_KEY`
- Unsupported model/duration -> see `config/models.json` and `shared/capabilities.py`
