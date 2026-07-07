---
name: nv-recreate-video
version: "2.0.0"
description: Recreate viral TikTok/Douyin ecommerce videos for the user's own product. Merges local analyze artifacts with the viral-video-replicator 8-section storyboard and per-shot prompts for Kling, Seedance, HappyHorse, Wan, or Doubao via APIMart.
---

# recreate-video

This skill **replaces the standalone `viral-video-replicator` skill**. All original reference docs now live in `references/`.

## Constraints

- Replicate structure, pacing, hook mechanism, and camera logic — especially the **first 3 seconds**.
- Must NOT copy watermark, music, creator identity, or exact captions.
- `@参考视频` / local video = structure reference only.
- `@产品图` = only visual product reference.
- `@人物图` = optional character reference.

## Reference files

- `references/storyboard_templates.md` — 8-section output format
- `references/input_template.md` — user input templates
- `references/output_templates.md` — final answer templates
- `references/prompt_rules.md` — model prompt rules
- `references/shot_patterns.md` — viral ecommerce patterns
- `references/workflow.md` — full replication workflow
- `references/compliance.md` — safe claims and boundaries
- `references/common-rules.md` — handoff rules

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

Read `.artifacts/<run_id>/outputs/recreate_source.json`, then produce the 8-section execution pack.

## Output structure

1. 输入摘要
2. 复刻策略摘要
3. 前三秒专项拆解
4. 完整分镜（5-6 镜头）
5. 全片统一约束
6. 全局提示词
7. 逐镜头提示词
8. 执行顺序

## Claims grading

- **A级**: visible on product image / packaging
- **B级**: user-provided notes
- **C级**: safe generic phrasing
- **禁止**: medical cure, guaranteed results, invented specs

## Handoff

When user confirms generation → `nv-generate-video` with shot prompts and reference images.
