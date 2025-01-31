import os
import json
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime
import re

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
            "sources": {
                "market_size": [],
                "competitors": [],
                "trends": [],
                "technical": []
            },
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
    
    def extract_sources(self, text: str) -> List[Dict[str, str]]:
        """Extract URLs and citations from text."""
        sources = []
        
        # URL patterns
        url_pattern = r'<(https?://[^>\s]+)>'  # URLs in angle brackets
        bare_url_pattern = r'(?<![<\w])(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+)(?![>\w])'  # URLs not in brackets
        
        # Extract URLs in angle brackets
        urls = re.findall(url_pattern, text)
        sources.extend([{"type": "url", "url": url, "citation": None} for url in urls])
        
        # Extract bare URLs
        bare_urls = re.findall(bare_url_pattern, text)
        sources.extend([{"type": "url", "url": url, "citation": None} for url in bare_urls])
        
        # Extract formatted citations with URLs
        citation_pattern = r'\[(\d+)\]\s+([^<\n]+)<(https?://[^>\s]+)>'
        citations = re.findall(citation_pattern, text, re.MULTILINE)
        for ref_num, citation_text, url in citations:
            sources.append({
                "type": "citation",
                "url": url,
                "citation": citation_text.strip(),
                "reference_number": ref_num
            })
        
        # Academic citation patterns
        academic_patterns = [
            (r'doi:\s*(10\.\d{4,}/[-._;()/:\w]+)', 'doi'),  # DOI
            (r'arXiv:\s*(\d{4}\.\d{4,})', 'arxiv'),  # arXiv
            (r'(?:Gartner|Forrester|IDC|McKinsey|Deloitte|PwC|KPMG|EY)\s+(?:Report|Study|Analysis|Survey)[\s,]+(\d{4})', 'report'),  # Market reports
            (r'Patent\s+([A-Z]{2}\d+[A-Z]\d+)', 'patent')  # Patents
        ]
        
        for pattern, source_type in academic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                sources.append({
                    "type": source_type,
                    "identifier": match,
                    "citation": None
                })
        
        # Remove duplicates while preserving citation information
        unique_sources = {}
        for source in sources:
            key = source.get("url") or source.get("identifier")
            if key and (key not in unique_sources or source.get("citation")):
                unique_sources[key] = source
                
        return list(unique_sources.values())

    def format_source_for_report(self, source: Dict[str, str]) -> str:
        """Format a source for the report."""
        if source["type"] == "citation":
            return f"[{source['reference_number']}] {source['citation']} {source['url']}"
        elif source["type"] == "url":
            return source["url"]
        elif source["type"] == "doi":
            return f"DOI: {source['identifier']}"
        elif source["type"] == "arxiv":
            return f"arXiv: {source['identifier']}"
        elif source["type"] == "report":
            return f"Market Report ({source['identifier']})"
        elif source["type"] == "patent":
            return f"Patent {source['identifier']}"
        return str(source)
    
    def add_market_size_data(self, data: str):
        """Add market size research data if not already present."""
        if not self.has_market_size_data():
            self.memory["market_size"] = data
            self.memory["sources"]["market_size"] = self.extract_sources(data)
            self.memory["_last_updated"]["market_size"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_competitor_data(self, data: str):
        """Add competitor research data if not already present."""
        if not self.has_competitor_data():
            self.memory["competitors"] = data
            self.memory["sources"]["competitors"] = self.extract_sources(data)
            self.memory["_last_updated"]["competitors"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_trend_data(self, data: str):
        """Add market trend research data if not already present."""
        if not self.has_trend_data():
            self.memory["trends"] = data
            self.memory["sources"]["trends"] = self.extract_sources(data)
            self.memory["_last_updated"]["trends"] = str(datetime.now())
            self._save_memory()
            return True
        return False
    
    def add_technical_data(self, data: str):
        """Add technical research data if not already present."""
        if not self.has_technical_data():
            self.memory["technical"] = data
            self.memory["sources"]["technical"] = self.extract_sources(data)
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
        findings.pop("sources", None)  # Remove sources before returning
        return findings
    
    def get_last_updated(self, section: str) -> Optional[str]:
        """Get when a section was last updated."""
        return self.memory.get("_last_updated", {}).get(section)
    
    def get_all_sources(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all sources used in the research."""
        return self.memory.get("sources", {})
    
    def get_market_findings(self) -> str:
        """Get all market-related findings."""
        sections = []
        
        if self.memory.get("market_size"):
            sections.append("### Market Size\n" + self.memory["market_size"])
            
        if self.memory.get("competitors"):
            sections.append("### Competitive Landscape\n" + self.memory["competitors"])
            
        if self.memory.get("trends"):
            sections.append("### Market Trends\n" + self.memory["trends"])
            
        return "\n\n".join(sections) if sections else "No market findings available."
    
    def get_technical_findings(self) -> str:
        """Get all technical findings."""
        if self.memory.get("technical"):
            return self.memory["technical"]
        return "No technical findings available."
