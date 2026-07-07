# Storyboard and recreation output templates

Use these templates for analyze follow-up and recreate final answers. Default to 5-6 shots for 15-20 seconds.

## Analyze output (user-facing)

1. **Original script** — timestamped lines from `transcript.segments`
2. **Storyboard table**

| 时间 | 画面摘要 | 视觉动作 | 口播/字幕 |
|------|----------|----------|-----------|

3. **Video metrics** — duration and any available stats from `video.stats`
4. **Next steps** — numbered list, user replies with digit only:
   1. 改写为我的产品
   2. 输出 AI 可生成脚本
   3. 拆解转化逻辑

## Recreate output (8-section execution pack)

```markdown
# 1. 输入摘要
- 参考视频：
- 产品：
- 产品卖点来源：A级 / B级 / 禁止

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
- 画幅：9:16
- 风格：
- 人物：@人物图
- 产品一致性：@产品图
- 禁止项：

# 6. 全局提示词

# 7. 逐镜头提示词
## SHOT 01 | 0:00-0:03
Scene:
Subject:
Camera:
Constraints:

# 8. 执行顺序
1. 先生成 SHOT 01
2. 再生成产品 hero
3. 再补中间使用镜头
4. 最后统一字幕和旁白
```

## Per-shot prompt format

```markdown
## SHOT 01 | 0:00-0:03
Scene: [environment, lighting, color palette]
Subject: [person/product/action]
Camera: [shot size, angle, motion, duration]
Constraints: @参考视频 rhythm only; @产品图 for product; no watermark/music/copy
```

## Claims grading

- **A级**: visible on product image or packaging
- **B级**: user-provided title or notes
- **C级**: safe generic phrasing only
- **禁止**: invented specs, medical cure, guaranteed results, fake certification
