---
name: nv-generate-video
version: "1.0.0"
description: Generate TikTok-style ecommerce video clips through the local APIMart pipeline (Kling, Doubao Seedance, HappyHorse, etc.). Use after nv-recreate-video produces shot prompts, or when the user asks to turn an approved script into video.
---

# generate-video (local APIMart)

## Constraints

- Uses **APIMart** (`HIGGSFIELD_API_KEY` in project `.env`), not CreatOK.
- Ask for confirmation before paid generation unless user passed `--yes`.
- Follow `references/generate_rules.md`.

## Default models

| Use case | Model | Duration |
|----------|-------|----------|
| 3s hook | `doubao-seedance-1-0-pro-fast` | 3 |
| product hero / multi-shot | `kling-v3-omni` | 5-15 |
| product-only broll | `kling-v3` | 5 |
| detail broll | `happyhorse-1.0` | 5 |

Models and hook defaults also load from `config/hybrid_remix.json`.

## Runtime

Submit new generation:

```bash
python scripts/run.py \
  --run_id <id> \
  --prompt "<english prompt>" \
  [--model doubao-seedance-1-0-pro-fast] \
  [--orientation 9:16] \
  [--seconds 3] \
  [--definition 480p] \
  [--reference_images d:/path/renwu.png,d:/path/chanpin.png] \
  [--yes]
```

Poll existing task:

```bash
python scripts/run.py --run_id <id> --task_id <task_id> [--wait]
```

## Workflow

1. Resolve model/duration from recreate shot prompt or user request.
2. Upload reference images when `@产品图` / `@人物图` are available.
3. Confirm with user unless they already approved.
4. Run script, poll task, download `outputs/generated.mp4`.
5. Report `task_id`, `video_url`, and local path.

## Prompt rules

Each shot prompt should include:

- vertical 9:16 and exact duration
- scene, subject, camera move, lighting
- product stability language when product appears
- negative: watermark, distorted product, unreadable text, copied identity

For Kling Omni with two refs, use `<<<image_1>>>` person and `<<<image_2>>>` product in prompt when appropriate.

## Artifacts

```
.artifacts/<run_id>/outputs/result.json
.artifacts/<run_id>/outputs/result.md
.artifacts/<run_id>/outputs/generated.mp4
```

## Post-production handoff

For hook + body splice, subtitles, and voiceover, hand off to project scripts:

- `scripts/hybrid_remix.py` — splice, subtitles, round1 builds
- `scripts/elevenlabs_tts.py` — voiceover

## Errors

- Missing API key → check `.env` / `HIGGSFIELD_API_KEY`
- Unsupported model/duration → see `skill/_shared/capabilities.py`
