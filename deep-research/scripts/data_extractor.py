"""
Deep Research Skill - 数据提取模块

提供从网页和PDF中提取结构化数据的功能。
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


@dataclass
class ExtractedData:
    """提取的数据类"""
    content_type: str  # table, list, statistic, text, etc.
    raw_content: str
    structured_data: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    source_url: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_type": self.content_type,
            "raw_content": self.raw_content,
            "structured_data": self.structured_data,
            "confidence": self.confidence,
            "source_url": self.source_url,
            "extracted_at": self.extracted_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Statistic:
    """统计数据类"""
    name: str
    value: Any
    unit: str = ""
    period: str = ""
    source: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "period": self.period,
            "source": self.source,
            "confidence": self.confidence
        }


class DataExtractor:
    """数据提取器"""

    # 数字模式
    NUMBER_PATTERN = re.compile(
        r'([-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?\s*)'
    )

    # 百分比模式
    PERCENTAGE_PATTERN = re.compile(
        r'(\d+(?:\.\d+)?%)\s*(?:，|,|\.|的|是|为|达到|增长|下降)?'
    )

    # 表格行模式
    TABLE_ROW_PATTERN = re.compile(
        r'([^\|\n]+)\|([^\|\n]+)\|([^\|\n]+)\|?([^\|\n]*)?'
    )

    def __init__(self):
        self.extracted_data: List[ExtractedData] = []

    def extract_tables(self, content: str, source_url: str = "") -> List[ExtractedData]:
        """提取表格数据"""
        tables = []
        lines = content.split('\n')
        current_table = []

        for line in lines:
            if '|' in line:
                current_table.append(line)
            else:
                if current_table:
                    table_data = self._parse_table(current_table, source_url)
                    if table_data:
                        tables.append(table_data)
                    current_table = []

        if current_table:
            table_data = self._parse_table(current_table, source_url)
            if table_data:
                tables.append(table_data)

        self.extracted_data.extend(tables)
        return tables

    def _parse_table(self, table_lines: List[str], source_url: str) -> Optional[ExtractedData]:
        """解析表格"""
        if len(table_lines) < 2:
            return None

        # 解析表头
        headers = [h.strip() for h in table_lines[0].split('|') if h.strip()]

        # 解析数据行
        rows = []
        for line in table_lines[1:]:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and len(cells) >= len(headers):
                row_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        row_data[header] = cells[i]
                rows.append(row_data)

        if not rows:
            return None

        return ExtractedData(
            content_type="table",
            raw_content='\n'.join(table_lines),
            structured_data=rows,
            confidence=0.9 if len(rows) > 1 else 0.7,
            source_url=source_url,
            metadata={"headers": headers, "row_count": len(rows)}
        )

    def extract_statistics(self, content: str, source_url: str = "") -> List[Statistic]:
        """提取统计数据"""
        statistics = []

        # 提取百分比
        for match in self.PERCENTAGE_PATTERN.finditer(content):
            percentage = match.group(1)
            # 尝试获取上下文
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]

            stat = Statistic(
                name="",
                value=percentage,
                confidence=0.8
            )

            # 尝试从上下文中提取指标名称
            name_match = re.search(r'([^\s\d，,。]{2,10})(?:的|是|为|达到|' + re.escape(percentage) + r')', context)
            if name_match:
                stat.name = name_match.group(1).strip()

            statistics.append(stat)

        # 提取大数值
        for match in self.NUMBER_PATTERN.finditer(content):
            num_str = match.group(1).strip()
            if '%' in num_str:
                continue  # 跳过百分比

            try:
                # 转换数字
                num_value = float(num_str.replace(',', ''))
                if num_value >= 10000:  # 大于1万
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    # 确定单位
                    unit = ""
                    if '亿' in context[match.end():match.end()+10]:
                        unit = "亿元"
                    elif '万' in context[match.end():match.end()+10]:
                        unit = "万元"
                    elif '百万' in context[match.end():match.end()+10]:
                        unit = "百万"
                    elif '千万' in context[match.end():match.end()+10]:
                        unit = "千万"

                    # 尝试获取指标名称
                    name_match = re.search(r'([^\s\d，,。]{2,10})(?:的|是|为|达到|' + re.escape(num_str[:10]) + r')', context)
                    if name_match:
                        stat = Statistic(
                            name=name_match.group(1).strip(),
                            value=num_value,
                            unit=unit,
                            confidence=0.75
                        )
                        statistics.append(stat)
            except ValueError:
                continue

        return statistics

    def extract_key_metrics(self, content: str, metric_names: List[str], source_url: str = "") -> List[Dict[str, Any]]:
        """提取指定指标"""
        results = []

        for metric in metric_names:
            # 搜索指标
            pattern = rf'{metric}[^\n。]{{0,50}}?(\d+(?:\.\d+)?%?)'
            match = re.search(pattern, content)

            if match:
                results.append({
                    "metric": metric,
                    "value": match.group(1),
                    "position": match.start(),
                    "confidence": 0.85
                })

            # 也尝试反向搜索
            reverse_pattern = rf'(\d+(?:\.\d+)?%?)[^\n。]{{0,30}}?{metric}'
            reverse_match = re.search(reverse_pattern, content)
            if reverse_match:
                results.append({
                    "metric": metric,
                    "value": reverse_match.group(1),
                    "position": reverse_match.start(),
                    "confidence": 0.8
                })

        return results

    def extract_timeline(self, content: str, source_url: str = "") -> List[Dict[str, Any]]:
        """提取时间线事件"""
        events = []

        # 时间模式
        time_patterns = [
            r'(\d{4}年\d{1,2}月)',
            r'(\d{4}年)',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(Q[1-4]\s*\d{4})',
        ]

        for pattern in time_patterns:
            for match in re.finditer(pattern, content):
                # 获取上下文
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 70)
                context = content[start:end]

                # 提取事件描述
                event_match = re.search(rf'[{match.group(1)}][^\n。]{{0,60}}', context)
                if event_match:
                    events.append({
                        "date": match.group(1),
                        "description": event_match.group().strip(),
                        "position": match.start()
                    })

        # 按位置排序并去重
        events.sort(key=lambda x: x["position"])
        unique_events = []
        seen = set()
        for event in events:
            if event["date"] not in seen:
                seen.add(event["date"])
                unique_events.append(event)

        return unique_events

    def generate_data_table(self, data_list: List[Dict[str, Any]], columns: List[str] = None) -> str:
        """生成Markdown表格"""
        if not data_list:
            return ""

        if columns is None:
            columns = list(data_list[0].keys())

        # 生成表头
        header = "| " + " | ".join(columns) + " |\n"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"

        # 生成数据行
        rows = []
        for item in data_list:
            row = "| " + " | ".join(str(item.get(col, "")) for col in columns) + " |"
            rows.append(row)

        return header + separator + "\n".join(rows)


# 便捷函数
def extract_all_data(content: str, source_url: str = "") -> Dict[str, Any]:
    """提取所有类型的数据"""
    extractor = DataExtractor()

    tables = extractor.extract_tables(content, source_url)
    statistics = extractor.extract_statistics(content, source_url)

    return {
        "tables": [t.to_dict() for t in tables],
        "statistics": [s.to_dict() for s in statistics],
        "extracted_count": len(tables) + len(statistics)
    }


def extract_metrics_for_table(content: str, metrics: List[str], source_url: str = "") -> str:
    """提取指标并生成表格"""
    extractor = DataExtractor()
    results = extractor.extract_key_metrics(content, metrics, source_url)

    if not results:
        return "未找到相关指标"

    return extractor.generate_data_table(results, ["metric", "value", "confidence"])


if __name__ == "__main__":
    # 测试代码
    test_content = """
2024年中国新能源汽车市场表现亮眼。

销量数据：
| 月份 | 销量(万辆) | 同比增长 |
|------|-----------|---------|
| 1月 | 68.8 | 78% |
| 2月 | 52.5 | 65% |

关键指标：
- 市场渗透率达到 35.2%
- 总销量突破 700万辆
- 出口量达到 120万辆

重要事件：
2024年3月，新能源汽车下乡政策启动
2024年6月，电池技术取得突破
    """

    extractor = DataExtractor()
    tables = extractor.extract_tables(test_content)
    statistics = extractor.extract_statistics(test_content)
    timeline = extractor.extract_timeline(test_content)

    print("=== 提取的表格 ===")
    for t in tables:
        print(f"类型: {t.content_type}, 置信度: {t.confidence}")
        print(f"数据行数: {len(t.structured_data)}")
        print()

    print("=== 提取的统计 ===")
    for s in statistics:
        print(f"指标: {s.name}, 数值: {s.value}")

    print("\n=== 提取的时间线 ===")
    for e in timeline:
        print(f"{e['date']}: {e['description']}")
