from modules import (
    create_agents,
    extract_findings,
    extract_summary
)
from modules.research_memory import ResearchMemory
from modules.report_generator import write_summary_to_file

async def run_product_research(topic: str):
    """
    Run product research on the given topic
    """
    print(f"Starting product research on topic: {topic}")
    
    # Create agents and research memory
    research_agent, user_proxy = create_agents()
    memory = ResearchMemory(topic)
    
    # Phase 1: Market Research
    print("\nPhase 1: Market Research")
    
    # Get market size data
    print("Researching market size...")
    query = f"""Search for market size information about {topic}.
        
        Use this exact query: "What is the current market size and growth rate of AI code generation and AI programming assistants? Include specific revenue numbers, growth rates, and market projections."
        
        Format your response with specific numbers and data points."""
    await user_proxy.a_initiate_chat(research_agent, message=query)
    market_size = extract_findings(user_proxy.chat_messages[research_agent])
    if not market_size:
        print("Warning: No market size data found")
    else:
        memory.save_market_size(market_size)
    
    # Get key players data
    print("Researching key players...")
    query = f"""Search for information about key players in {topic}.
        
        Use this exact query: "Who are the major companies and startups in AI code generation and AI programming tools? Include market share, revenue, funding, and notable products."
        
        Format your response with specific company details."""
    await user_proxy.a_initiate_chat(research_agent, message=query)
    key_players = extract_findings(user_proxy.chat_messages[research_agent])
    if not key_players:
        print("Warning: No key players data found")
    else:
        memory.save_key_players(key_players)

    # Get market trends
    print("Researching market trends...")
    query = f"""Search for market trends in {topic}.
        
        Use this exact query: "What are the latest market trends and developments in AI code generation and AI programming assistants? Include adoption rates, user statistics, and industry shifts."
        
        Format your response with specific trend analysis."""
    await user_proxy.a_initiate_chat(research_agent, message=query)
    market_trends = extract_findings(user_proxy.chat_messages[research_agent])
    if not market_trends:
        print("Warning: No market trends data found")
    else:
        memory.save_market_trends(market_trends)
    
    # Phase 2: Technical Research
    print("\nPhase 2: Technical Research")
    query = f"""Search for technical innovations in {topic}.
        
        Use this exact query: "What are the latest technical innovations and breakthroughs in AI code generation and programming AI? Include specific model architectures, performance metrics, and technical capabilities."
        
        Format your response with specific technical details."""
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
        summary_content,
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
