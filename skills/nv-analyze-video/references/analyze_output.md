# Analyze output template

Use this format for the user-facing analyze step. Keep it scannable for creators and sellers.

## Required sections

### 1. Original script

Timestamped lines from `transcript.segments`:

| 时间 | 口播/字幕 |
|------|-----------|
| 0:00-0:02 | ... |

If transcript is empty, infer cautiously from `vision.scenes` and state assumptions.

### 2. Storyboard table

| 时间 | 画面摘要 | 视觉动作 | 口播/字幕 |
|------|----------|----------|-----------|

Source data:
- time ranges from `transcript.segments` or `vision.scenes`
- visual action from `vision.scenes[].title` and extracted frames / contact sheet

### 3. Video metrics

Grounded only in available data:
- duration
- platform label if known
- do not invent views/likes unless provided by the user

### 4. Short assessment

One paragraph:
- video type (selling pitch, demo, before/after, lifestyle, etc.)
- hook mechanism
- why the structure works or feels weak

### 5. Next steps

Offer numbered choices. Tell the user to reply with a digit only:

1. 改写为我的产品 → hand off to `nv-recreate-video`
2. 输出 AI 可生成脚本
3. 拆解转化逻辑

Example closing line: `回复 1、2 或 3 即可继续。`

## Analysis emphasis by video type

- **Selling video**: hook, value, proof, CTA, claim order
- **Product demo**: what is shown first, demonstration clarity
- **Before/after**: contrast timing and believability
- **Non-selling**: hook, pacing, emotional pull; do not force selling analysis

## Do not do in analyze step

- do not write final per-shot generation prompts unless user chose option 2
- do not call `nv-generate-video`
- do not copy original watermark, creator identity, music, or exact subtitle text as reusable assets

For recreation rules, compliance, and the 8-section execution pack, read `../../nv-recreate-video/references/` when the user continues to step 1.
