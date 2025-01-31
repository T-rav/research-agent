import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
from .research_memory import ResearchMemory
from .qa_agent import QAAgent

class ResearchReport:
    def __init__(self, topic: str):
        self.topic = topic
        self._memory = ResearchMemory(topic)  # Internal implementation detail
        self._qa_agent = QAAgent()  # QA agent for content validation
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
    
    async def _validate_content(self, section: str, content: str) -> Tuple[str, List[str]]:
        """
        Validate content with QA agent
        Returns: (validated_content, warnings)
        """
        is_valid, corrections, improvements = await self._qa_agent.validate_content(section, content)
        warnings = []
        
        if not is_valid:
            warnings.extend([f"Warning: {correction}" for correction in corrections])
            # Log improvements as suggestions
            warnings.extend([f"Suggestion: {improvement}" for improvement in improvements])
            
            print("\nContent validation results:")
            print("\nCorrections needed:")
            for correction in corrections:
                print(f"- {correction}")
            print("\nStyle improvements suggested:")
            for improvement in improvements:
                print(f"- {improvement}")
            
            # For now, we'll still save the content but with warnings
            # In the future, we might want to make this configurable
        
        return content, warnings
    
    def to_dict(self) -> Dict:
        """Convert report metadata to dictionary for JSON serialization"""
        return {
            "topic": self.topic,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "version": self.version
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load report metadata from dictionary"""
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
        """Save report metadata and memory state"""
        self._update_metadata()
        # Save report metadata
        with open(self.json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        # Save memory state
        self._memory.save()
        # Generate markdown
        self._write_markdown()
    
    def load(self) -> None:
        """Load report metadata if it exists"""
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                try:
                    data = json.load(f)
                    self.from_dict(data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not load data from {self.json_path}")
    
    def _write_markdown(self) -> None:
        """Generate markdown report from current data"""
        market_size = self.get_market_size()
        competitors = self.get_competitors()
        trends = self.get_trends()
        technical = self.get_technical_findings()
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
        # Add sources
        sources = self.get_sources()
        for section, section_sources in sources.items():
            if section_sources:
                report_content += f"\n### {section.replace('_', ' ').title()}\n"
                for source in section_sources:
                    report_content += f"- {self._format_source(source)}\n"
        
        with open(self.report_path, 'w') as f:
            f.write(report_content)
    
    def get_path(self) -> str:
        """Get the path to the generated markdown report"""
        return self.report_path
    
    def is_empty(self) -> bool:
        """Check if report has any content"""
        return not any([
            self.get_market_size(),
            self.get_competitors(),
            self.get_trends(),
            self.get_technical_findings(),
            self.get_summary()
        ])
    
    def has_section(self, section: str) -> bool:
        """Check if a section has content"""
        content = {
            'market_size': self.get_market_size,
            'competitors': self.get_competitors,
            'trends': self.get_trends,
            'technical': self.get_technical_findings,
            'summary': self.get_summary
        }.get(section, lambda: None)()
        return bool(content)
    
    def get_section_updated(self, section: str) -> str:
        """Get when a section was last updated"""
        return self._memory.get_last_updated(section)
    
    # Core report sections
    def get_market_size(self) -> str:
        """Get market size analysis"""
        return self._memory.get_market_size()
    
    def set_market_size(self, content: str) -> None:
        """Update market size analysis"""
        self._memory.add_market_size_data(content)
        self.save()
    
    def get_competitors(self) -> str:
        """Get competitor analysis"""
        return self._memory.get_competitors()
    
    def set_competitors(self, content: str) -> None:
        """Update competitor analysis"""
        self._memory.add_competitor_data(content)
        self.save()
    
    def get_trends(self) -> str:
        """Get market trends analysis"""
        return self._memory.get_trends()
    
    def set_trends(self, content: str) -> None:
        """Update market trends analysis"""
        self._memory.add_trend_data(content)
        self.save()
    
    def get_technical_findings(self) -> str:
        """Get technical analysis"""
        return self._memory.get_technical()
    
    def set_technical_findings(self, content: str) -> None:
        """Update technical analysis"""
        self._memory.add_technical_data(content)
        self.save()
    
    def get_summary(self) -> str:
        """Get executive summary"""
        return self._memory.get_summary()
    
    def set_summary(self, content: str) -> None:
        """Update executive summary"""
        self._memory.add_summary(content)
        self.save()
    
    def get_sources(self) -> Dict[str, List[str]]:
        """Get all sources used in the report"""
        return self._memory.get_all_sources()
    
    def _format_source(self, source: str) -> str:
        """Format a source for the report"""
        return self._memory.format_source_for_report(source)
