"""Main application module for product research"""
import sys
import os
import asyncio
from typing import Tuple, List
from research_director import ResearchDirector

async def run_product_research(topic: str):
    """Run product research
    
    Args:
        topic: The product/technology to research
    """
    try:
        # Create research director
        director = ResearchDirector()
        
        # Run research
        report_path, warnings = await director.research_full_topic(topic)
        
        # Print results
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"- {warning}")
                
        if report_path:
            print(f"\nResearch completed! Report saved to: {report_path}")
        else:
            print("\nNo report generated due to errors")
            
    except Exception as e:
        print(f"Error during research: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a topic to research")
        sys.exit(1)
        
    topic = sys.argv[1]
    asyncio.run(run_product_research(topic))
