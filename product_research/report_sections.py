"""Report section definitions"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SectionConfig:
    """Configuration for a report section"""
    title: str
    description: str
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
        description="Total addressable market size, growth rates, and segmentation",
    ),
    ReportSection.COMPETITORS: SectionConfig(
        title="Key Players and Companies",
        description="Competitive landscape and market positioning",
    ),
    ReportSection.TRENDS: SectionConfig(
        title="Market Trends and Developments",
        description="Current and emerging market trends",
    ),
    ReportSection.TECHNICAL: SectionConfig(
        title="Technical Analysis",
        description="Technical aspects and implementation considerations",
    ),
    ReportSection.SUMMARY: SectionConfig(
        title="Executive Summary",
        description="Key findings and recommendations",
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
