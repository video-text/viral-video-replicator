# Standard input template

Use this template when the user wants a stable viral video recreation workflow.

## Full version

```text
请用 viral-video-replicator 处理。

@参考视频：已上传
@产品图：已上传
@人物图：无 / 已上传

产品名称：
产品品类：
目标市场：
目标语言：
目标时长：15-20 秒

允许卖点：
1.
2.
3.

禁止表达：
1. 不要写医疗治愈类承诺
2. 不要写保证有效
3. 不要写夸张前后对比
4. 不要复制原视频人物、品牌、水印、音乐和字幕原文

要求：
前三秒高精度复刻参考视频的钩子结构、镜头节奏、构图、机位、运动方式和字幕节奏。
后面根据产品重新设计成电商广告。
@参考视频 只作为结构参考，不复制原人物、品牌、水印、音乐和原字幕。
@产品图 是唯一产品视觉参考，必须保持产品外观稳定。

输出：
精简版，不要长篇分析。
只输出：输入摘要、复刻策略、前三秒拆解、完整分镜、统一约束、全局提示词、逐镜头提示词、执行顺序。
```

## Fast version

```text
请用 viral-video-replicator 复刻这个爆款视频。

@参考视频：已上传
@产品图：已上传
产品名称：
产品品类：
目标语言：
目标时长：15-20 秒

要求：前三秒高精度复刻原视频的镜头节奏、构图、机位、痛点放大和字幕节奏。后面根据我的产品重新设计成电商广告。产品必须以 @产品图 为唯一视觉参考。不要复制原视频人物、水印、音乐、品牌和字幕原文。不要写医疗治愈、保证有效、夸张功效。

输出：复刻策略摘要 + 前三秒拆解 + 完整分镜 + 全局提示词 + 逐镜头提示词。
```

## Role binding rules

Interpret user labels this way:

- `@参考视频`: structure reference only. Use it for hook rhythm, shot timing, camera angle, subtitle pacing, and emotional structure. Do not copy the original character, watermark, music, brand, exact subtitle text, or creator identity.
- `@产品图`: highest-priority visual product reference. Use it as the only source for product shape, color, packaging, logo placement, material, and recognizable identity.
- `@人物图`: optional character reference. Use only when uploaded and appropriate. Do not imply celebrity identity.

If the user writes only a product keyword such as `@产品 sebamed`, treat it as weak semantic guidance. Ask for or rely on a product image when product appearance accuracy matters.
