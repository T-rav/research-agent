import os
import json
from typing import Optional, Dict, List
from pathlib import Path

class ResearchMemory:
    def __init__(self, topic: str):
        """Initialize research memory with JSON storage"""
        self.topic = topic
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
            "market_size": "",
            "key_players": "",
            "market_trends": "",
            "tech_findings": "",
            "summary": "",
            "detailed_report": ""
        }
    
    def _save_memory(self) -> None:
        """Save memory to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def save_market_size(self, content: str) -> None:
        """Save market size findings to memory"""
        self.memory["market_size"] = content
        self._save_memory()
    
    def save_key_players(self, content: str) -> None:
        """Save key players findings to memory"""
        self.memory["key_players"] = content
        self._save_memory()
    
    def save_market_trends(self, content: str) -> None:
        """Save market trends findings to memory"""
        self.memory["market_trends"] = content
        self._save_memory()
    
    def save_tech_findings(self, content: str) -> None:
        """Save technical findings to memory"""
        self.memory["tech_findings"] = content
        self._save_memory()
    
    def save_summary(self, summary: str, detailed_report: str) -> None:
        """Save summary and detailed report to memory"""
        self.memory["summary"] = summary
        self.memory["detailed_report"] = detailed_report
        self._save_memory()
    
    def get_market_size(self) -> str:
        """Get market size findings from memory"""
        return self.memory.get("market_size", "")
    
    def get_key_players(self) -> str:
        """Get key players findings from memory"""
        return self.memory.get("key_players", "")
    
    def get_market_trends(self) -> str:
        """Get market trends findings from memory"""
        return self.memory.get("market_trends", "")
    
    def get_tech_findings(self) -> str:
        """Get technical findings from memory"""
        return self.memory.get("tech_findings", "")
    
    def get_summary(self) -> str:
        """Get executive summary from memory"""
        return self.memory.get("summary", "")
    
    def get_detailed_report(self) -> str:
        """Get detailed report from memory"""
        return self.memory.get("detailed_report", "")
    
    def get_all_findings(self) -> Dict[str, str]:
        """Get all research findings"""
        return self.memory.copy()
