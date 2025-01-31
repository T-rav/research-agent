import os
import json
from typing import Dict
from datetime import datetime

class ResearchReport:
    def __init__(self, topic: str):
        self.topic = topic
        self.market_size = ""
        self.key_players = ""
        self.market_trends = ""
        self.tech_findings = ""
        self.summary = ""
        self.detailed_report = ""
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
            "market_size": self.market_size,
            "key_players": self.key_players,
            "market_trends": self.market_trends,
            "tech_findings": self.tech_findings,
            "summary": self.summary,
            "detailed_report": self.detailed_report,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "version": self.version
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load report from dictionary"""
        self.topic = data.get("topic", self.topic)
        self.market_size = data.get("market_size", "")
        self.key_players = data.get("key_players", "")
        self.market_trends = data.get("market_trends", "")
        self.tech_findings = data.get("tech_findings", "")
        self.summary = data.get("summary", "")
        self.detailed_report = data.get("detailed_report", "")
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.last_updated = data.get("last_updated", self.created_at)
        self.version = data.get("version", "1.0.0")
    
    def save(self) -> None:
        """Save report data to JSON file"""
        self._update_metadata()
        with open(self.json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        self._write_markdown()
    
    def load(self) -> None:
        """Load report data from JSON file if it exists"""
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                try:
                    data = json.load(f)
                    self.from_dict(data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not load data from {self.json_path}")
    
    def _write_markdown(self) -> None:
        """Write the report in markdown format"""
        # Combine market findings
        market_findings = ""
        if self.market_size:
            market_findings += f"# Market Size and Growth\n{self.market_size}\n\n"
        if self.key_players:
            market_findings += f"# Key Players and Companies\n{self.key_players}\n\n"
        if self.market_trends:
            market_findings += f"# Market Trends and Developments\n{self.market_trends}\n\n"
        
        # Format the complete report
        report_content = f"""# Product Research Report: {self.topic}

## Report Metadata
- Generated: {self.created_at}
- Last Updated: {self.last_updated}
- Version: {self.version}

## Executive Summary

{self.summary}

### Top 3 Product Opportunities
{self.detailed_report}

## Detailed Analysis

### Market Research Findings:
{market_findings}

### Technical Research Findings:
{self.tech_findings}
"""
        
        with open(self.report_path, 'w') as f:
            f.write(report_content)

    def _update_metadata(self) -> None:
        """Update metadata when changes are made"""
        self.last_updated = datetime.now().isoformat()
        # Increment patch version
        major, minor, patch = self.version.split('.')
        self.version = f"{major}.{minor}.{int(patch) + 1}"

    def update_market_size(self, content: str) -> None:
        """Update market size section and save"""
        self.market_size = content
        self.save()
    
    def update_key_players(self, content: str) -> None:
        """Update key players section and save"""
        self.key_players = content
        self.save()
    
    def update_market_trends(self, content: str) -> None:
        """Update market trends section and save"""
        self.market_trends = content
        self.save()
    
    def update_tech_findings(self, content: str) -> None:
        """Update technical findings section and save"""
        self.tech_findings = content
        self.save()
    
    def update_summary(self, summary: str, detailed_report: str) -> None:
        """Update summary and detailed report sections and save"""
        self.summary = summary
        self.detailed_report = detailed_report
        self.save()
    
    def get_report_path(self) -> str:
        """Get the path to the markdown report"""
        return self.report_path
