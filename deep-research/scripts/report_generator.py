"""
Deep Research Skill - 报告生成模块

提供Markdown报告生成和格式规范化功能。
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReportType(Enum):
    """报告类型"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    COMPARISON = "comparison"


class QualityScore(Enum):
    """质量评分"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    level: int  # 1-6 对应 markdown 的 # 到 ######
    content: str = ""
    subsections: List['ReportSection'] = field(default_factory=list)

    def to_markdown(self) -> str:
        prefix = "#" * self.level
        md = f"{prefix} {self.title}\n\n"
        if self.content:
            md += f"{self.content}\n\n"
        for sub in self.subsections:
            md += sub.to_markdown()
        return md


@dataclass
class ReportMetadata:
    """报告元数据"""
    title: str
    topic: str
    created_at: datetime = field(default_factory=datetime.now)
    research_period: str = ""
    scope: str = ""
    data_source_count: int = 0
    quality_score: Optional[QualityScore] = None
    author: str = "Deep Research Skill"
    version: str = "1.0"


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.sections: List[ReportSection] = []

    def create_header(self, metadata: ReportMetadata) -> str:
        """生成报告头部"""
        header = f"""# {metadata.title}

## 研究概述

| 项目 | 内容 |
|------|------|
| 研究主题 | {metadata.topic} |
| 研究时间 | {metadata.created_at.strftime('%Y-%m-%d %H:%M')} |
| 研究范围 | {metadata.scope or '未定义'} |
| 数据来源 | {metadata.data_source_count} 个 |
| 质量评分 | {metadata.quality_score.value if metadata.quality_score else '未评估'} |

---
"""
        return header

    def add_section(self, title: str, level: int, content: str = ""):
        """添加章节"""
        section = ReportSection(title=title, level=level, content=content)
        self.sections.append(section)
        return section

    def add_conclusion_section(self, conclusions: List[str]):
        """添加核心结论章节"""
        self.add_section("核心结论", 2)
        if self.sections[-1]:
            self.sections[-1].content = "\n".join(f"- {c}" for c in conclusions)

    def add_analysis_section(self, analysis: str):
        """添加深度分析章节"""
        self.add_section("深度分析", 2)
        if self.sections[-1]:
            self.sections[-1].content = analysis

    def add_data_table(self, headers: List[str], rows: List[List[str]], caption: str = ""):
        """添加数据表格"""
        table = f"\n**{caption}**\n\n"
        table += "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"
        table += "\n"

        # 找到最后一个 section 并添加表格
        if self.sections:
            self.sections[-1].content += table

    def add_reference_section(self, references: List[Dict[str, Any]]):
        """添加参考文献章节"""
        self.add_section("参考来源", 2)
        if self.sections[-1]:
            lines = []
            for ref in references:
                reliability = ref.get('reliability', 'C')
                lines.append(f"{ref['id']}. [{ref['source_name']}]({ref['url']}) - {ref['description']} [{reliability}]")
            self.sections[-1].content = "\n".join(lines)

    def add_quality_assessment(self, assessment: Dict[str, str]):
        """添加质量评估章节"""
        self.add_section("质量评估", 2)
        if self.sections[-1]:
            lines = ["| 评估维度 | 评分 |", "|---------|------|"]
            for dim, score in assessment.items():
                lines.append(f"| {dim} | {score} |")
            self.sections[-1].content = "\n".join(lines)

    def generate_report(
        self,
        metadata: ReportMetadata,
        conclusions: List[str] = None,
        analysis: str = "",
        data_tables: List[Dict[str, Any]] = None,
        references: List[Dict[str, Any]] = None,
        quality_assessment: Dict[str, str] = None
    ) -> str:
        """生成完整报告"""
        report = []

        # 头部
        report.append(self.create_header(metadata))

        # 核心结论
        if conclusions:
            self.add_conclusion_section(conclusions)

        # 深度分析
        if analysis:
            self.add_analysis_section(analysis)

        # 数据表格
        if data_tables:
            self.add_section("数据支撑", 2)
            for dt in data_tables:
                self.add_data_table(
                    dt.get('headers', []),
                    dt.get('rows', []),
                    dt.get('caption', '')
                )

        # 质量评估
        if quality_assessment:
            self.add_quality_assessment(quality_assessment)

        # 参考文献
        if references:
            self.add_reference_section(references)

        # 转换为Markdown
        for section in self.sections:
            report.append(section.to_markdown())

        return "\n".join(report)


class ReportFormatter:
    """报告格式化器"""

    @staticmethod
    def bold_text(text: str) -> str:
        """加粗文本"""
        return f"**{text}**"

    @staticmethod
    def italic_text(text: str) -> str:
        """斜体文本"""
        return f"*{text}*"

    @staticmethod
    def format_number(value: Any, precision: int = 2) -> str:
        """格式化数字"""
        if isinstance(value, float):
            return f"{value:.{precision}f}"
        return str(value)

    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """格式化百分比"""
        return f"{value:.{precision}f}%"

    @staticmethod
    def format_currency(value: Any, currency: str = "¥") -> str:
        """格式化货币"""
        if isinstance(value, (int, float)):
            return f"{currency}{value:,.0f}"
        return f"{currency}{value}"

    @staticmethod
    def highlight_key_points(text: str, key_points: List[str]) -> str:
        """高亮关键点"""
        for point in key_points:
            text = text.replace(point, f"**{point}**")
        return text

    @staticmethod
    def add_footnote(content: str, footnote_id: int) -> str:
        """添加脚注"""
        return f"{content}[^{footnote_id}]"

    @staticmethod
    def generate_table_of_contents(content: str) -> str:
        """生成目录"""
        toc = ["## 目录\n"]
        for line in content.split('\n'):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 3:  # 只显示到3级标题
                    title = line.lstrip('#').strip()
                    anchor = title.lower().replace(' ', '-').replace('，', '')
                    toc.append(f"{'  ' * (level - 1)}- [{title}](#{anchor})")
        return '\n'.join(toc)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """规范化空白字符"""
        # 规范化换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 规范化空格
        text = re.sub(r'[ \t]+', ' ', text)
        # 移除首尾空白
        text = text.strip()
        return text


# 便捷函数
def generate_research_report(
    topic: str,
    conclusions: List[str],
    analysis: str,
    data_sources: List[Dict[str, Any]],
    references: List[Dict[str, Any]] = None,
    scope: str = ""
) -> str:
    """生成研究报告"""
    generator = ReportGenerator()

    metadata = ReportMetadata(
        title=f"{topic}研究报告",
        topic=topic,
        scope=scope,
        data_source_count=len(data_sources)
    )

    # 数据表格处理
    data_tables = []
    for ds in data_sources:
        if ds.get('type') == 'table':
            data_tables.append({
                'headers': ds.get('headers', []),
                'rows': ds.get('rows', []),
                'caption': ds.get('caption', '')
            })

    return generator.generate_report(
        metadata=metadata,
        conclusions=conclusions,
        analysis=analysis,
        data_tables=data_tables,
        references=references
    )


def format_data_table(headers: List[str], data: List[Dict[str, Any]]) -> str:
    """格式化数据表格"""
    if not data:
        return ""

    if not headers:
        headers = list(data[0].keys())

    rows = []
    for item in data:
        rows.append([str(item.get(h, "")) for h in headers])

    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"

    return table


if __name__ == "__main__":
    # 测试代码
    metadata = ReportMetadata(
        title="2024年新能源汽车市场研究",
        topic="新能源汽车市场",
        scope="中国市场",
        data_source_count=5
    )

    conclusions = [
        "2024年新能源汽车销量突破700万辆",
        "市场渗透率达到35.2%",
        "比亚迪稳居市场领导地位"
    ]

    analysis = """
2024年，中国新能源汽车市场继续保持高速增长态势。在政策支持和消费升级的双重驱动下，行业实现了多项突破：

1. **销量增长**：全年销量达到 720 万辆，同比增长 82%
2. **渗透率提升**：新能源汽车渗透率从年初的 25% 提升至年末的 40%
3. **竞争格局**：市场集中度提高，头部企业优势明显

预计2025年，市场将继续保持增长，但增速可能放缓。
    """

    data_sources = [
        {
            'type': 'table',
            'headers': ['指标', '数值', '同比'],
            'rows': [['总销量', '720万辆', '+82%'], ['渗透率', '35.2%', '+10pp']],
            'caption': '关键销量指标'
        }
    ]

    references = [
        {'id': 1, 'source_name': '中汽协', 'url': 'http://www.caam.org.cn/', 'description': '官方销量数据', 'reliability': 'A'},
        {'id': 2, 'source_name': '乘联会', 'url': 'http://www.cpcaauto.com/', 'description': '市场分析报告', 'reliability': 'A'}
    ]

    report = generate_research_report(
        topic="2024年新能源汽车市场",
        conclusions=conclusions,
        analysis=analysis,
        data_sources=data_sources,
        references=references,
        scope="中国市场"
    )

    print(report)
