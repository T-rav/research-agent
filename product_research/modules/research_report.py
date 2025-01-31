import os
import json
from typing import Dict
from datetime import datetime
from .research_memory import ResearchMemory

class ResearchReport:
    def __init__(self, topic: str):
        self.topic = topic
        self.memory = ResearchMemory(topic)
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        self.version = "1.0.0"
        
        # Create safe filename
        safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower()
        
        # Setup paths
        os.makedirs("reports", exist_ok=True)
        self.json_path = f"reports/research_data_{safe_filename}.json"
        self.report_path = f"reports/product_research_report_{safe_filename}.md"
        
        # Load existing data if available
        self.load()
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization"""
        return {
            "topic": self.topic,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "version": self.version
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load report from dictionary"""
        self.topic = data.get("topic", self.topic)
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.last_updated = data.get("last_updated", self.created_at)
        self.version = data.get("version", "1.0.0")
    
    def _update_metadata(self) -> None:
        """Update metadata when changes are made"""
        self.last_updated = datetime.now().isoformat()
        # Increment patch version
        major, minor, patch = self.version.split('.')
        self.version = f"{major}.{minor}.{int(patch) + 1}"
    
    def save(self) -> None:
        """Save report metadata to JSON file"""
        self._update_metadata()
        with open(self.json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        self._write_markdown()
    
    def load(self) -> None:
        """Load report metadata from JSON file if it exists"""
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                try:
                    data = json.load(f)
                    self.from_dict(data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not load data from {self.json_path}")
    
    def _write_markdown(self) -> None:
        """Write the report in markdown format using data from memory"""
        # Get data from memory
        market_size = self.get_market_size_data()
        competitors = self.get_competitor_data()
        trends = self.get_trend_data()
        technical = self.get_technical_data()
        summary = self.get_summary()
        
        # Combine market findings
        market_findings = ""
        if market_size:
            market_findings += f"# Market Size and Growth\n{market_size}\n\n"
        if competitors:
            market_findings += f"# Key Players and Companies\n{competitors}\n\n"
        if trends:
            market_findings += f"# Market Trends and Developments\n{trends}\n\n"
        
        # Format the complete report
        report_content = f"""# Product Research Report: {self.topic}

## Report Metadata
- Generated: {self.created_at}
- Last Updated: {self.last_updated}
- Version: {self.version}

## Executive Summary

{summary}

## Detailed Analysis

### Market Research Findings:
{market_findings}

### Technical Research Findings:
{technical}

## Sources
"""
        # Add sources from memory
        sources = self.get_all_sources()
        for section, section_sources in sources.items():
            if section_sources:
                report_content += f"\n### {section.replace('_', ' ').title()}\n"
                for source in section_sources:
                    report_content += f"- {self.format_source_for_report(source)}\n"
        
        with open(self.report_path, 'w') as f:
            f.write(report_content)
    
    def update_market_size(self, content: str) -> None:
        """Update market size section and save"""
        self.add_market_size_data(content)
        self.save()
    
    def update_key_players(self, content: str) -> None:
        """Update key players section and save"""
        self.add_competitor_data(content)
        self.save()
    
    def update_market_trends(self, content: str) -> None:
        """Update market trends section and save"""
        self.add_trend_data(content)
        self.save()
    
    def update_tech_findings(self, content: str) -> None:
        """Update technical findings section and save"""
        self.add_technical_data(content)
        self.save()
    
    def update_summary(self, summary: str, detailed_report: str = "") -> None:
        """Update summary and save"""
        self.add_summary(summary)
        self.save()
    
    def get_report_path(self) -> str:
        """Get the path to the markdown report"""
        return self.report_path
    
    def has_market_size_data(self) -> bool:
        """Check if market size data exists"""
        return self.memory.has_market_size_data()
    
    def has_competitor_data(self) -> bool:
        """Check if competitor data exists"""
        return self.memory.has_competitor_data()
    
    def has_trend_data(self) -> bool:
        """Check if trend data exists"""
        return self.memory.has_trend_data()
    
    def has_technical_data(self) -> bool:
        """Check if technical data exists"""
        return self.memory.has_technical_data()
    
    def has_summary(self) -> bool:
        """Check if summary exists"""
        return self.memory.has_summary()
    
    def get_last_updated(self, section: str) -> str:
        """Get when a section was last updated"""
        return self.memory.get_last_updated(section)
    
    def get_market_size_data(self) -> str:
        """Get market size data"""
        return self.memory.get_market_size_data()
    
    def get_competitor_data(self) -> str:
        """Get competitor data"""
        return self.memory.get_competitor_data()
    
    def get_trend_data(self) -> str:
        """Get trend data"""
        return self.memory.get_trend_data()
    
    def get_technical_data(self) -> str:
        """Get technical data"""
        return self.memory.get_technical_data()
    
    def get_summary(self) -> str:
        """Get summary"""
        return self.memory.get_summary()
    
    def get_all_sources(self) -> Dict:
        """Get all sources"""
        return self.memory.get_all_sources()
    
    def add_market_size_data(self, content: str) -> None:
        """Add market size data"""
        self.memory.add_market_size_data(content)
    
    def add_competitor_data(self, content: str) -> None:
        """Add competitor data"""
        self.memory.add_competitor_data(content)
    
    def add_trend_data(self, content: str) -> None:
        """Add trend data"""
        self.memory.add_trend_data(content)
    
    def add_technical_data(self, content: str) -> None:
        """Add technical data"""
        self.memory.add_technical_data(content)
    
    def add_summary(self, summary: str) -> None:
        """Add summary"""
        self.memory.add_summary(summary)
    
    def format_source_for_report(self, source: str) -> str:
        """Format source for report"""
        return self.memory.format_source_for_report(source)
