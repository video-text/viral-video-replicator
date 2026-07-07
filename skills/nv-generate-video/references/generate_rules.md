# Generate rules

## Handoff

- Run only after the user confirms shot prompts from `nv-recreate-video`.
- Carry forward prompt text, model choice, duration, and reference image paths.

## Prompt source

Per-shot prompts should come from:

- `../nv-recreate-video/references/prompt_rules.md`
- the approved `Scene / Subject / Camera / Constraints` blocks in conversation

## Shared rules

- `../nv-recreate-video/references/common-rules.md`
- `../nv-recreate-video/references/compliance.md`

## API errors

- Missing Higgsfield CLI: run `python scripts/setup_higgsfield.py`.
- Not authenticated: run `python scripts/setup_higgsfield.py`.
- No workspace selected: generation auto-selects the only workspace; with multiple workspaces, choose one via `higgsfield workspace set <id>`.
- APIMart legacy mode: missing `HIGGSFIELD_API_KEY` means set it in `.env` or environment variables.
