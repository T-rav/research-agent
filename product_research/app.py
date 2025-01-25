import os
import json
from typing import Dict, List
import autogen
from modules.agents import create_agents
from modules.research_memory import ResearchMemory
from modules.report_generator import write_summary_to_file
from datetime import datetime

def extract_findings(content: str) -> str:
    """Extract research findings from agent response."""
    return content.strip() if content else ""

def extract_summary(content: str) -> str:
    """Extract summary from agent response."""
    if not content:
        return ""
    
    # Extract content between SUMMARY_START and SUMMARY_COMPLETE
    start_marker = "SUMMARY_START"
    end_marker = "SUMMARY_COMPLETE"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        return content.strip()
    
    summary = content[start_idx + len(start_marker):end_idx].strip()
    return summary

async def run_product_research(topic: str):
    """
    Run comprehensive product research on a given topic.
    """
    print(f"\nResearching topic: {topic}")
    
    # Initialize memory and report generator
    memory = ResearchMemory(topic)
    report_file = f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{topic.replace(' ', '_')}.md"
    
    try:
        # Create agents
        agents = create_agents()
        research_lead = agents["lead"]
        user_proxy = agents["proxy"]

        # Initialize group chat
        groupchat = autogen.GroupChat(
            agents=[
                agents["lead"],
                agents["analyst"], 
                agents["researcher"],
                agents["reviewer"],
                agents["proxy"]
            ],
            messages=[],
            max_round=12
        )
        
        # Create manager
        manager = autogen.GroupChatManager(groupchat=groupchat)
        
        # Market Size Research
        if not memory.has_market_size_data():
            print("\nResearching market size and opportunity...")
            query = f"""Research the market size and growth potential for {topic}:
                - Total addressable market (TAM)
                - Current market value and CAGR
                - Regional market breakdown
                - Key growth drivers and market dynamics
                
                Prioritize data from industry reports, market research firms, and financial analyses."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            market_size = extract_findings(results)
            if not market_size:
                print("Warning: No market size data found")
            else:
                memory.add_market_size_data(market_size)
                print("✓ Market size research complete")
        else:
            print("\nSkipping market size research - data already exists")
            print(f"Last updated: {memory.get_last_updated('market_size')}")

        # Key Players Research
        if not memory.has_competitor_data():
            print("\nResearching key players and competitive landscape...")
            query = f"""Analyze the competitive landscape for {topic}:
                - Market leaders and their market share
                - Key differentiators and value propositions
                - Business models and pricing strategies
                - Strategic partnerships and acquisitions
                
                Focus on company reports, investor presentations, and industry analyses."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            key_players = extract_findings(results)
            if not key_players:
                print("Warning: No key players data found")
            else:
                memory.add_competitor_data(key_players)
                print("✓ Competitor research complete")
        else:
            print("\nSkipping competitor research - data already exists")
            print(f"Last updated: {memory.get_last_updated('competitors')}")

        # Market Trends Research
        if not memory.has_trend_data():
            print("\nResearching market trends and dynamics...")
            query = f"""Identify key market trends and dynamics in {topic}:
                - Current and emerging trends
                - Customer needs and pain points
                - Regulatory environment and compliance
                - Implementation challenges and solutions
                
                Use healthcare industry reports, regulatory documents, and market surveys."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            market_trends = extract_findings(results)
            if not market_trends:
                print("Warning: No market trends data found")
            else:
                memory.add_trend_data(market_trends)
                print("✓ Market trends research complete")
        else:
            print("\nSkipping market trends research - data already exists")
            print(f"Last updated: {memory.get_last_updated('trends')}")

        # Technical Research
        if not memory.has_technical_data():
            print("\nConducting technical research...")
            query = f"""Analyze the technical aspects of {topic}:
                - Key technologies and platforms
                - Technical requirements and standards
                - Implementation considerations
                - Patent and IP landscape
                
                Reference technical papers, patent databases, and product documentation."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            tech_findings = extract_findings(results)
            if not tech_findings:
                print("Warning: No technical research data found")
            else:
                memory.add_technical_data(tech_findings)
                print("✓ Technical research complete")
        else:
            print("\nSkipping technical research - data already exists")
            print(f"Last updated: {memory.get_last_updated('technical')}")

        # Generate Summary
        if not memory.has_summary():
            print("\nGenerating comprehensive summary...")
            query = f"""Based on all research findings for {topic}, generate a comprehensive summary:

                MARKET OVERVIEW
                [Summarize market size, growth potential, and key dynamics]
                
                COMPETITIVE LANDSCAPE
                [Detail key players, market shares, and competitive advantages]
                
                MARKET TRENDS
                [List major trends, challenges, and opportunities]
                
                TECHNICAL ANALYSIS
                [Summarize key technical findings and considerations]
                
                RECOMMENDATIONS
                [Provide strategic recommendations]
                
                Format the response as:
                SUMMARY_START
                [Your comprehensive summary here, organized in sections]
                - [Include specific data points and metrics]
                - [Include specific technical or market-focused actions]
                SUMMARY_COMPLETE
                """
            results = await run_team_research(query, user_proxy, research_lead, manager)

            # Extract and verify summary
            summary_content = extract_summary(results)
            if not summary_content:
                print("Error: Failed to generate summary")
                return

            # Get findings from memory
            market_findings = memory.get_market_findings()
            technical_findings = memory.get_technical_findings()
            sources = memory.get_all_sources()

            # Write report and save to memory
            write_summary_to_file(
                topic=topic,
                market_findings=market_findings,
                technical_findings=technical_findings,
                summary_content=summary_content,
                report_file=report_file,
                sources=sources
            )
            memory.add_summary(summary_content)
            print("✓ Summary generation complete")
        else:
            print("\nSkipping summary generation - summary already exists")
            print(f"Last updated: {memory.get_last_updated('summary')}")

    except Exception as e:
        print(f"Error during research: {str(e)}")
        return

    print(f"\nReport has been written to: {report_file}")
    print("\nResearch complete!")

async def run_team_research(query: str, user_proxy, research_lead, manager) -> str:
    """Run a research query through the multi-agent team."""
    await user_proxy.a_initiate_chat(
        research_lead,
        message=f"""Please coordinate the research team to investigate: {query}
        
        Required steps:
        1. Break down research objectives
        2. Delegate specific tasks to team members
        3. Review and validate findings
        4. Synthesize final report
        
        END RESEARCH with 'TERMINATE' when complete.""",
        manager=manager
    )
    return research_lead.last_message()["content"]

if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) < 2:
        print("Please provide a research topic")
        sys.exit(1)
        
    topic = " ".join(sys.argv[1:])
    asyncio.run(run_product_research(topic))
