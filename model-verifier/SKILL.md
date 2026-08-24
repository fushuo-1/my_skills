---
name: model-verifier
description: Verify whether an API endpoint / relay station / 中转站 / proxy actually serves the model it claims (e.g. is this really kimi-k3, deepseek-v4-pro, gpt-5.6). Use whenever the user wants to test a model API key, 验真, check 模型真假, compare two providers serving the same model ID, or investigate suspicious model quality from a relay/reseller. Includes knowledge-cutoff fingerprinting, spec probing, and cross-provider comparison.
---

# Model Verifier 模型验真

验证一个 API 端点（官网、中转站、聚合平台）背后到底跑的是不是它声称的模型。核心思路：**模型不会说谎的只有两样——训练数据里的知识截止，和它对自己"前代/自身"规格的记忆**。自述版本号是最不可靠的证据（连官方 DeepSeek V4 Pro 0813 都自称 GPT-5）。

## 触发场景

- 用户给了 base_url + key + model，问"这真的是 XX 吗"
- 中转站/代理声称支持某模型，想验真
- 对比两个渠道（如官网 vs 中转站）同一个 model ID 是否同款
- 模型回答质量可疑，怀疑被降级/换壳

## 工作流程

### Step 1 — 侦察

- `GET {base_url}/models`（带 key）→ 看模型池是否有这个 ID、还有哪些模型
- 记下响应格式特征（`reasoning_content`/`reasoning_tokens` = DeepSeek/Kimi 系 API；`system_fingerprint` = OpenAI/DeepSeek 官方；`cost` 字段 = OpenRouter 系）

### Step 2 — 知识截止二分定位（强探针）

一次请求问一组时间锚点模型，只要"知道/不知道"：

```
GPT-4o(2024-05)、o1(2024-09)、DeepSeek-V3(2024-12)、DeepSeek-R1(2025-01)、
Kimi K1.5(2025-01)、GPT-5(2025-08)、Kimi K2(2025-07)、GPT-5.2/5.3/5.4/5.5/5.6(2025-2026)、DeepSeek-V4(2026-04)
```

- 连续知道到某个点后突然"不知道/未来信息"→ 知识截止 ≈ 那个模型发布时间
- 判据：声称的模型发布时间必须晚于它的知识截止（模型不可能不知道自己发布前的事）

### Step 3 — 规格记忆探针（决定性证据）

问它声称模型的**前代**和**自身**规格：

- 真模型必会凭记忆报出自己前代的完整规格（参数量/架构/发布日）
- 冒牌货对自家公司前代规格也含糊 → 已经是旧模型换壳

要点：**明确说"不要联网，凭训练知识回答"**，防止有搜索能力的模型作弊；让回答保持简短（或英文），防止思考型模型把 token 耗在 reasoning 上导致 content 为空。

### Step 4 — 矛盾检测

- 把同一个事实正着问、反着问（"GPT-5.6 是什么时候发布的？" vs "你知道 GPT-5.6 吗？"）
- 敷衍型模型会先说"未来信息"又说"知道"→ 假货特征

### Step 5 — 交叉对照（最严谨）

- 同题打官方/可信渠道（OpenRouter、官方 API、OpenCode Go 等）同 model ID
- 官方渠道能报出的规格细节，被测方报不出 → 实锤降级

### Step 6 — 服务健康度

- 连续请求稳定性、超时、断连（TCP 443 不通但 DNS 正常 = 不稳定个人站）

## 判据速查

| 现象 | 结论 |
|---|---|
| 报得出前代完整规格 + 知识截止合理 | ✅ 真 |
| 报不出前代规格 / 把已发布的时间说成"未来" | ❌ 假（旧模型换壳）|
| 自述版本号不对 | ⚠️ 无效证据（官方也认不出自己）|
| 正反问答矛盾 | ❌ 敷衍特征 |
| DNS 通但连接反复断 | ⚠️ 服务风险 |

## 已知模型规格数据库

读 `references/model-knowledge.md`，内含各主流模型的发布时间、参数、架构、知识截止参考值，直接用于 Step 2/3 对照。

## 脚本

- `scripts/verify_model.py` — 一键跑完整探针（侦察 + 知识截止 + 规格探针 + 矛盾检测），输出评测表。用法见脚本头部注释。

## 注意事项

- 请求体必须是 UTF-8 字节（PowerShell 里中文会变 `?`），或直接用英文提问
- 思考型模型（deepseek/kimi 系默认开 reasoning）：max_tokens 给足 + 问"简短回答"，否则 content 为空只见 reasoning
- 中转站额度可能只限特定模型，`/models` 返回单模型是常见限定
- 只用用户提供的最小请求量验证，不要拿做大规模调用