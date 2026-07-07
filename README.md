# Viral Video Skills

Codex / Claude / OpenClaw skill pack for viral ecommerce video replication.

Merged from:

- **viral-video-replicator** storyboard and prompt rules
- **creatok-skills** analyze -> recreate -> generate chain
- **Higgsfield Cloud generation**: Seedance 2.0, Kling 3.0, Wan 2.7, Veo 3.1
- optional legacy **APIMart pipeline**: Doubao, Kling, HappyHorse

## Install for Codex

```bash
git clone https://github.com/video-text/viral-video-replicator.git
cd viral-video-replicator
pip install -r requirements.txt

mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

After install you should see:

- `nv-analyze-video`
- `nv-recreate-video` (includes former viral-video-replicator rules)
- `nv-generate-video`

Restart Codex if skills do not appear immediately.

## Configure Higgsfield

Install and log in to the Higgsfield CLI:

```bash
npm install -g @higgsfield/cli
higgsfield auth login
```

The default generation provider is `higgsfield` and the default model is `seedance_2_0`.

## Optional APIMart Legacy Key

Only needed when running `--provider apimart`:

```bash
export HIGGSFIELD_API_KEY="your-apimart-key"
```

Or create `.env` in the repo root or your working directory:

```env
HIGGSFIELD_API_KEY=your-apimart-key
```

## Requirements

- Python 3.10+
- ffmpeg on PATH
- `requests` (`pip install -r requirements.txt`)
- Higgsfield CLI for default generation (`npm install -g @higgsfield/cli`)

## Workflow

```bash
# 1. Analyze local reference video
python skills/nv-analyze-video/scripts/run.py \
  --video_path /path/to/ref.mp4 \
  --run_id demo-001

# 2. Bundle recreate source (+ product images)
python skills/nv-recreate-video/scripts/run.py \
  --video_path /path/to/ref.mp4 \
  --run_id demo-001 \
  --product_name "My product" \
  --product_image /path/to/product.png \
  --person_image /path/to/person.png

# 3. Generate a shot after LLM produces prompt
python skills/nv-generate-video/scripts/run.py \
  --run_id demo-001-shot01 \
  --prompt "Vertical 9:16 realistic UGC hook..." \
  --provider higgsfield \
  --model seedance_2_0 \
  --seconds 5 \
  --reference_images /path/to/person.png,/path/to/product.png \
  --yes
```

## Repo Layout

```text
skills/
  nv-analyze-video/     # ffmpeg local analyze
  nv-recreate-video/    # storyboard + prompt pack
  nv-generate-video/    # Higgsfield generation, APIMart legacy optional
shared/                 # Python runtime shared by all skills
config/models.json      # provider/model capabilities
```

## Migration From Standalone viral-video-replicator

The old single-skill install is now **`nv-recreate-video`**. Its `references/` folder contains all former `viral-video-replicator` docs (`input_template.md`, `compliance.md`, `prompt_rules.md`, etc.).

Use the full chain for best results:
`nv-analyze-video` -> `nv-recreate-video` -> `nv-generate-video`
