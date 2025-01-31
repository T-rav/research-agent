import os
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from report_sections import ReportSection

class ResearchMemory:
    def __init__(self, topic: str):
        self.memory_dir = Path("research_memory")
        self.topic = topic
        
        # Create safe filename
        safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower()
        
        # Store memory file in topic subdirectory
        self.memory_file = self.memory_dir / safe_filename / "memory.json"
        
        # Initialize or load memory
        self.memory = self._load_memory()
        
        # Save initial state if file didn't exist
        if not self.memory_file.exists():
            self.save()
    
    def _load_memory(self) -> Dict:
        """Load memory from file if it exists, otherwise initialize empty."""
        if not self.memory_dir.exists():
            self.memory_dir.mkdir(parents=True)
        
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not load memory from {self.memory_file}")
        
        # Initialize empty memory with timestamps
        return {str(section): "" for section in ReportSection} | {
            f"{str(section)}_updated": "" for section in ReportSection
        } | {"sources": {str(section): [] for section in ReportSection}}

    def save(self) -> None:
        """Save memory to file."""
        # Ensure directory exists
        if not self.memory_dir.exists():
            self.memory_dir.mkdir(parents=True)
        if not self.memory_file.parent.exists():
            self.memory_file.parent.mkdir(parents=True)
            
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _update_timestamp(self, section: ReportSection) -> None:
        """Update timestamp for a section."""
        self.memory[f"{str(section)}_updated"] = datetime.now().isoformat()
    
    def has_section(self, section: ReportSection) -> bool:
        """Check if a section has content"""
        return bool(self.memory.get(str(section), ""))
    
    def get_section(self, section: ReportSection) -> str:
        """Get content for a section"""
        return self.memory.get(str(section), "")
    
    def set_section(self, section: ReportSection, content: str) -> None:
        """Update content for a section"""
        self.memory[str(section)] = content
        self._update_timestamp(section)
        self.save()

    # Legacy methods for backward compatibility
    def has_market_size_data(self) -> bool:
        """Check if market size data exists."""
        return self.has_section(ReportSection.MARKET_SIZE)
    
    def has_competitor_data(self) -> bool:
        """Check if competitor data exists."""
        return self.has_section(ReportSection.COMPETITORS)
    
    def has_trend_data(self) -> bool:
        """Check if trend data exists."""
        return self.has_section(ReportSection.TRENDS)
    
    def has_technical_data(self) -> bool:
        """Check if technical data exists."""
        return self.has_section(ReportSection.TECHNICAL)
    
    def has_summary(self) -> bool:
        """Check if summary exists."""
        return self.has_section(ReportSection.SUMMARY)
    
    def get_market_size(self) -> str:
        """Get market size data"""
        return self.get_section(ReportSection.MARKET_SIZE)
    
    def get_competitors(self) -> str:
        """Get competitor data"""
        return self.get_section(ReportSection.COMPETITORS)
    
    def get_trends(self) -> str:
        """Get trend data"""
        return self.get_section(ReportSection.TRENDS)
    
    def get_technical(self) -> str:
        """Get technical data"""
        return self.get_section(ReportSection.TECHNICAL)
    
    def get_summary(self) -> str:
        """Get summary"""
        return self.get_section(ReportSection.SUMMARY)
    
    def add_market_size_data(self, data: str) -> None:
        """Add market size research data."""
        self.set_section(ReportSection.MARKET_SIZE, data)
    
    def add_competitor_data(self, data: str) -> None:
        """Add competitor research data."""
        self.set_section(ReportSection.COMPETITORS, data)
    
    def add_trend_data(self, data: str) -> None:
        """Add trend research data."""
        self.set_section(ReportSection.TRENDS, data)
    
    def add_technical_data(self, data: str) -> None:
        """Add technical research data."""
        self.set_section(ReportSection.TECHNICAL, data)
    
    def add_summary(self, summary: str) -> None:
        """Add summary."""
        self.set_section(ReportSection.SUMMARY, summary)
    
    def add_source(self, section: ReportSection, source: str) -> None:
        """Add a source to a section if not already present."""
        if source not in self.memory["sources"][str(section)]:
            self.memory["sources"][str(section)].append(source)
    
    def get_section_sources(self, section: ReportSection) -> List[str]:
        """Get sources for a specific section."""
        return self.memory["sources"].get(str(section), [])
    
    def get_all_sources(self) -> Dict[str, List[str]]:
        """Get all sources."""
        return self.memory["sources"]
    
    def get_last_updated(self, section: ReportSection) -> str:
        """Get when a section was last updated."""
        return self.memory.get(f"{str(section)}_updated", "")

    def format_source_for_report(self, source: str) -> str:
        """Format a source for the report."""
        return source
