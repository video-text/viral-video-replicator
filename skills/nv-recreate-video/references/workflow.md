# Viral ecommerce video recreation workflow

## 1. Reference intake

Classify source material:
- full video: analyze visual rhythm, product role, captions, and voiceover
- screenshots/contact sheet: infer shot order and mark visual uncertainty
- transcript only: reconstruct likely shots and mark visual assumptions

Record:
- reference length and format
- first 3 seconds hook
- product category and product role
- target output length, language, platform, and default model
- uploaded roles: `@参考视频`, `@产品图`, `@人物图`

## 2. Product and claim intake

Before writing the final storyboard, separate claims by source:

| Level | Source | How to use |
|---|---|---|
| A | visible on product image/packaging | highest priority |
| B | provided by user in title or notes | usable if not risky |
| C | safe generic phrasing | use sparingly |
| forbidden | medical cure, guaranteed result, invented specs | never use |

If product appearance matters, require or strongly prefer a product image. A text keyword such as `@产品 sebamed` is not enough for visual stability.

## 3. First 3 seconds: high-fidelity structural replica

The first 3 seconds are the conversion-critical zone. Replicate these attributes as closely as possible without copying protected assets:

| Attribute | Preserve | Replace |
|---|---|---|
| beat count | number of micro-actions | original objects, logos, people |
| camera | distance, angle, motion energy | exact background if distinctive |
| composition | subject positions and visual hierarchy | brand-specific props/signage |
| hook mechanism | urgency, surprise, problem, demo, comparison | exact caption wording |
| rhythm | cuts, pauses, movement direction | original footage/music |

For the first 3 seconds, use micro time ranges such as `0:00-0:00.8`, `0:00.8-0:01.8`, `0:01.8-0:03.0`.

## 4. After 3 seconds: conversion-focused adaptation

After the hook, diverge to fit the user's product. Prefer 5-6 total shots for a 15-20 second first draft:

1. hook/problem replica
2. product entrance
3. product hero or key feature
4. use/demo shot
5. result feeling or relief moment
6. product hero + CTA

Avoid 8+ shots unless the user asks for a detailed long version or the product genuinely needs more steps.

## 5. Replacement strategy

Create a compact mapping before writing prompts:

```text
reference pain/product role -> new product role
reference character role -> generic character or @人物图
reference scene function -> suitable new scene
reference claim -> supported or safe benefit
reference CTA/social proof -> non-deceptive CTA
```

## 6. Final answer order

Default final output:
1. input summary
2. replication strategy summary
3. first 3 seconds micro breakdown
4. full storyboard, 5-6 shots when possible
5. global constraints
6. global prompt
7. per-shot prompts using Scene/Subject/Camera/Constraints
8. execution order

Skip long “why it works” analysis unless the user explicitly asks for analysis.

## 7. Handling weak or incomplete inputs

If the video is unclear, still produce a usable draft but state uncertainty:
- “我只能从当前画面/字幕判断...“
- “以下是基于可见信息的复刻版...“
- “如果你补充产品卖点，我可以把后半段卖点改得更准。”

Do not stall unless the missing input blocks the task entirely.
