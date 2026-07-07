# Common Rules

## Skill handoff

- Hand off naturally between `nv-analyze-video` -> `nv-recreate-video` -> `nv-generate-video`.
- Do not require the user to say skill names.
- Carry forward product name, images, script, and shot prompts across steps.

## API errors

- Default generation uses Higgsfield CLI. If it is not set up, run `python skills/nv-generate-video/scripts/setup_higgsfield.py`.
- If APIMart legacy mode returns auth errors, check `HIGGSFIELD_API_KEY` in project `.env`.
- If ffmpeg is missing, tell the user to install ffmpeg and ensure it is on PATH.

## Local runtime

- Analyze uses ffmpeg locally, not a remote analyze API.
- Generate uses Higgsfield CLI by default; APIMart remains a legacy option.
- Default video models come from `config/models.json`.
