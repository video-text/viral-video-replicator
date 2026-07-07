---
name: nv-recreate-video
version: "2.1.0"
description: Recreate viral TikTok/Douyin ecommerce videos for the user's own product, including exact-remix workflows for matching reference camera timing and burned-in one-word captions.
---

# recreate-video

This skill replaces the standalone `viral-video-replicator` skill. All original reference docs live in `references/`.

## Constraints

- Replicate structure, pacing, hook mechanism, and camera logic, especially the first 3 seconds.
- For exact-remix requests, use dense frame analysis and post-production captions instead of asking the video model to render subtitles.
- Must not copy watermark, music, creator identity, original product, or protected exact captions when adapting to a new product/language.
- `@reference video` / local video = structure, rhythm, camera, caption timing reference.
- `@product image` = visual product reference.
- `@person image` = optional character/person reference.

## Reference Files

- `references/storyboard_templates.md` - 8-section output format
- `references/input_template.md` - user input templates
- `references/output_templates.md` - final answer templates
- `references/prompt_rules.md` - model prompt rules
- `references/shot_patterns.md` - viral ecommerce patterns
- `references/workflow.md` - full replication workflow
- `references/compliance.md` - safe claims and boundaries
- `references/common-rules.md` - handoff rules
- `references/exact_remix_rules.md` - exact camera/caption replication workflow

## Runtime

```bash
python scripts/run.py \
  --video_path <abs_path> \
  --run_id <id> \
  [--transcript_path <srt_or_txt>] \
  [--product_name <name>] \
  [--product_image <abs_path>] \
  [--person_image <abs_path>]
```

For exact remix, analyze first with dense frames:

```bash
python ../nv-analyze-video/scripts/run.py \
  --video_path <abs_path> \
  --run_id <id> \
  --exact_remix \
  --exact_fps 4
```

Read `.artifacts/<run_id>/outputs/recreate_source.json`, then produce the 8-section execution pack.

## Output Structure

1. Input summary
2. Replication strategy
3. First-three-seconds breakdown
4. Full storyboard
5. Global constraints
6. Global prompt
7. Per-shot prompts
8. Execution order

For exact remix, also include:

- frame-by-frame camera timeline
- caption word timeline source
- clean-video generation prompts with no subtitles
- post-production caption burn command

## Claims Grading

- **A-level**: visible on product image / packaging
- **B-level**: user-provided notes
- **C-level**: safe generic phrasing
- **Forbidden**: medical cure, guaranteed results, invented specs

## Handoff

When user confirms generation, hand off to `nv-generate-video` with shot prompts and reference images. Exact-remix captions are added after generation via `burn_word_captions.py`.
