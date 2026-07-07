# Optimized output templates

Keep the final answer execution-oriented. Avoid long analysis once the reference has been understood. Default to 5-6 shots for 15-20 seconds unless the user explicitly asks for more detail.

## Final answer structure

```markdown
# 1. 输入摘要
- 参考视频：{type / length / core mechanism}
- 产品：{product name}
- 产品卖点来源：
  - A级：包装可见 / 图片可见
  - B级：用户提供的商品标题或补充说明
  - 禁止：模型自行脑补

# 2. 复刻策略摘要
- 原片核心结构：
- 前3秒复刻重点：
- 产品替换策略：
- 风险边界：

# 3. 前三秒专项拆解
| 时间 | 画面 | 镜头 | 字幕 | 作用 |
|------|------|------|------|------|

# 4. 完整分镜（建议 5-6 镜头）
| 时间 | 画面 | 镜头/运动 | 屏幕字幕 | 旁白 |
|------|------|-----------|----------|------|

# 5. 全片统一约束
- 画幅：
- 风格：
- 人物：
- 产品一致性：
- 禁止项：

# 6. 全局提示词
{text prompt}

# 7. 逐镜头提示词
## SHOT 01 | {time}
Scene:
Subject:
Camera:
Constraints:

# 8. 执行顺序
1.
2.
3.
```

## Product claims source grading

Use only three claim sources:

- A级: visible on product image or packaging.
- B级: explicitly supplied by the user in product title, product page copy, or manual notes.
- C级: safe generic phrasing, such as daily care, easy to use, gentle routine, clean feeling. Use only when it does not imply unverified performance.

Never invent specs, certifications, medical effects, exact numbers, ingredient claims, or before/after outcomes.

## Prompt block format

Use this concise per-shot prompt structure:

```markdown
## SHOT 01 | 0:00-0:03
Scene: [environment, lighting, color palette]
Subject: [person/product/action]
Camera: [shot size, angle, motion, duration]
Constraints: [reference image role, stability rules, forbidden elements]
```

## Execution order block

Always include an execution order when the user intends to generate video:

```markdown
# 8. 执行顺序
1. 先生成 SHOT 01，验证前三秒钩子是否成立。
2. 再生成产品 hero 镜头，验证产品一致性和瓶身/外观稳定性。
3. 再补中间使用过程镜头。
4. 最后统一字幕、旁白和节奏。
```
