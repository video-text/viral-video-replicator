# Prompt rules for video models

## Product and media role binding

Use explicit role binding instead of relying only on product keywords.

Preferred wording:

```text
Use the provided product image as the exact product reference. Image A is the product image. The reference video defines rhythm, hook structure, camera logic, and subtitle pacing only; do not copy the original person, brand, watermark, music, or exact captions.
```

If the platform supports labels such as `@产品图`, `@参考视频`, or `@人物图`, keep them in the user-facing input, then translate them internally:

```json
{
  "reference_video": {
    "role": "structure_reference",
    "use_for": ["hook rhythm", "shot timing", "camera angle", "subtitle pacing", "emotional structure"],
    "do_not_copy": ["original character", "watermark", "music", "brand", "exact subtitle text"]
  },
  "product_image": {
    "role": "visual_product_reference",
    "priority": "highest",
    "must_preserve": ["product shape", "main logo", "main color", "label position", "recognizable packaging"]
  },
  "person_image": {
    "role": "optional_character_reference",
    "use_when_uploaded": true
  }
}
```

`@产品图` helps as an input marker, but it is not enough by itself. Always pair it with product name, visual constraints, allowed claims, and forbidden claims.

## Exact remix product/character decision

When the user asks for exact replication, first decide whether the uploaded product is visually consistent with the product in the reference video.

If product category, packaging silhouette, usage mode, or scene role do not match, preserve the reference character archetype and action logic more tightly. For example, a skeleton-mascot hair-loss reference should remain a generic skeleton-like mascot if the new product is a different shampoo/product category; do not suddenly switch to a realistic human unless the user requests a loose adaptation.

If the uploaded product is consistent with the reference product, the character can be lightly varied while keeping camera timing, pose rhythm, color palette, and caption cadence nearly identical.

Always avoid copying creator identity, watermark, exact proprietary character design, exact subtitles, music, or original brand marks.

## Universal prompt requirements

Every prompt should include:
- aspect ratio: vertical 9:16
- exact shot duration
- realism level: realistic, smartphone ugc, ecommerce ad, cinematic, or product demo
- reference usage: product image and character image when available
- product stability: shape, color, material, logo handling, placement
- camera: distance, angle, motion, cut style
- one clear action per shot
- text handling: leave space for captions; add readable subtitles in editing when possible
- negative prompt: distorted product, wrong logo, extra fingers, unreadable text, watermarks, copied brands

## Product identity lock

Use wording like:

```text
Use the provided product image as the exact product reference. Keep the product shape, proportions, color, surface material, cap/button layout, label placement, main logo area, and key visual identifiers consistent. Do not change it into another object. Do not add random logos or text.
```

If exact label text is unstable, tell the user to prioritize the silhouette, main logo area, brand colors, packaging shape, and major visual markers rather than every small word.

## Character reference lock

When a user provides a character/person image:

```text
Use the provided person image as the character reference for general face, hairstyle, age range, and clothing vibe. Preserve identity only if the uploaded image is the user's authorized reference. Avoid celebrity resemblance.
```

## Kling / Seedance style

Use concise, action-oriented prompts. One action and one camera move per shot.

Use model-native durations. Seedance 2.0 has a 4s minimum in this project: for a 3s reference hook, write the prompt as 4s with the first 3s matching the reference and the final second as an editing handle, or choose a 3s-capable Kling model.

```text
Vertical 9:16 realistic smartphone ecommerce video, 3 seconds. Use the product image as exact product reference. A young adult in a bright bathroom holds the device against the neck, soft pink led glow, gentle mirror reflection. Camera starts at medium shot and slowly pushes in. Natural morning light, clean ugc skincare routine style. Product remains clearly visible and stable.
```

Avoid overloading one clip with multiple scenes.

## HappyHorse high-detail style

Use denser prompts for precise shot recreation:

```text
Vertical 9:16, 2.5 seconds, high-detail realistic ecommerce ad. Handheld camera at eye level inside a busy warehouse aisle. Three generic adult workers reach toward stacked plain product boxes on a pallet, fast chaotic motion, slight camera shake, shallow background blur. The user's product packaging is visible on the top boxes, no real brand signage. The shot copies the urgency and crowd-rush structure of the reference while using original generic characters and a new product.
```

## Wan / Doubao style

Use simpler motion:
- one subject
- one product action
- clear product placement
- minimal camera moves
- generated still-start frames where product accuracy matters

## Text and subtitles

Video models often render text poorly. Prefer:
- describe blank space for captions
- add subtitle copy separately in the output
- use editing tools to burn captions later

Prompt wording:

```text
Leave clean negative space at the upper center for later caption overlay. Do not generate readable text inside the video.
```
