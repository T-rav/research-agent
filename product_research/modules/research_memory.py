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
        seen_urls = set()  # Track unique URLs
        
        # URL patterns
        url_pattern = r'<(https?://[^>\s]+)>'  # URLs in angle brackets
        bare_url_pattern = r'(?<![<\w])(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+)(?![>\w])'  # URLs not in brackets
        
        # Extract URLs in angle brackets
        urls = re.findall(url_pattern, text)
        for url in urls:
            normalized_url = self._normalize_url(url)
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                sources.append({"type": "url", "url": url, "citation": None})
        
        # Extract bare URLs
        bare_urls = re.findall(bare_url_pattern, text)
        for url in bare_urls:
            normalized_url = self._normalize_url(url)
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                sources.append({"type": "url", "url": url, "citation": None})
        
        # Extract formatted citations with URLs
        citation_pattern = r'\[(\d+)\]\s+([^<\n]+)<(https?://[^>\s]+)>'
        citations = re.findall(citation_pattern, text, re.MULTILINE)
        for ref_num, citation_text, url in citations:
            normalized_url = self._normalize_url(url)
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
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
                source_id = f"{source_type}:{match}"
                if source_id not in seen_urls:  # Use same set for deduplication
                    seen_urls.add(source_id)
                    sources.append({
                        "type": source_type,
                        "id": match,
                        "citation": self._format_academic_citation(source_type, match)
                    })
        
        return sources

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication by removing common variations"""
        url = url.lower()
        url = re.sub(r'https?://(www\.)?', '', url)  # Remove protocol and www
        url = url.rstrip('/')  # Remove trailing slash
        url = re.sub(r'\?.*$', '', url)  # Remove query parameters
        return url

    def _format_academic_citation(self, source_type: str, identifier: str) -> str:
        """Format academic citations consistently"""
        if source_type == 'doi':
            return f"DOI: {identifier}"
        elif source_type == 'arxiv':
            return f"arXiv: {identifier}"
        elif source_type == 'report':
            return f"Market Report ({identifier})"
        elif source_type == 'patent':
            return f"Patent {identifier}"
        return identifier

    def add_sources(self, section: str, sources: List[Dict[str, str]]) -> None:
        """Add sources to a section with deduplication"""
        if section not in self.memory["sources"]:
            return
        
        existing_sources = {
            self._normalize_url(s.get("url", s.get("id", "")))
            for s in self.memory["sources"][section]
        }
        
        new_sources = []
        for source in sources:
            source_id = self._normalize_url(source.get("url", source.get("id", "")))
            if source_id not in existing_sources:
                existing_sources.add(source_id)
                new_sources.append(source)
        
        self.memory["sources"][section].extend(new_sources)
        self._save_memory()

    def format_source_for_report(self, source: Dict[str, str]) -> str:
        """Format a source for the report."""
        if source["type"] == "citation":
            return f"[{source['reference_number']}] {source['citation']} <{source['url']}>"
        elif source["type"] == "url":
            return f"<{source['url']}>"
        else:  # Academic citations
            return source["citation"]

    def get_sources_by_type(self, source_type: Optional[str] = None) -> List[Dict[str, str]]:
        """Get all sources of a specific type, or all sources if type is None"""
        all_sources = []
        for section_sources in self.memory["sources"].values():
            for source in section_sources:
                if source_type is None or source["type"] == source_type:
                    all_sources.append(source)
        return all_sources

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
