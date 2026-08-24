# 主流模型规格数据库（用于验真对照）

> 用途：模型验真时对照"前代规格"和"知识截止锚点"。数据来自公开报道/官方文档/第三方核实（metehan.ai 2026-06 等），使用时如与官方冲突以官方为准。
> 更新时间：2026-08-14

## Kimi 系列（Moonshot AI）

| 模型 | 发布时间 | 总参数 | 激活参数 | 架构要点 | 知识截止(参考) |
|---|---|---|---|---|---|
| Kimi K1.5 | 2025-01 | 32B 级 | - | 长思考 / 多模态 / RL | 2024 年末 |
| Kimi K2 | 2025-07-11 | 1.04T | 32B | MoE 384 专家、每 token 激活 8+1 共享、MLA 注意力、15.5T tokens 预训练、Muon+MuonClip 优化器 | 2025-04(核实) |
| Kimi K2.6 | 2026-04-20 | - | - | 多模态、256K 上下文、agent swarm | 2025-04 |
| Kimi K3 | 2026-07-16 | 2.8T | - | KDA 混合线性注意力(非 MLA!)、896 专家激活 16、20T tokens、Moon Clip 二阶优化器、1M 上下文、原生视觉；7-27 权重开源，arXiv 技术报告 2607.24653 | 未公布，推断 2025 末~2026 初 |

**验真要点**：真 kimi-k3 必能凭记忆报出 **K2 的规格**（384 专家 / 15.5T / Muon / 2025-07-11 发布 / 1.04T/32B）。K3 不知道自己叫 K3 是正常的（DeepSeek 0813 亦然），判据是前代规格 + 知识截止位置。

## DeepSeek 系列

| 模型 | 发布时间 | 关键规格 | 知识截止 |
|---|---|---|---|
| DeepSeek-V3 | 2024-12 | MoE 671B 总/37B 激活、MLA | - |
| DeepSeek-R1 | 2025-01 | 推理模型 | - |
| DeepSeek-V4-Flash (GA) | 2026-07-31 | - | - |
| DeepSeek-V4-Pro-0813 | 2026-08-13 | 1M 上下文、384K 输出、思考/非思考双模；指纹 `fp_v4pro_20260812_prod0820_fp8_kvcache_20260402` | 未公布 |

**验真要点**：官方 API 响应带 `system_fingerprint`（`v4pro_20260812`）；官方自称"DeepSeek-V4-Pro"是 0813 实锤。模型自述版本不可信（0813 自称 GPT-5）。

## OpenAI GPT-5.x 系

| 模型 | 发布时间 | 官方价($/M in/out) | OpenRouter 价 |
|---|---|---|---|
| GPT-5.6 Luna | 2026-07-09 首发，07-30 降价 80% | 0.20 / 1.20 | 0.10 / 0.60（5折）|
| GPT-5.6 Terra | 同上，降价 20% | 2.00 / 12.00 | 1.00 / 6.00（5折）|
| GPT-5.6 Sol | 同上，未降价 | 5.00 / 30.00 | 同官方价 |
| GPT-5.6 通用 | | 1M 上下文、128K 输出上限 | `-pro`/`:batch` 变体更便宜 |

**时间锚点**：GPT-4o(2024-05)、o1(2024-09)、GPT-5(2025-08)、GPT-5.2~5.5(2025-10~2026 H1)、GPT-5.6(2026-07) —— 用于知识截止二分。

## 其他锚点模型（知识截止二分用）

- GLM-4.6/5.x：2025-2026 系列
- Qwen2.5(2024-09) / Qwen3(2025-04) / Qwen3.5+ (2026)
- Claude 3.5 Sonnet(2024-06) / Claude Fable 5 / Opus 4.8
- Gemini 2.0(2024-12) / 3.x(2025-2026)
- MiniMax M2.7/M3：2026 初

## 渠道特征速查

| 特征字段 | 说明 |
|---|---|
| `system_fingerprint` | OpenAI / DeepSeek 官方直连特征（v4pro_20260812 可定位版本）|
| `reasoning_content` + `reasoning_tokens` | DeepSeek / Kimi 系思考模式特征 |
| `cost` 字段 | OpenRouter 系网关特征 |
| 无 fingerprint 且无 reasoning 字段 | 第三方代理剥壳常见 |

## 参考来源

- metehan.ai/articles/llm-knowledge-cutoff-dates（2026-06，逐模型核实 cutoff）
- Kimi 官方 platform.moonshot.ai / arXiv 2607.24653《Kimi K3: Open Frontier Intelligence》
- OpenAI developer 文档（模型定价页）
- OpenRouter /api/v1/models（实时价格）