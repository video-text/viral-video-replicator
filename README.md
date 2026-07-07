# Viral Video Skills

Codex / Claude / OpenClaw skill pack for viral ecommerce video replication.

Merged from:
- **viral-video-replicator** (storyboard + prompt rules)
- **creatok-skills** structure (analyze → recreate → generate chain)
- **local APIMart pipeline** (Doubao / Kling / HappyHorse)

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

## Configure API key

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
  --model doubao-seedance-1-0-pro-fast \
  --seconds 3 \
  --reference_images /path/to/person.png \
  --yes
```

## Repo layout

```
skills/
  nv-analyze-video/     # ffmpeg local analyze
  nv-recreate-video/    # storyboard + prompt pack (merged viral-video-replicator)
  nv-generate-video/    # APIMart generation
shared/                 # Python runtime shared by all skills
references/             # shared contracts + templates
```

## Migration from standalone viral-video-replicator

The old single-skill install is now **`nv-recreate-video`**. Its `references/` folder contains all former `viral-video-replicator` docs (`input_template.md`, `compliance.md`, `prompt_rules.md`, etc.).

Use the full chain for best results:
`nv-analyze-video` → `nv-recreate-video` → `nv-generate-video`
