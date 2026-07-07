---
name: viral-video-replicator
description: analyzes uploaded tiktok, douyin, or short-form ai ecommerce videos and turns them into concise, safe, original recreation plans. use when the user wants to reverse-engineer a viral product video, make the first three seconds structurally similar, bind a product image with labels such as @产品图, replace the product or actor with their own images, and output compact storyboard tables plus model-ready prompts for kling, seedance, happyhorse, wan, doubao, or similar video models.
---

# Viral Video Replicator

## Purpose

Transform a viral ecommerce reference video into a safe, original **分镜 + 提示词** package for the user's own product. The default is not to generate video, write code, or adapt to a local pipeline unless the user asks.

The user usually provides:
- `@参考视频`: a local TikTok/Douyin/reference video, contact sheet, screenshots, or transcript
- `@产品图`: one or more product images, often named `chanpin.jpg`
- `@人物图`: optional character/person image, often named `renwu.jpg`
- product name, product category, target duration, target language, allowed claims, and forbidden claims

## Core rule: replicate structure, not assets

When the user says “复刻”, preserve successful **creative mechanics** while creating a new ad:
- replicate timing, camera logic, hook type, pacing, composition, emotional beat, and selling structure
- make the first 3 seconds structurally near-identical: same beat count, shot rhythm, camera distance, motion energy, scene role, subtitle cadence, and hook mechanism
- after 3 seconds, prioritize product clarity, safe selling points, and conversion rather than exact matching
- never copy watermarks, logos, music, exact captions, creator likeness, protected characters, distinctive brand identity, or original footage

If the user asks for direct copying of original footage, voice, exact person, watermark, logo, or music, redirect to a safe original remix using the same format and pacing.

## Interpret `@参考视频`, `@产品图`, and `@人物图`

Use labels as role markers:

- `@参考视频`: structure reference only. Use it for hook rhythm, shot timing, camera angle, composition, subtitle pacing, and emotional structure. Do not copy original identity, brand, watermark, music, or exact subtitle text.
- `@产品图`: highest-priority visual product reference. Treat it as the only source for product shape, color, packaging, logo placement, surface material, and visual identity.
- `@人物图`: optional character reference. Use it only when provided and appropriate. Avoid celebrity resemblance or unauthorized identity claims.

Do not rely on product keywords alone. A phrase such as `@产品 sebamed` helps semantically, but the stable visual binding comes from `@产品图` plus explicit product constraints.

## Claims and product facts

Separate claims before writing the storyboard:

- **A级**: visible on product image or packaging. Use first.
- **B级**: explicitly provided by user in product title, notes, or product page copy. Use if safe.
- **C级**: safe generic phrasing such as daily care, easy to use, clean feeling, gentle routine. Use sparingly.
- **禁止**: invented specs, medical cure, guaranteed result, fake certification, exact numbers, or strong before/after claims.

For beauty, wellness, massage, recovery, and personal-care products, prefer cautious language such as “helps”, “designed for”, “supports”, “feels”, “for everyday use”, or Chinese equivalents like “有助于”, “适合日常护理”, “使用感更清爽”.

## Default workflow

1. **Intake**: identify reference video, product image, optional person image, product name, target duration, language, and allowed/forbidden claims.
2. **Deconstruct reference**: identify first-frame hook, first 3 seconds micro-beats, shot rhythm, camera logic, caption cadence, emotional mechanism, and conversion structure.
3. **Map replacement**: map original pain/product/character/scene/claim to the user's product and safe benefits.
4. **Output compact execution plan**: use the default final output structure below. Avoid long analysis unless requested.

Ask a short follow-up only when a required input is missing. If benefits are unknown, infer only visible features and mark assumptions.

## Default final output structure

Use this structure unless the user asks otherwise:

1. **输入摘要**
   - reference video type/length/core mechanism
   - product name and category
   - product claim source grading: A级 / B级 / 禁止
2. **复刻策略摘要**
   - original structure
   - first 3 seconds replication focus
   - product replacement strategy
   - risk boundary
3. **前三秒专项拆解**
   - table columns: `时间 | 画面 | 镜头 | 字幕 | 作用`
   - use 0.5-1.0 second micro-beats when possible
4. **完整分镜**
   - for 15-20 seconds, default to 5-6 shots, not 8+ shots
   - table columns: `时间 | 画面 | 镜头/运动 | 屏幕字幕 | 旁白`
5. **全片统一约束**
   - aspect ratio, style, character, product consistency, color palette, forbidden elements
6. **全局提示词**
   - one clean global prompt for video models
7. **逐镜头提示词**
   - each shot uses `Scene / Subject / Camera / Constraints`
8. **执行顺序**
   - generate the hook first, then product hero, then middle use/demo shots, then captions/voiceover

## Per-shot prompt format

Use English prompts for model compatibility, with Chinese headings if useful.

```markdown
## SHOT 01 | 0:00-0:03
Scene: clean green-toned bathroom, soft natural light, vertical 9:16.
Subject: a young adult lowers their head; mild visible product-relevant problem appears.
Camera: top-down shot, fast push-in from wider view to close-up within 3 seconds.
Constraints: use @参考视频 for rhythm only; do not copy original character, watermark, music, brand, or exact text. Use @产品图 only when product appears. Leave clean space for captions; do not generate readable text in the video.
```

## Prompting rules

For each shot, include:
- vertical 9:16 and exact duration
- realism/style level
- product reference usage when the product appears: “use the provided product image as the exact product reference”
- character reference usage if `@人物图` exists
- scene, action, camera movement, lighting, and product visibility
- stability rules: product shape, color, label placement, main logo area, key visual identifiers
- forbidden elements: watermarks, copied identity, unreadable generated text, distorted product, random logos

If exact label text is unstable, prioritize product silhouette, main logo area, brand colors, packaging shape, and major visual markers rather than every small word.

## Quality checklist

Before finishing, verify:
- the first 3 seconds match the reference structure, pacing, camera logic, composition, and hook mechanism
- the answer is concise and execution-oriented, not a long essay
- the full storyboard avoids unnecessary duplicate rows and defaults to 5-6 shots for 15-20 seconds
- every claim is visible, user-provided, or safely generic
- the product image role is explicit and product identity constraints are stated
- no copied watermark, creator identity, original music, exact captions, protected character, or third-party brand trade dress appears
- prompts can be pasted into Kling, Seedance, HappyHorse, Wan, Doubao, or similar models without major rewriting

## Reference files

Consult only as needed:
- `references/input_template.md` for the recommended user input template and role binding rules
- `references/workflow.md` for the full replication workflow
- `references/output_templates.md` for the optimized final answer format
- `references/prompt_rules.md` for model-specific prompting and `@产品图` binding rules
- `references/shot_patterns.md` for common ecommerce viral structures
- `references/compliance.md` for safe transformation boundaries and claims guidance
