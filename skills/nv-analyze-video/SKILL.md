---
name: nv-analyze-video
version: "1.0.0"
description: Analyze a local TikTok/Douyin/reference video with ffmpeg, produce transcript + scene artifacts, and output a creator-friendly script and storyboard table. Use when the user uploads a reference video or asks to break down a selling video structure.
---

# analyze-video (local)

## Constraints

- Input is a **local video file** (`.mp4`, `.mov`, etc.), not a remote CreatOK API.
- Optional `.srt` or plain transcript file improves script accuracy.
- Follow `references/analyze_output.md` for the user-facing analyze format.
- Follow `references/common-rules.md` for handoff rules.
- For recreation/compliance/prompt rules, read `../nv-recreate-video/references/` only after analyze is done.
- Final user-facing language should match the user's input language.

## Runtime

```bash
python scripts/run.py --video_path <abs_path> --run_id <id> [--transcript_path <srt_or_txt>] [--source_url <url>]
```

Then read `.artifacts/<run_id>/outputs/result.json`.

## Workflow

1. Run the script when the user provides a local reference video.
2. Read `transcript.segments` and `vision.scenes`.
3. Produce user-facing output:
   - timestamped original script
   - storyboard table: `时间 | 画面摘要 | 视觉动作 | 口播/字幕`
   - short metrics section from `video.duration`
4. End with numbered next steps; user can reply `1`, `2`, or `3`:
   1. 改写为我的产品 → hand off to `nv-recreate-video`
   2. 输出 AI 可生成脚本
   3. 拆解转化逻辑

## Analysis focus

Infer video type internally (selling pitch, pain-solution, demo, before/after, review, lifestyle). Emphasize:

- hook / value / proof / CTA for selling videos
- hook, pacing, emotional pull for non-selling content

## Artifacts

```
.artifacts/<run_id>/
  input/video_details.json
  transcript/transcript.json
  vision/vision.json
  vision/cover.jpg
  vision/frames/
  outputs/result.json
```

## Notes

- If transcript is empty, infer spoken content cautiously from scene timing and tell the user assumptions.
- Use `vision/contact_sheet.jpg` when present for visual confirmation.
