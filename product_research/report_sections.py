"""Report section definitions"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SectionConfig:
    """Configuration for a report section"""
    title: str
    description: str
    focus_points: List[str]
    depends_on: Optional[List[str]] = None

class ReportSection(Enum):
    """Available report sections"""
    MARKET_SIZE = "market_size"
    COMPETITORS = "competitors"
    TRENDS = "trends"
    TECHNICAL = "technical"
    SUMMARY = "summary"

    def __str__(self) -> str:
        return self.value

# Section configurations
SECTION_CONFIGS = {
    ReportSection.MARKET_SIZE: SectionConfig(
        title="Market Size and Growth",
        description="Analyze the total addressable market size, growth rates, and segmentation",
        focus_points=[
            "Current market value",
            "Growth rate and projections",
            "Key market segments",
            "Regional distribution"
        ]
    ),
    ReportSection.COMPETITORS: SectionConfig(
        title="Key Players and Companies",
        description="Analyze the competitive landscape and market positioning",
        focus_points=[
            "Key competitors and market share",
            "Competitor strengths/weaknesses",
            "Market positioning",
            "Competitive advantages"
        ]
    ),
    ReportSection.TRENDS: SectionConfig(
        title="Market Trends and Developments",
        description="Identify and analyze current and emerging market trends",
        focus_points=[
            "Current market trends",
            "Emerging technologies",
            "Consumer behavior shifts",
            "Future outlook"
        ]
    ),
    ReportSection.TECHNICAL: SectionConfig(
        title="Technical Analysis",
        description="Analyze technical aspects and implementation considerations",
        focus_points=[
            "Implementation considerations",
            "Architecture and design",
            "Technology stack",
            "Technical challenges"
        ]
    ),
    ReportSection.SUMMARY: SectionConfig(
        title="Executive Summary",
        description="Summarize key findings and recommendations",
        focus_points=[
            "Key findings from all sections",
            "Critical insights",
            "Main recommendations",
            "Next steps"
        ],
        depends_on=[
            ReportSection.MARKET_SIZE,
            ReportSection.COMPETITORS,
            ReportSection.TRENDS,
            ReportSection.TECHNICAL
        ]
    )
}

# Default order of sections
DEFAULT_SECTION_ORDER = [
    ReportSection.MARKET_SIZE,
    ReportSection.COMPETITORS,
    ReportSection.TRENDS,
    ReportSection.TECHNICAL,
    ReportSection.SUMMARY
]

def get_section_config(section: ReportSection) -> SectionConfig:
    """Get configuration for a section"""
    return SECTION_CONFIGS[section]

def get_research_prompt(section: ReportSection, topic: str) -> str:
    """Generate research prompt for a section"""
    config = get_section_config(section)
    points = "\n".join(f"{i+1}. {point}" for i, point in enumerate(config.focus_points))
    return f"""Research and analyze {config.title.lower()} for {topic}.
        
{config.description}

Focus on:
{points}

QA Reviewer will fact-check in real-time.
All team members collaborate to ensure accuracy and clarity.
End with TERMINATE when complete."""

def validate_section_order(sections: List[ReportSection]) -> bool:
    """Validate that sections are ordered correctly based on dependencies"""
    completed = set()
    for section in sections:
        config = get_section_config(section)
        if config.depends_on:
            if not all(dep in completed for dep in config.depends_on):
                return False
        completed.add(section)
    return True
