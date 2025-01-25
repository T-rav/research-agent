import os
import json
from typing import Optional, Dict, List
from pathlib import Path

class ResearchMemory:
    """Manages research findings and maintains state between research phases."""
    
    def __init__(self):
        """Initialize research memory"""
        self.memory_dir = Path("research_memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / "research_memory.json"
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
            "summary": None
        }
    
    def _save_memory(self) -> None:
        """Save memory to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def add_market_size_data(self, data: str):
        """Add market size research data."""
        self.memory["market_size"] = data
        self._save_memory()
    
    def add_competitor_data(self, data: str):
        """Add competitor research data."""
        self.memory["competitors"] = data
        self._save_memory()
    
    def add_trend_data(self, data: str):
        """Add market trend research data."""
        self.memory["trends"] = data
        self._save_memory()
    
    def add_technical_data(self, data: str):
        """Add technical research data."""
        self.memory["technical"] = data
        self._save_memory()
    
    def add_summary(self, summary: str):
        """Add summary."""
        self.memory["summary"] = summary
        self._save_memory()
    
    def get_all_findings(self) -> dict:
        """Get all research findings."""
        return self.memory.copy()
