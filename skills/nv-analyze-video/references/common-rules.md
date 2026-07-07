# Common Rules (analyze step)

## Handoff

- After analyze, offer numbered next steps.
- If the user chooses product rewrite, hand off to `nv-recreate-video`.
- Carry forward `outputs/result.json` and the confirmed video path; do not make the user restate the reference video.

## Shared recreation rules

Detailed storyboard, compliance, prompt, and workflow rules live in the sibling skill:

- `../../nv-recreate-video/references/storyboard_templates.md`
- `../../nv-recreate-video/references/compliance.md`
- `../../nv-recreate-video/references/common-rules.md`

Read those only when moving from analyze to recreate.

## Runtime errors

- Missing ffmpeg: ask the user to install ffmpeg and ensure it is on PATH.
- Missing local video path: analyze requires a local file, not only a URL.
