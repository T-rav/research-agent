import os
import json
from typing import Dict, List
import autogen
from modules.agents import create_agents
from modules.research_report import ResearchReport
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
    
    # Initialize report
    report = ResearchReport(topic)
    
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
        if not report.has_section('market_size'):
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
                report.set_market_size(market_size)
                print("✓ Market size research complete")
        else:
            print("\nSkipping market size research - data already exists")
            print(f"Last updated: {report.get_section_updated('market_size')}")

        # Key Players Research
        if not report.has_section('competitors'):
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
                report.set_competitors(key_players)
                print("✓ Competitor research complete")
        else:
            print("\nSkipping competitor research - data already exists")
            print(f"Last updated: {report.get_section_updated('competitors')}")

        # Market Trends Research
        if not report.has_section('trends'):
            print("\nResearching market trends and developments...")
            query = f"""Analyze current and emerging trends in {topic}:
                - Key market trends and developments
                - Emerging technologies and innovations
                - Consumer behavior and preferences
                - Regulatory landscape and compliance
                
                Focus on recent industry reports, news, and analyst insights."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            trends = extract_findings(results)
            if not trends:
                print("Warning: No trend data found")
            else:
                report.set_trends(trends)
                print("✓ Market trends research complete")
        else:
            print("\nSkipping trends research - data already exists")
            print(f"Last updated: {report.get_section_updated('trends')}")

        # Technical Research
        if not report.has_section('technical'):
            print("\nResearching technical aspects and implementation...")
            query = f"""Analyze the technical aspects of {topic}:
                - Core technologies and frameworks
                - Implementation challenges
                - Infrastructure requirements
                - Technical skills and expertise needed
                
                Focus on technical documentation, developer resources, and engineering blogs."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            tech_findings = extract_findings(results)
            if not tech_findings:
                print("Warning: No technical findings")
            else:
                report.set_technical_findings(tech_findings)
                print("✓ Technical research complete")
        else:
            print("\nSkipping technical research - data already exists")
            print(f"Last updated: {report.get_section_updated('technical')}")

        # Generate Executive Summary
        if not report.has_section('summary'):
            print("\nGenerating executive summary...")
            query = f"""Based on all research findings, provide:
                1. A concise executive summary
                2. Top 3 product opportunities with clear rationale
                
                Use all the collected research data to support your conclusions."""
            results = await run_team_research(query, user_proxy, research_lead, manager)
            summary = extract_summary(results)
            if not summary:
                print("Warning: Could not generate summary")
            else:
                report.set_summary(summary)
                print("✓ Executive summary complete")
        else:
            print("\nSkipping summary - already exists")
            print(f"Last updated: {report.get_section_updated('summary')}")

        print(f"\nResearch complete! Report saved to: {report.get_path()}")
        return report.get_path()

    except Exception as e:
        print(f"Error during research: {str(e)}")
        raise

async def run_team_research(query: str, user_proxy, research_lead, manager):
    """Run a research query through the multi-agent team."""
    try:
        await user_proxy.initiate_chat(
            research_lead,
            message=query
        )
        return user_proxy.last_message()
    except Exception as e:
        print(f"Error in team research: {str(e)}")
        return ""

if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python app.py 'research topic'")
        sys.exit(1)
    
    topic = sys.argv[1]
    asyncio.run(run_product_research(topic))
