# Shared contracts for local video skills

## Artifact layout

```
<skill>/.artifacts/<run_id>/
  input/
  transcript/
  vision/
  outputs/
  logs/
```

## Machine-readable outputs

- analyze: `outputs/result.json`
- recreate: `outputs/recreate_source.json`
- generate: `outputs/result.json` + `outputs/result.md`

## Analyze result shape

Compatible with creatok-analyze-video so recreate can consume it:

```json
{
  "run_id": "...",
  "skill": "nv-analyze-video",
  "video": { "duration": 15.0, "local_video_path": "..." },
  "transcript": { "segments": [{ "sequence": 1, "start": 0.0, "end": 1.8, "content": "..." }] },
  "vision": { "scenes": [{ "sequence": 1, "start": 0.0, "end": 3.0, "title": "...", "shot_type": "..." }] }
}
```
