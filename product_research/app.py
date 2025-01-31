"""Main application module for product research"""
import asyncio
from typing import Dict, Any, Tuple, List

from .modules.research_agent import ResearchAgent
from .modules.research_report import ResearchReport

async def run_product_research(topic: str) -> Tuple[ResearchReport, List[str]]:
    """Run product research on a given topic
    
    Args:
        topic: The product/technology to research
        
    Returns:
        Tuple of (ResearchReport, List[warnings])
    """
    report = ResearchReport(topic)
    warnings = []
    
    try:
        # Initialize research agent
        research_agent = ResearchAgent()
        
        # Research each section
        sections = ["market_size", "competitors", "trends", "technical", "summary"]
        for section in sections:
            content = await research_agent.research_topic(topic, section)
            
            # Save to appropriate section
            if section == "market_size":
                report.set_market_size(content)
            elif section == "competitors":
                report.set_competitors(content)
            elif section == "trends":
                report.set_trends(content)
            elif section == "technical":
                report.set_technical_findings(content)
            else:  # summary
                report.set_summary(content)
        
        print(f"\nResearch complete! Report saved to: {report.report_path}")
        return report, warnings
        
    except Exception as e:
        print(f"Error during research: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python app.py <topic>")
        sys.exit(1)
        
    topic = sys.argv[1]
    asyncio.run(run_product_research(topic))
