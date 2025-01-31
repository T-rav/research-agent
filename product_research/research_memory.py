import os
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class ResearchMemory:
    def __init__(self, topic: str):
        self.memory_dir = Path("research_memory")
        self.topic = topic
        
        # Create safe filename
        safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower()
        self.memory_file = self.memory_dir / f"{safe_filename}_memory.json"
        
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
        return {
            "market_size": "",
            "market_size_updated": "",
            "competitors": "",
            "competitors_updated": "",
            "trends": "",
            "trends_updated": "",
            "technical": "",
            "technical_updated": "",
            "summary": "",
            "summary_updated": "",
            "sources": {
                "market_size": [],
                "competitors": [],
                "trends": [],
                "technical": [],
                "summary": []
            }
        }
    
    def save(self) -> None:
        """Save memory to file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _update_timestamp(self, section: str) -> None:
        """Update timestamp for a section."""
        self.memory[f"{section}_updated"] = datetime.now().isoformat()
    
    def has_market_size_data(self) -> bool:
        """Check if market size data exists."""
        return bool(self.memory.get("market_size", ""))
    
    def has_competitor_data(self) -> bool:
        """Check if competitor data exists."""
        return bool(self.memory.get("competitors", ""))
    
    def has_trend_data(self) -> bool:
        """Check if trend data exists."""
        return bool(self.memory.get("trends", ""))
    
    def has_technical_data(self) -> bool:
        """Check if technical data exists."""
        return bool(self.memory.get("technical", ""))
    
    def has_summary(self) -> bool:
        """Check if summary exists."""
        return bool(self.memory.get("summary", ""))
    
    def get_last_updated(self, section: str) -> str:
        """Get when a section was last updated."""
        return self.memory.get(f"{section}_updated", "")
    
    def get_market_size(self) -> str:
        """Get market size data"""
        return self.memory.get("market_size", "")
    
    def get_competitors(self) -> str:
        """Get competitor data"""
        return self.memory.get("competitors", "")
    
    def get_trends(self) -> str:
        """Get trend data"""
        return self.memory.get("trends", "")
    
    def get_technical(self) -> str:
        """Get technical data"""
        return self.memory.get("technical", "")
    
    def get_summary(self) -> str:
        """Get summary"""
        return self.memory.get("summary", "")
    
    def add_market_size_data(self, data: str) -> None:
        """Add market size research data."""
        self.memory["market_size"] = data
        self._update_timestamp("market_size")
    
    def add_competitor_data(self, data: str) -> None:
        """Add competitor research data."""
        self.memory["competitors"] = data
        self._update_timestamp("competitors")
    
    def add_trend_data(self, data: str) -> None:
        """Add trend research data."""
        self.memory["trends"] = data
        self._update_timestamp("trends")
    
    def add_technical_data(self, data: str) -> None:
        """Add technical research data."""
        self.memory["technical"] = data
        self._update_timestamp("technical")
    
    def add_summary(self, summary: str) -> None:
        """Add summary."""
        self.memory["summary"] = summary
        self._update_timestamp("summary")
    
    def add_source(self, section: str, source: str) -> None:
        """Add a source to a section if not already present."""
        if source not in self.memory["sources"][section]:
            self.memory["sources"][section].append(source)
    
    def get_section_sources(self, section: str) -> List[str]:
        """Get sources for a specific section."""
        return self.memory["sources"].get(section, [])
    
    def get_all_sources(self) -> Dict[str, List[str]]:
        """Get all sources."""
        return self.memory["sources"]
    
    def format_source_for_report(self, source: str) -> str:
        """Format a source for the report."""
        return source
