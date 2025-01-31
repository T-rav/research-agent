"""Main application module for product research"""
import asyncio
from typing import Dict, Any, Tuple, List

from .modules.research_director import ResearchDirector

async def run_product_research(topic: str) -> Tuple[str, List[str]]:
    """Run product research on a given topic
    
    Args:
        topic: The product/technology to research
        
    Returns:
        Tuple of (report_path, List[warnings])
    """
    try:
        # Initialize director to coordinate research
        director = ResearchDirector()
        
        # Run full research process
        report_path, warnings = await director.research_full_topic(topic)
        
        print(f"\nResearch complete! Report saved to: {report_path}")
        return report_path, warnings
        
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
