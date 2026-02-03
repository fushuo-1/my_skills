"""
Deep Research Skill - 引用管理模块

提供引用来源管理、格式转换和重复检测功能。
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict


class SourceReliability(Enum):
    """来源可靠性分级"""
    A = "官方机构"  # 政府、国际组织
    B = "权威媒体"  # 主流媒体
    C = "专业平台"  # 行业门户
    D = "一般来源"  # 博客、论坛


@dataclass
class Citation:
    """引用类"""
    id: int
    source_name: str
    url: str
    description: str
    reliability: SourceReliability
    access_date: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    publication_date: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_name": self.source_name,
            "url": self.url,
            "description": self.description,
            "reliability": self.reliability.value,
            "access_date": self.access_date,
            "title": self.title,
            "authors": self.authors,
            "publication_date": self.publication_date,
            "metadata": self.metadata
        }

    def to_markdown(self) -> str:
        """生成Markdown格式"""
        return f"[{self.id}]. [{self.source_name}]({self.url}) - {self.description} [{self.reliability.value}]"

    def to_apa(self) -> str:
        """生成APA格式"""
        date_str = f"({self.publication_date})" if self.publication_date else "(n.d.)"
        author_str = ", ".join(self.authors) if self.authors else ""
        if author_str and not author_str.endswith("."):
            author_str += "."

        return f"{author_str} {date_str}. {self.title}. {self.source_name}. {self.url}"


@dataclass
class ReferenceEntry:
    """参考文献条目"""
    id: int
    content: str  # 原文引用内容
    citations: List[int] = field(default_factory=list)  # 引用的来源ID
    page_number: Optional[str] = None
    quote: bool = False
    paraphrase: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "citations": self.citations,
            "page_number": self.page_number,
            "quote": self.quote,
            "paraphrase": self.paraphrase
        }


class CitationManager:
    """引用管理器"""

    def __init__(self):
        self.citations: Dict[int, Citation] = {}
        self.next_id: int = 1
        self.references: List[ReferenceEntry] = []

    def add_source(
        self,
        source_name: str,
        url: str,
        description: str,
        reliability: SourceReliability,
        title: str = "",
        authors: List[str] = None,
        publication_date: str = ""
    ) -> Citation:
        """添加引用来源"""
        citation = Citation(
            id=self.next_id,
            source_name=source_name,
            url=url,
            description=description,
            reliability=reliability,
            title=title,
            authors=authors or [],
            publication_date=publication_date,
            access_date=datetime.now().strftime("%Y-%m-%d")
        )
        self.citations[self.next_id] = citation
        self.next_id += 1
        return citation

    def get_citation(self, citation_id: int) -> Optional[Citation]:
        """获取引用"""
        return self.citations.get(citation_id)

    def add_reference(self, content: str, citation_ids: List[int] = None) -> ReferenceEntry:
        """添加参考文献条目"""
        entry = ReferenceEntry(
            id=len(self.references) + 1,
            content=content,
            citations=citation_ids or []
        )
        self.references.append(entry)
        return entry

    def check_duplicates(self, url: str) -> Optional[Citation]:
        """检查重复来源"""
        for citation in self.citations.values():
            if citation.url == url:
                return citation
        return None

    def merge_sources(self, primary_id: int, secondary_ids: List[int]):
        """合并重复来源"""
        primary = self.get_citation(primary_id)
        if not primary:
            return

        for sid in secondary_ids:
            secondary = self.get_citation(sid)
            if secondary:
                # 更新引用计数
                for ref in self.references:
                    if sid in ref.citations and primary_id not in ref.citations:
                        ref.citations.append(primary_id)
                # 移除重复的引用
                del self.citations[sid]

    def format_citations(self, citation_ids: List[int]) -> str:
        """格式化引用标记"""
        unique_ids = sorted(set(citation_ids))
        formatted = ", ".join(f"[{id}]" for id in unique_ids)
        return formatted

    def generate_reference_list(self) -> str:
        """生成参考文献列表"""
        lines = ["## 参考来源\n"]
        for citation in sorted(self.citations.values(), key=lambda x: x.id):
            lines.append(f"{citation.id}. {citation.to_markdown()}")
        return "\n".join(lines)

    def get_source_summary(self) -> Dict[str, int]:
        """获取来源统计"""
        summary = defaultdict(int)
        for citation in self.citations.values():
            summary[citation.reliability.value] += 1
        return dict(summary)

    def export_citations(self) -> List[Dict[str, Any]]:
        """导出所有引用"""
        return [c.to_dict() for c in sorted(self.citations.values(), key=lambda x: x.id)]


class CitationFormatter:
    """引用格式器"""

    @staticmethod
    def format_inline(citation_ids: List[int], style: str = "numeric") -> str:
        """格式化行内引用"""
        unique_ids = sorted(set(citation_ids))

        if style == "numeric":
            return f"[{', '.join(map(str, unique_ids))}]"
        elif style == "author_date":
            return f"({', '.join(map(str, unique_ids))})"
        else:
            return f"[{', '.join(map(str, unique_ids))}]"

    @staticmethod
    def parse_url(url: str) -> Dict[str, str]:
        """解析URL获取域名等信息"""
        pattern = r'https?://(?:www\.)?([^/]+)/?(.*)'
        match = re.match(pattern, url)
        if match:
            return {
                "domain": match.group(1),
                "path": match.group(2)[:50] if match.group(2) else ""
            }
        return {"domain": url, "path": ""}

    @staticmethod
    def infer_reliability(url: str) -> SourceReliability:
        """推断来源可靠性"""
        url_lower = url.lower()

        # 官方机构
        official_domains = [
            'gov.cn', 'who.int', 'un.org', 'worldbank.org',
            'stats.gov.cn', 'nbs.gov.cn', 'ccp.gov.cn'
        ]
        for domain in official_domains:
            if domain in url_lower:
                return SourceReliability.A

        # 权威媒体
        media_domains = [
            'reuters.com', 'bloomberg.com', 'ft.com', 'wsj.com',
            'nytimes.com', 'economist.com', 'caijing.com.cn',
            'sina.com.cn', 'ifeng.com', 'qq.com', '163.com'
        ]
        for domain in media_domains:
            if domain in url_lower:
                return SourceReliability.B

        # 专业平台
        professional_domains = [
            'huggingface.co', 'github.com', 'arxiv.org',
            '36kr.com', 'jiemian.com', 'thepaper.cn',
            'cls.cn', 'eastmoney.com', 'sse.com.cn', 'szse.cn'
        ]
        for domain in professional_domains:
            if domain in url_lower:
                return SourceReliability.C

        return SourceReliability.D


# 便捷函数
def create_citation(
    source_name: str,
    url: str,
    description: str,
    reliability: str = "C",
    title: str = "",
    authors: List[str] = None,
    publication_date: str = ""
) -> Citation:
    """创建引用"""
    reliability_map = {
        "A": SourceReliability.A,
        "B": SourceReliability.B,
        "C": SourceReliability.C,
        "D": SourceReliability.D
    }
    rel = reliability_map.get(reliability.upper(), SourceReliability.C)

    manager = CitationManager()
    return manager.add_source(
        source_name=source_name,
        url=url,
        description=description,
        reliability=rel,
        title=title,
        authors=authors,
        publication_date=publication_date
    )


def format_reference_list(citations: List[Dict[str, Any]]) -> str:
    """格式化参考文献列表"""
    lines = ["## 参考来源\n"]
    for c in citations:
        reliability = c.get('reliability', 'C')
        lines.append(f"{c['id']}. [{c['source_name']}]({c['url']}) - {c['description']} [{reliability}]")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    manager = CitationManager()

    # 添加来源
    c1 = manager.add_source(
        source_name="国家统计局",
        url="http://www.stats.gov.cn/",
        description="2024年国民经济和社会发展统计公报",
        reliability=SourceReliability.A,
        publication_date="2024-02-29"
    )

    c2 = manager.add_source(
        source_name="中国汽车工业协会",
        url="http://www.caam.org.cn/",
        description="2024年汽车产销数据",
        reliability=SourceReliability.A
    )

    c3 = manager.add_source(
        source_name="财经网",
        url="https://www.caijing.com.cn/",
        description="2024年新能源汽车市场分析",
        reliability=SourceReliability.B
    )

    print("=== 参考文献列表 ===")
    print(manager.generate_reference_list())

    print("\n=== 来源统计 ===")
    print(manager.get_source_summary())

    print("\n=== APA格式 ===")
    print(c1.to_apa())
