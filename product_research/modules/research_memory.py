import os
import json
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime

class ResearchMemory:
    """Manages research findings and maintains state between research phases."""
    
    def __init__(self, topic: str):
        """Initialize research memory with topic-specific file"""
        self.memory_dir = Path("research_memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / f"research_{topic.replace(' ', '_').lower()}.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from JSON file"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "market_size": None,
            "competitors": None,
            "trends": None,
            "technical": None,
            "summary": None,
            "_last_updated": {}  # Track when each section was last updated
        }
    
    def _save_memory(self) -> None:
        """Save memory to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def has_market_size_data(self) -> bool:
        """Check if market size data exists and is not empty"""
        return bool(self.memory.get("market_size"))
    
    def has_competitor_data(self) -> bool:
        """Check if competitor data exists and is not empty"""
        return bool(self.memory.get("competitors"))
    
    def has_trend_data(self) -> bool:
        """Check if trend data exists and is not empty"""
        return bool(self.memory.get("trends"))
    
    def has_technical_data(self) -> bool:
        """Check if technical data exists and is not empty"""
        return bool(self.memory.get("technical"))
    
    def has_summary(self) -> bool:
        """Check if summary exists and is not empty"""
        return bool(self.memory.get("summary"))
    
    def add_market_size_data(self, data: str):
        """Add market size research data if not already present."""
        if not self.has_market_size_data():
            self.memory["market_size"] = data
            self.memory["_last_updated"]["market_size"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_competitor_data(self, data: str):
        """Add competitor research data if not already present."""
        if not self.has_competitor_data():
            self.memory["competitors"] = data
            self.memory["_last_updated"]["competitors"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_trend_data(self, data: str):
        """Add market trend research data if not already present."""
        if not self.has_trend_data():
            self.memory["trends"] = data
            self.memory["_last_updated"]["trends"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_technical_data(self, data: str):
        """Add technical research data if not already present."""
        if not self.has_technical_data():
            self.memory["technical"] = data
            self.memory["_last_updated"]["technical"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_summary(self, summary: str):
        """Add summary if not already present."""
        if not self.has_summary():
            self.memory["summary"] = summary
            self.memory["_last_updated"]["summary"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def get_all_findings(self) -> dict:
        """Get all research findings."""
        findings = self.memory.copy()
        findings.pop("_last_updated", None)  # Remove metadata before returning
        return findings
    
    def get_last_updated(self, section: str) -> Optional[str]:
        """Get when a section was last updated."""
        return self.memory.get("_last_updated", {}).get(section)
