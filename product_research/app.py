from modules import (
    create_agents,
    extract_findings,
    extract_summary
)
from modules.research_memory import ResearchMemory
from modules.report_generator import write_summary_to_file
from datetime import datetime

async def run_product_research(topic: str):
    """
    Run product research on the given topic
    """
    print(f"Starting product research on topic: {topic}")
    
    # Get current year for queries
    current_year = datetime.now().year
    projection_year = current_year + 5
    
    # Create agents and research memory
    research_agent, user_proxy = create_agents()
    memory = ResearchMemory(topic)
    
    # Phase 1: Market Research
    print("\nPhase 1: Market Research")
    
    # Get market size data
    print("Researching market size...")
    if memory.get_market_size():
        print("Market size data already exists, skipping...")
    else:
        query = f"""Search for market size information about {topic}.
            
            Find current market size as of {current_year}, growth rate, and market projections through {projection_year}. Focus on:
            - Global and regional market size data
            - CAGR (Compound Annual Growth Rate)
            - Market segmentation by type and application
            - Key growth drivers and market dynamics
            
            Prioritize data from industry reports, market research firms, and financial analyses."""
        await user_proxy.a_initiate_chat(research_agent, message=query)
        market_size = extract_findings(user_proxy.chat_messages[research_agent])
        if not market_size:
            print("Warning: No market size data found")
        else:
            memory.save_market_size(market_size)
    
    # Get key players data
    print("Researching key players...")
    if memory.get_key_players():
        print("Key players data already exists, skipping...")
    else:
        query = f"""Search for information about key players in {topic}.
            
            Find major companies and startups in this field as of {current_year}. Include:
            - Market share and competitive positioning
            - Revenue data and financial performance
            - Recent funding rounds and investments
            - Product portfolio and technological capabilities
            - Strategic partnerships and acquisitions
            
            Focus on company reports, investor presentations, and industry analyses."""
        await user_proxy.a_initiate_chat(research_agent, message=query)
        key_players = extract_findings(user_proxy.chat_messages[research_agent])
        if not key_players:
            print("Warning: No key players data found")
        else:
            memory.save_key_players(key_players)

    # Get market trends
    print("Researching market trends...")
    if memory.get_market_trends():
        print("Market trends data already exists, skipping...")
    else:
        query = f"""Search for market trends in {topic}.
            
            Find the latest market trends and developments in {current_year}. Cover:
            - Current adoption rates and deployment statistics
            - Regional adoption patterns
            - Regulatory landscape and policy changes
            - Consumer/end-user preferences and feedback
            - Implementation challenges and solutions
            
            Use healthcare industry reports, regulatory documents, and market surveys."""
        await user_proxy.a_initiate_chat(research_agent, message=query)
        market_trends = extract_findings(user_proxy.chat_messages[research_agent])
        if not market_trends:
            print("Warning: No market trends data found")
        else:
            memory.save_market_trends(market_trends)
    
    # Phase 2: Technical Research
    print("\nPhase 2: Technical Research")
    if memory.get_tech_findings():
        print("Technical research data already exists, skipping...")
    else:
        query = f"""Search for technical innovations in {topic}.
            
            Find the latest technical innovations and breakthroughs as of {current_year}. Include:
            - Recent technological advancements
            - Performance benchmarks and comparisons
            - Safety and reliability metrics
            - Integration capabilities and standards
            - Patent and IP landscape
            
            Reference technical papers, patent databases, and product documentation."""
        await user_proxy.a_initiate_chat(research_agent, message=query)
        tech_findings = extract_findings(user_proxy.chat_messages[research_agent])
        if not tech_findings:
            print("Warning: No technical research data found")
        else:
            memory.save_tech_findings(tech_findings)

    # Verify we have enough data to proceed
    findings = memory.get_all_findings()
    if not any([findings["market_size"], findings["key_players"], 
                findings["market_trends"], findings["tech_findings"]]):
        print("\nError: No research data was collected. Please try again.")
        return

    # Combine all research with proper formatting
    market_findings = ""
    if findings["market_size"]:
        market_findings += f"# Market Size and Growth\n{findings['market_size']}\n\n"
    if findings["key_players"]:
        market_findings += f"# Key Players and Companies\n{findings['key_players']}\n\n"
    if findings["market_trends"]:
        market_findings += f"# Market Trends and Developments\n{findings['market_trends']}\n\n"

    research_data = f"""# Comprehensive Research Data: {topic}

## Market Research Findings
{market_findings if market_findings.strip() else "No market research data available."}

## Technical Research Findings
{findings["tech_findings"] if findings["tech_findings"].strip() else "No technical research data available."}
"""

    print("\nGenerating executive summary...")
    if memory.get_summary():
        print("Executive summary already exists, skipping...")
    else:
        query = f"""Based on the research data below, create an executive summary for {topic}.
            Use ONLY the information provided in the research data.
            
            {research_data}
            
            Format your response exactly like this:
            <SUMMARY>
            # Executive Summary
            [Write a concise overview based on the research data]

            # Key Findings
            [List 3-5 specific findings from the research data]
            - [Include specific numbers and facts]
            - [Include company names and market positions]
            - [Include technical capabilities and innovations]

            # Market Opportunities
            [List 2-3 specific opportunities from the research]
            - [Base these on actual market gaps or trends found]
            - [Include technical opportunities identified]

            # Recommendations
            [List 3-4 actionable recommendations]
            - [Base these on the research findings]
            - [Include specific technical or market-focused actions]
            SUMMARY_COMPLETE
            """
        await user_proxy.a_initiate_chat(research_agent, message=query)

        # Extract and verify summary
        summary_content = extract_summary(user_proxy.chat_messages[research_agent])
        if not summary_content:
            print("Error: Failed to generate summary")
            return

        # Save summary and generate final report
        memory.save_summary(summary_content, research_data)
    
    # Write markdown report
    print("\nWriting final report...")
    report_file = write_summary_to_file(
        memory.get_summary(),
        research_data,
        topic,
        market_findings,
        findings["tech_findings"]
    )
    print(f"\nReport has been written to: {report_file}")
    print("\nResearch complete!")

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Get topic from command line argument, or use default
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI agents for product research"
    print(f"Researching topic: {topic}")
    asyncio.run(run_product_research(topic))
