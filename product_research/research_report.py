import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
from research_memory import ResearchMemory
from report_sections import ReportSection, get_section_config

class ResearchReport:
    """Stores and formats research findings"""
    
    def __init__(self, topic: str):
        """Initialize research report
        
        Args:
            topic: Research topic
        """
        self.topic = topic
        self._memory = ResearchMemory(topic)
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        self.version = "1.0.0"
        
        # Create safe filename
        safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower()
        
        # Setup paths under research_memory
        self.json_path = f"research_memory/{safe_filename}/metadata.json"
        self.report_path = f"research_memory/{safe_filename}/report.md"
        
        # Create directory
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        
        # Load existing data if available, otherwise create empty files
        if os.path.exists(self.json_path):
            self.load()
        else:
            # Save initial empty state
            self.save()
            # Create empty markdown report
            self._write_markdown()

    def to_dict(self) -> Dict:
        """Convert report metadata to dictionary for JSON serialization"""
        return {
            "topic": self.topic,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "version": self.version,
            # Include section status from memory
            "sections": {
                str(section): self._memory.has_section(section)
                for section in ReportSection
            },
            "section_timestamps": {
                str(section): self._memory.get_last_updated(section)
                for section in ReportSection
            }
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
        # Save memory state
        self._memory.save()
        # Save report metadata
        with open(self.json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
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
        # Get section content
        sections_content = {
            section: self._memory.get_section(section)
            for section in ReportSection
        }
        
        # Format summary first (if exists)
        summary = ""
        config = get_section_config(ReportSection.SUMMARY)
        summary = f"# {config.title}\n"
        if sections_content[ReportSection.SUMMARY]:
            summary += f"{sections_content[ReportSection.SUMMARY]}\n\n"
        else:
            summary += "_No summary available yet._\n\n"
        
        # Format market research sections
        market_findings = ""
        # Market Size
        config = get_section_config(ReportSection.MARKET_SIZE)
        market_findings += f"# {config.title}\n"
        if sections_content[ReportSection.MARKET_SIZE]:
            market_findings += f"{sections_content[ReportSection.MARKET_SIZE]}\n\n"
        else:
            market_findings += "_No market size analysis available yet._\n\n"
            
        # Competitors
        config = get_section_config(ReportSection.COMPETITORS)
        market_findings += f"# {config.title}\n"
        if sections_content[ReportSection.COMPETITORS]:
            market_findings += f"{sections_content[ReportSection.COMPETITORS]}\n\n"
        else:
            market_findings += "_No competitor analysis available yet._\n\n"
            
        # Trends
        config = get_section_config(ReportSection.TRENDS)
        market_findings += f"# {config.title}\n"
        if sections_content[ReportSection.TRENDS]:
            market_findings += f"{sections_content[ReportSection.TRENDS]}\n\n"
        else:
            market_findings += "_No trend analysis available yet._\n\n"
        
        # Format technical findings
        technical_findings = ""
        config = get_section_config(ReportSection.TECHNICAL)
        technical_findings = f"# {config.title}\n"
        if sections_content[ReportSection.TECHNICAL]:
            technical_findings += f"{sections_content[ReportSection.TECHNICAL]}\n\n"
        else:
            technical_findings += "_No technical analysis available yet._\n\n"
        
        # Format sources
        sources = self.get_sources()
        sources_section = "# Sources\n\n"
        if any(sources.values()):
            for section in ReportSection:
                section_sources = sources[str(section)]
                if section_sources:
                    config = get_section_config(section)
                    sources_section += f"## {config.title}\n"
                    for source in section_sources:
                        sources_section += f"- {source}\n"
                    sources_section += "\n"
        else:
            sources_section += "_No sources available yet._\n\n"
        
        # Format metadata
        metadata = f"""---
Generated: {self.created_at}
Last Updated: {self.last_updated}
Version: {self.version}
---\n\n"""
        
        # Format the complete report
        report = f"""# Product Research Report: {self.topic}

{metadata}
{summary}
{market_findings}
{technical_findings}
{sources_section}"""
        
        # Write to file
        with open(self.report_path, 'w') as f:
            f.write(report)
    
    def get_path(self) -> str:
        """Get the path to the generated markdown report"""
        return self.report_path
    
    def is_empty(self) -> bool:
        """Check if report has any content"""
        return not any(self._memory.has_section(section) for section in ReportSection)
    
    def has_section(self, section: ReportSection) -> bool:
        """Check if a section has content"""
        return self._memory.has_section(section)
    
    def get_section_updated(self, section: ReportSection) -> str:
        """Get when a section was last updated"""
        return self._memory.get_last_updated(section)
    
    # Legacy methods for backward compatibility
    def get_market_size(self) -> str:
        """Get market size analysis"""
        return self._memory.get_market_size()
    
    def set_market_size(self, content: str):
        """Update market size analysis"""
        self._memory.add_market_size_data(content)
        self.save()
    
    def get_competitors(self) -> str:
        """Get competitor analysis"""
        return self._memory.get_competitors()
    
    def set_competitors(self, content: str):
        """Update competitor analysis"""
        self._memory.add_competitor_data(content)
        self.save()
    
    def get_trends(self) -> str:
        """Get market trends analysis"""
        return self._memory.get_trends()
    
    def set_trends(self, content: str):
        """Update market trends analysis"""
        self._memory.add_trend_data(content)
        self.save()
    
    def get_technical_findings(self) -> str:
        """Get technical analysis"""
        return self._memory.get_technical()
    
    def set_technical_findings(self, content: str):
        """Update technical analysis"""
        self._memory.add_technical_data(content)
        self.save()
    
    def get_summary(self) -> str:
        """Get executive summary"""
        return self._memory.get_summary()
    
    def set_summary(self, content: str):
        """Update executive summary"""
        self._memory.add_summary(content)
        self.save()
    
    def get_sources(self) -> Dict[str, List[str]]:
        """Get all sources"""
        return self._memory.get_all_sources()
