"""
Deep Research Skill - 研究任务管理模块

提供研究任务管理、子问题生成和进度追踪功能。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import json


class Priority(Enum):
    """任务优先级枚举"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "待执行"
    IN_PROGRESS = "执行中"
    COMPLETED = "已完成"
    VERIFIED = "已验证"
    FAILED = "失败"


@dataclass
class SubQuestion:
    """子问题类"""
    id: int
    question: str
    priority: Priority
    status: TaskStatus = TaskStatus.PENDING
    keywords: List[str] = field(default_factory=list)
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "priority": self.priority.value,
            "status": self.status.value,
            "keywords": self.keywords,
            "search_results_count": len(self.search_results),
            "findings_count": len(self.findings),
            "notes": self.notes
        }


@dataclass
class ResearchTask:
    """研究任务类"""
    id: str
    original_question: str
    created_at: datetime = field(default_factory=datetime.now)
    sub_questions: List[SubQuestion] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    quality_score: Optional[str] = None

    def add_sub_question(self, question: str, priority: Priority, keywords: List[str] = None):
        """添加子问题"""
        sub_q = SubQuestion(
            id=len(self.sub_questions) + 1,
            question=question,
            priority=priority,
            keywords=keywords or []
        )
        self.sub_questions.append(sub_q)
        return sub_q

    def update_progress(self):
        """更新进度"""
        if not self.sub_questions:
            self.progress = 0.0
            return
        completed = sum(1 for sq in self.sub_questions if sq.status == TaskStatus.VERIFIED)
        self.progress = (completed / len(self.sub_questions)) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "original_question": self.original_question,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "progress": f"{self.progress:.1f}%",
            "sub_questions_count": len(self.sub_questions),
            "sub_questions": [sq.to_dict() for sq in self.sub_questions],
            "sources_count": len(self.sources),
            "conclusions_count": len(self.conclusions),
            "quality_score": self.quality_score
        }


class ResearchManager:
    """研究任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, ResearchTask] = {}

    def create_task(self, question: str) -> ResearchTask:
        """创建新研究任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = ResearchTask(id=task_id, original_question=question)
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[ResearchTask]:
        """获取研究任务"""
        return self.tasks.get(task_id)

    def decompose_question(self, question: str) -> ResearchTask:
        """分解问题为子问题"""
        task = self.create_task(question)

        # 默认分解模板
        default_sub_questions = [
            (f"关于「{question}」的核心定义和背景", Priority.HIGH, ["定义", "背景", "概念"]),
            (f"「{question}」的最新数据和统计", Priority.HIGH, ["数据", "统计", "最新"]),
            (f"「{question}」的主要参与者和机构", Priority.MEDIUM, ["参与者", "机构", "公司"]),
            (f"「{question}」的趋势和发展动态", Priority.HIGH, ["趋势", "发展", "动态"]),
            (f"「{question}」的挑战和问题", Priority.MEDIUM, ["挑战", "问题", "风险"]),
            (f"「{question}」的未来预测和展望", Priority.LOW, ["预测", "展望", "未来"]),
        ]

        for q, priority, keywords in default_sub_questions:
            task.add_sub_question(q, priority, keywords)

        return task

    def mark_sub_question_status(self, task_id: str, sub_q_id: int, status: TaskStatus):
        """更新子问题状态"""
        task = self.get_task(task_id)
        if task:
            for sq in task.sub_questions:
                if sq.id == sub_q_id:
                    sq.status = status
                    task.update_progress()
                    break

    def add_findings(self, task_id: str, sub_q_id: int, finding: str):
        """添加研究发现"""
        task = self.get_task(task_id)
        if task:
            for sq in task.sub_questions:
                if sq.id == sub_q_id:
                    sq.findings.append(finding)
                    break

    def add_source(self, task_id: str, source: Dict[str, Any]):
        """添加数据源"""
        task = self.get_task(task_id)
        if task:
            task.sources.append(source)

    def generate_report(self, task_id: str) -> Dict[str, Any]:
        """生成报告数据"""
        task = self.get_task(task_id)
        if not task:
            return {}

        return task.to_dict()

    def export_task(self, task_id: str, filepath: str = None):
        """导出任务为JSON"""
        task_data = self.generate_report(task_id)
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
        return task_data


# 便捷函数
def create_research_task(question: str) -> ResearchTask:
    """创建研究任务"""
    manager = ResearchManager()
    return manager.decompose_question(question)


def generate_sub_questions_template(question: str) -> str:
    """生成子问题模板"""
    manager = ResearchManager()
    task = manager.decompose_question(question)

    template = f"""## 研究问题分解

### 核心问题
{question}

### 子问题列表
"""
    for sq in task.sub_questions:
        template += f"- **{sq.question}** (优先级：{sq.priority.value})\n"
        template += f"  - 关键词：{', '.join(sq.keywords)}\n"

    return template


if __name__ == "__main__":
    # 测试代码
    task = create_research_task("2024年AI大模型发展趋势")
    print("研究任务已创建:")
    print(f"原始问题: {task.original_question}")
    print(f"子问题数量: {len(task.sub_questions)}")
    print("\n子问题列表:")
    for sq in task.sub_questions:
        print(f"  {sq.id}. {sq.question} ({sq.priority.value})")
