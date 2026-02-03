---
name: deep-research
description: Perform comprehensive web research with multi-round exploration, data validation, cross-referencing, and structured output. Use when the user asks for latest news, financial reports, research studies, or requires data-driven analysis with citations.
---
# Deep Research Skill

## Overview

This skill provides a systematic, 6-step framework for conducting deep research on any topic. It combines automated tools with structured methodology to ensure research depth, data accuracy, and reliable output.

## When to Use

- User asks for latest news, market trends, or industry analysis
- User needs financial reports, research studies, or data-driven analysis
- User requires citations and verifiable sources for conclusions
- User wants comprehensive understanding of a complex topic
- User needs comparative analysis across multiple dimensions

## Goals

- **深度联网搜索**：针对用户问题进行多维度、多轮次检索，获取最新、最全面的信息
- **系统性研究**：采用6步标准流程，确保研究覆盖广度和深度
- **数据验证**：建立分级验证体系，确保数据可靠性和准确性
- **结构化输出**：生成专业研究报告，包含核心结论、深度分析、数据支撑和完整引用

## Execution Process

### Step 1: 问题拆解 (Problem Decomposition)

将复杂问题分解为可执行的子问题：

1. **识别核心问题** - 明确用户的核心查询目标
2. **分解子问题** - 将主问题拆分为 3-7 个子问题
3. **确定搜索维度** - 为每个子问题定义搜索关键词和角度
4. **优先级排序** - 按重要性和相关性排序子问题

**输出格式：**
```markdown
## 研究问题分解

### 核心问题
[用户原始问题]

### 子问题列表
1. [子问题1] - 优先级：高
2. [子问题2] - 优先级：中
3. [子问题3] - 优先级：中
...
```

### Step 2: 多源检索 (Multi-Source Search)

使用多种工具和关键词组合进行广泛搜索：

**工具组合：**
- `web-search-prime`：多维度网络搜索
- `zread_search_doc`：GitHub 代码仓库文档搜索
- `zread_get_repo_structure`：探索代码仓库结构
- `pdf-reader`：学术论文和报告分析

**搜索策略：**
1. 使用多个关键词组合（中英文双语）
2. 搜索不同时间范围的数据
3. 使用高级搜索语法（site:, filetype: 等）
4. 针对不同子问题执行独立搜索

### Step 3: 深度挖掘 (Deep Exploration)

针对关键发现进行二次深入搜索：

1. **识别关键点** - 从初步结果中识别需要深入的点
2. **扩展搜索** - 针对关键点进行更精确的搜索
3. **获取一手资料** - 查找原始数据源和官方文档
4. **追溯引用链** - 验证关键结论的原始来源

### Step 4: 交叉验证 (Cross-Validation)

对比多个来源的数据，建立分级验证体系：

**来源可靠性分级：**

| 等级 | 来源类型 | 说明 |
|------|----------|------|
| A | 官方机构 | 政府网站、国际组织、官方统计 |
| B | 权威媒体 | 主流媒体、知名财经媒体 |
| C | 专业平台 | 行业门户、专业数据平台 |
| D | 一般来源 | 博客、论坛、社交媒体 |

**验证流程：**
1. 对比至少 2-3 个来源的数据
2. 优先采用 A/B 级来源数据
3. 标注数据来源的可靠性等级
4. 记录数据差异和验证结果

### Step 5: 结构化加工 (Structured Processing)

将搜集到的信息进行系统化整理：

**加工任务：**
- 提炼关键量化指标
- 整理时间线和事件序列
- 建立对比维度表
- 识别数据趋势和模式
- 归纳核心观点
- 过滤无关信息

### Step 6: 输出呈现 (Output Presentation)

按照标准结构生成研究报告：

```markdown
# [研究主题]研究报告

## 研究概述
- 研究时间：[时间范围]
- 研究范围：[定义范围]
- 数据来源数量：[数量]

## 核心结论
[用 2-3 句话概括最重要的发现]

## 研究范围与边界
[定义研究范围和局限性]

## 深度分析
[详细解释数据含义、分析因果关系]

## 数据支撑表
| 指标 | 数值 | 时间 | 来源 | 可靠性 |
|------|------|------|------|--------|
| ...  | ...  | ...  | ...  | ...    |

## 质量评估
- 数据完整性：[评分]
- 来源可靠性：[评分]
- 时效性评估：[评分]

## 参考来源
1. [来源名称](链接) - 简要说明 [A/B/C/D]
```

## Output Constraints

### 客观性

- 严禁猜测或编造数据
- 若搜索不到准确数据，必须明确说明"未找到相关数据"
- 区分事实数据和预测数据
- 标注数据的不确定性

### 关联度

- 数据必须与问题直接相关
- 剔除无关信息
- 确保每个数据点都有明确用途

### 条理性

- 必须使用 Markdown 格式
- 重要数据点使用 **加粗** 显示
- 使用列表、表格、引用等格式增强可读性
- 保持逻辑清晰，层次分明

### 参考来源

- 列出所有参考来源
- 附上对应的链接，可直接跳转
- 在每个关键结论后通过数字角标（如 [1], [2]）标注信息来源
- 标注来源的可靠性等级（A/B/C/D）

## Best Practices

### 搜索策略

- 使用多个关键词组合搜索
- 搜索不同时间范围的数据
- 搜索中英文双语资料
- 使用高级搜索语法（site:, filetype: 等）
- 针对不同来源类型使用不同搜索策略

### 数据验证

- 优先使用 A/B 级来源
- 对比至少 3 个来源
- 注意数据发布时间
- 区分原始数据和衍生数据
- 记录数据冲突和处理方式

### 引用规范

```
示例：根据国家统计局数据，中国 GDP 增长率达到 5.2% [1]，高于市场预期的 5.0% [2]。

参考来源：
1. [国家统计局 - 2024年国民经济和社会发展统计公报](http://www.stats.gov.cn/) [A]
2. [财经网 - 2024年中国经济数据解读](https://www.caijing.com.cn/) [B]
```

### 错误处理

- 如果数据冲突，说明差异原因并采用高级别来源
- 如果数据过时，标注发布时间
- 如果来源不可靠，降低权重或不采用
- 如果无法验证，明确标注"待确认"

## Scripts

使用以下脚本支持研究任务：

- `scripts/research_manager.py`：研究任务管理和进度追踪
- `scripts/data_extractor.py`：从网页和PDF提取结构化数据
- `scripts/citation_manager.py`：引用来源管理和格式转换
- `scripts/report_generator.py`：Markdown报告生成和格式规范化

## References

### 搜索模板

使用 `references/search_templates.md` 获取：
- 行业特定搜索关键词模板
- 中英文双语搜索模式
- 高级搜索语法示例

### 数据验证规则

使用 `references/data_validation_rules.md` 获取：
- 数据验证规则
- 来源可靠性评估标准
- 数据冲突处理流程

### 输出模板

使用 `references/output_templates.md` 获取：
- 研究报告模板
- 数据表格格式
- 引用格式规范

### 行业研究指南

使用 `references/domain_guides/` 获取：
- 科技行业研究模板
- 金融行业研究模板
- 医疗行业研究模板

## Assets

### 模板库

使用 `assets/templates/` 获取：
- `research_report_template.md`：完整研究报告模板
- `data_summary_template.md`：数据摘要模板
- `comparison_template.md`：对比分析模板

### 样本库

使用 `assets/samples/` 获取：
- `sample_research_report.md`：研究报告样本
- `sample_data_analysis.md`：数据分析样本
- `sample_citation_format.md`：引用格式样本

## Examples

### Example 1: 行业分析

用户问题："2024 年中国新能源汽车市场表现如何？"

**执行步骤：**

1. 问题拆解
   - 子问题1：2024年新能源汽车销量数据
   - 子问题2：市场渗透率变化
   - 子问题3：主要厂商竞争格局
   - 子问题4：政策影响因素
   - 子问题5：未来发展趋势预测

2. 多源检索
   - 搜索：中汽协、乘联会、工信部数据
   - 搜索：比亚迪、特斯拉、蔚小理销量
   - 搜索：新能源汽车补贴政策变化

3. 深度挖掘
   - 获取中汽协2024年完整年度报告
   - 分析各厂商季度销量变化趋势
   - 追溯政策文件的原始来源

4. 交叉验证
   - 对比中汽协与乘联会数据差异
   - 标注各来源可靠性等级
   - 记录数据验证结果

5. 结构化加工
   - 整理销量时间序列数据
   - 建立市场份额对比表
   - 分析渗透率变化趋势

6. 输出呈现
   - 生成完整研究报告
   - 包含数据支撑表和引用

### Example 2: 技术趋势研究

用户问题："分析 2024-2025 年 AI 大模型技术发展趋势"

**执行步骤：**

1. 问题拆解
   - 子问题1：主要大模型发布时间线
   - 子问题2：技术能力评测对比
   - 子问题3：应用场景落地情况
   - 子问题4：算力需求和成本趋势
   - 子问题5：监管政策演变

2. 多源检索
   - 搜索：OpenAI、Google、Anthropic 最新动态
   - 搜索：Hugging Face、GitHub trending
   - 搜索：学术论文和技术报告

3. 深度挖掘
   - 获取各模型的技术论文
   - 分析基准测试结果
   - 研究算力成本数据

4. 交叉验证
   - 对比多个评测基准结果
   - 验证技术参数准确性
   - 评估信息来源可靠性

5. 结构化加工
   - 建立技术能力对比表
   - 整理发布时间线
   - 分析成本效益趋势

6. 输出呈现
   - 生成技术趋势研究报告

## Tools

### 核心工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| `web-search-prime` | 多维度网络搜索 | 高 |
| `web-reader` | 网页内容深度读取 | 高 |
| `mcp__zread__search_doc` | GitHub 文档搜索 | 中 |
| `mcp__zread__read_file` | 代码仓库文件读取 | 中 |
| `mcp__zread__get_repo_structure` | 仓库结构探索 | 中 |
| `mcp__pdf-reader` | PDF 文档分析 | 中 |

### 辅助工具

- `mcp__zai-mcp-server__analyze_image`：分析图表和可视化
- `mcp__zai-mcp-server__extract_text_from_screenshot`：从截图提取数据

## Quality Metrics

### 研究质量评估维度

1. **数据完整性** - 关键数据的覆盖程度
2. **来源可靠性** - 高等级来源的占比
3. **时效性** - 数据的更新时间和频率
4. **一致性** - 多源数据的吻合程度
5. **可验证性** - 每个结论的可追溯性

### 质量评分标准

| 评分 | 说明 |
|------|------|
| A | 完全满足质量标准，可作为权威参考 |
| B | 基本满足质量标准，个别数据需进一步验证 |
| C | 部分满足质量标准，需要谨慎使用 |
| D | 存在明显问题，不建议作为主要参考 |

## Notes

- 本 Skill 适用于需要深度和广度的系统性研究
- 对于简单事实查询，可简化流程
- 对于需要实时数据的问题，优先使用最新来源
- 保持中立客观，避免主观判断
- 始终标注数据的不确定性
