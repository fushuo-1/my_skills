"""
Deep Research Skill - Scripts Package
"""

from .research_manager import ResearchManager, ResearchTask, SubQuestion, create_research_task, generate_sub_questions_template
from .data_extractor import DataExtractor, ExtractedData, Statistic, extract_all_data, extract_metrics_for_table
from .citation_manager import CitationManager, Citation, SourceReliability, CitationFormatter, create_citation
from .report_generator import ReportGenerator, ReportMetadata, ReportFormatter, generate_research_report, format_data_table

__all__ = [
    # Research Manager
    'ResearchManager',
    'ResearchTask',
    'SubQuestion',
    'create_research_task',
    'generate_sub_questions_template',

    # Data Extractor
    'DataExtractor',
    'ExtractedData',
    'Statistic',
    'extract_all_data',
    'extract_metrics_for_table',

    # Citation Manager
    'CitationManager',
    'Citation',
    'SourceReliability',
    'CitationFormatter',
    'create_citation',

    # Report Generator
    'ReportGenerator',
    'ReportMetadata',
    'ReportFormatter',
    'generate_research_report',
    'format_data_table',
]
