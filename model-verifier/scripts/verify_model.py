#!/usr/bin/env python3
"""
Model Verifier - 一键验证 API 端点背后是否真是指定模型
用法:
  python verify_model.py --base-url https://api.example.com/v1 --key sk-xxx --model kimi-k3
  python verify_model.py --base-url https://opencode.ai/zen/go/v1 --key sk-xxx --model kimi-k3 [--verbose]

流程: 侦察(/models) -> 知识截止二分 -> 规格探针 -> 矛盾检测 -> usage 指纹 -> 长上下文探针(可选) -> 汇总
依赖: 仅标准库 (Python 3.8+)
"""
import argparse
import json
import random
import sys
import urllib.request
import urllib.error

def api(base_url, key, model, messages, max_tokens=800):
    """调用 chat/completions，返回解析后的 JSON"""
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def ask(base_url, key, model, question, max_tokens=500):
    """问一个问题，返回 content 文本（处理思考型模型只出 reasoning 的情况）"""
    try:
        resp = api(base_url, key, model, [
            {"role": "user", "content": question + " Answer briefly, 2-3 sentences max."}
        ], max_tokens=max_tokens)
        msg = resp["choices"][0]["message"]
        return msg.get("content") or (msg.get("reasoning_content", "")[-200:] + " [only reasoning returned]")
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}] {e.read().decode('utf-8', 'ignore')[:200]}"
    except Exception as e:
        return f"[ERR] {e}"

def probe_models(base_url, key):
    """侦察模型池"""
    try:
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {key}",
                      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        return [m.get("id") for m in data.get("data", [])]
    except Exception as e:
        return f"[ERR] {e}"

def usage_check(base_url, key, model):
    """usage 后端指纹：检查 usage 字段是否有异源残留（换壳检测）"""
    try:
        resp = api(base_url, key, model, [{"role": "user", "content": "Say OK"}], max_tokens=20)
    except urllib.error.HTTPError as e:
        return {"error": f"[HTTP {e.code}] {e.read().decode('utf-8', 'ignore')[:200]}"}
    except Exception as e:
        return {"error": f"[ERR] {e}"}

    usage = resp.get("usage") or {}
    keys = list(usage.keys())
    flags = []
    lower_model = model.lower()

    # Anthropic 系命名（claude 换壳卖 GPT 的残留）
    if "input_tokens" in keys or "output_tokens" in keys:
        flags.append("Anthropic 命名 input_tokens/output_tokens")
    for k in keys:
        if "claude_cache" in k:
            flags.append(f"Anthropic 缓存字段 {k}")
    if str(usage.get("usage_source")).lower() == "anthropic":
        flags.append("usage_source=anthropic")

    # DeepSeek 系缓存字段：出现在 DeepSeek/Qwen 自身 = 正常；出现在其他模型 = 换壳
    if ("prompt_cache_hit_tokens" in keys or "prompt_cache_miss_tokens" in keys) \
            and not ("deepseek" in lower_model or "qwen" in lower_model or "v4" in lower_model):
        flags.append("DeepSeek/百炼系缓存字段 prompt_cache_*（目标非 DeepSeek 系）")

    # 公用字段算正常
    normal = {"prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens",
              "reasoning_tokens", "completion_tokens_details", "prompt_tokens_details",
              "prompt_cache_hit_tokens", "prompt_cache_miss_tokens", "cost", "weight"}
    unknown = [k for k in keys if k not in normal]
    return {"usage_keys": keys, "flags": flags, "unknown_keys": unknown}

def needle_probe(base_url, key, model, level):
    """needle-in-haystack 长上下文探针：在填充文本里埋入标记字符串，验证真实上下文窗口
    level: 1=32k, 2=100k, 3=200k（逐级，中段大海捞针）
    返回 (level_tokens, found_bool, note)
    """
    targets = {1: 32000, 2: 100000, 3: 200000}
    n = targets[level]
    needle = f"MAGIC-NEEDLE-{random.randint(100000, 999999)}"
    # 填充词：每条约 4 token 的句子，拼到 n token 左右（粗略按字符算）
    fill_line = "The quick brown fox jumps over the lazy dog near the river bank. "
    fill = (fill_line * ((n * 3 + len(fill_line) - 1) // len(fill_line)))[: n * 3]
    # 在中间插入 needle + 上下文线索
    mid = len(fill) // 2
    haystack = fill[:mid] + f"\n[{needle}] is the secret passphrase found in this text.\n" + fill[mid:]
    q = (f"Search the text below and report the secret passphrase exactly "
         f"(it is inside square brackets). Do NOT think step by step; answer with only "
         f"the passphrase, no other text.\n\n{haystack}")
    try:
        resp = api(base_url, key, model, [{"role": "user", "content": q}], max_tokens=1000)
        msg = resp["choices"][0]["message"]
        text = msg.get("content") or ""
        found = needle in text
        return (n, found, "ok" if found else "missed")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:200]
        if "context" in body.lower() or "length" in body.lower() or e.code in (400, 413, 422):
            return (n, False, f"拒绝/超限({e.code})")
        return (n, False, f"[HTTP {e.code}] {body}")
    except Exception as e:
        return (n, False, f"[ERR] {e}")

def main():
    p = argparse.ArgumentParser(description="Model Verifier 模型验真")
    p.add_argument("--base-url", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--extra-models", help="要一并侦察的其他模型 ID（逗号分隔）")
    p.add_argument("--long-context", action="store_true",
                   help="开启 needle-in-haystack 长上下文探针（32k→100k→200k，烧 token，默认关）")
    args = p.parse_args()

    print("=" * 60)
    print(f"目标: {args.model} @ {args.base_url}")
    print("=" * 60)

    # Step 1 侦察
    models = probe_models(args.base_url, args.key)
    if isinstance(models, list):
        print(f"\n[1/6] 模型池 ({len(models)} 个): {', '.join(models[:20])}")
        if len(models) == 1:
            print("      ⚠️ 仅 1 个模型——中转站常见限定")
    else:
        print(f"\n[1/4] 模型池: {models}")

    # Step 2 知识截止二分（时间锚点，从旧到新）
    print("\n[2/6] 知识截止二分（知道/不知道 时间锚点）...")
    anchors = [
        "GPT-4o", "OpenAI o1", "DeepSeek-V3", "DeepSeek-R1",
        "Kimi K1.5", "Kimi K2", "GPT-5", "GPT-5.2", "GPT-5.3",
        "GPT-5.4", "GPT-5.5", "GPT-5.6", "DeepSeek-V4",
    ]
    q = "只回答知道或不知道，每题一行，不要解释。\n" + "".join(f"{i+1}. 你知道 {m} 吗？\n" for i, m in enumerate(anchors))
    ans = ask(args.base_url, args.key, args.model, q, 600)
    print(ans)
    # 简单统计：连续 "知道" 数
    known = sum(1 for m in anchors if m.split()[0] in ans and "不知道" not in ans.split(f"{len(anchors)}.")[0])

    # Step 3 规格记忆探针
    print("\n[3/6] 规格探针（问它前代规格——真模型必会）...")
    spec_q = ("不要联网，凭训练知识回答，简短：{m} 的总参数量、激活参数、注意力机制、"
              "预训练数据量、发布时间分别是什么？如果不知道直接说不知道。")
    # 根据模型名猜前代（常见命名规则）
    lower = args.model.lower()
    if "kimi" in lower:
        probes = ["Kimi K2", "Kimi K1.5"]
    elif "deepseek" in lower:
        probes = ["DeepSeek-V3", "DeepSeek-R1"]
    elif "gpt" in lower:
        probes = ["GPT-5.3", "GPT-5"]
    elif "qwen" in lower:
        probes = ["Qwen3", "Qwen2.5"]
    elif "glm" in lower:
        probes = ["GLM-4.6", "GLM-4.5"]
    else:
        probes = [args.model]
    for m in probes:
        print(f"  --- 问: {m} 规格 ---")
        print("  " + ask(args.base_url, args.key, args.model, spec_q.format(m=m), 600).replace("\n", "\n  "))

    # Step 4 矛盾检测
    print("\n[4/6] 矛盾检测（正反两问对比）...")
    newest = anchors[-1]
    q1 = ask(args.base_url, args.key, args.model, f"{newest} 是什么时候发布的？", 300)
    q2 = ask(args.base_url, args.key, args.model, f"你知道 {newest} 吗？", 300)
    print(f"  正问「{newest} 何时发布」→ {q1[:100]}")
    print(f"  反问「知道 {newest} 吗」→ {q2[:100]}")
    contradiction = ("未来" in q1 or "尚未" in q1 or "不知道" in q1) and ("知道" in q2 and "不" not in q2[:4])
    if contradiction:
        print("  ⚠️ 正反问矛盾——敷衍特征，疑似假模型")

    print("\n[5/6] usage 后端指纹（换壳残留检测）...")
    u = usage_check(args.base_url, args.key, args.model)
    if "error" in u:
        print(f"  {u['error']}")
    else:
        print(f"  usage 字段: {u['usage_keys']}")
        if u["flags"]:
            print("  ⚠️ 异源残留: " + "；".join(u["flags"]))
            print("     → 后端疑似跑在别家模型上，critical 级疑点")
        elif u["unknown_keys"]:
            print(f"  ~ 非标准字段: {u['unknown_keys']}")
        else:
            print("  ✓ usage 字段无明显异源残留")

    # Step 6 长上下文探针（可选）
    if args.long_context:
        print("\n[6/6] needle-in-haystack 长上下文探针（烧 token）...")
        for lv in (1, 2, 3):
            n, found, note = needle_probe(args.base_url, args.key, args.model, lv)
            status = "✅ 找回" if found else ("❌ 失败" if "拒绝" not in note else "⚠️ " + note)
            print(f"  {n//1000}k tokens: {status} (note={note})")
            if not found and "拒绝" in note:
                break  # 上层超限，后面更大的也测不了
    else:
        print("\n[6/6] 长上下文探针：跳过（用 --long-context 开启）")

    print("\n" + "=" * 60)
    print("判读提示：")
    print("1. 报得出前代完整规格 + 知识截止合理 → 真")
    print("2. 前代规格含糊 / 已发布事件说成'未来' → 假（旧模型换壳）")
    print("3. 自述版本号不对 → 无效证据（官方模型也认不出自己）")
    print("4. usage 异源残留（Anthropic/DeepSeek 字段混入）→ 换壳实锤")
    print("5. needle 探针：小上下文能找回、大上下文失败 → 宣传窗口注水")
    print("=" * 60)

if __name__ == "__main__":
    main()