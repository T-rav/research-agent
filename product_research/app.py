from modules import (
    create_agents,
    extract_findings,
    extract_summary,
    write_summary_to_file
)

async def run_product_research(topic: str):
    """
    Run product research on the given topic
    """
    print(f"Starting product research on topic: {topic}")
    
    # Create agents
    research_agent, user_proxy = create_agents()
    
    # Phase 1: Market Research
    print("\nPhase 1: Market Research")
    
    # Get market size data
    print("Researching market size...")
    await user_proxy.a_initiate_chat(
        research_agent,
        message=f"""Search for market size information about {topic}.
        
        Use this exact query: "What is the current market size and growth rate of AI code generation and AI programming assistants? Include specific revenue numbers, growth rates, and market projections."
        
        Format your response with specific numbers and data points."""
    )
    market_size = extract_findings(user_proxy.chat_messages[research_agent])
    if not market_size:
        print("Warning: No market size data found")
    
    # Get key players data
    print("Researching key players...")
    await user_proxy.a_initiate_chat(
        research_agent,
        message=f"""Search for information about key players in {topic}.
        
        Use this exact query: "Who are the major companies and startups in AI code generation and AI programming tools? Include market share, revenue, funding, and notable products."
        
        Format your response with specific company details."""
    )
    key_players = extract_findings(user_proxy.chat_messages[research_agent])
    if not key_players:
        print("Warning: No key players data found")

    # Get market trends
    print("Researching market trends...")
    await user_proxy.a_initiate_chat(
        research_agent,
        message=f"""Search for market trends in {topic}.
        
        Use this exact query: "What are the latest market trends and developments in AI code generation and AI programming assistants? Include adoption rates, user statistics, and industry shifts."
        
        Format your response with specific trend analysis."""
    )
    market_trends = extract_findings(user_proxy.chat_messages[research_agent])
    if not market_trends:
        print("Warning: No market trends data found")

    # Combine market research with proper formatting
    market_findings = ""
    if market_size:
        market_findings += f"# Market Size and Growth\n{market_size}\n\n"
    if key_players:
        market_findings += f"# Key Players and Companies\n{key_players}\n\n"
    if market_trends:
        market_findings += f"# Market Trends and Developments\n{market_trends}\n\n"
    
    # Phase 2: Technical Research
    print("\nPhase 2: Technical Research")
    await user_proxy.a_initiate_chat(
        research_agent,
        message=f"""Search for technical innovations in {topic}.
        
        Use this exact query: "What are the latest technical innovations and breakthroughs in AI code generation and programming AI? Include specific model architectures, performance metrics, and technical capabilities."
        
        Format your response with specific technical details."""
    )
    tech_findings = extract_findings(user_proxy.chat_messages[research_agent])
    if not tech_findings:
        print("Warning: No technical research data found")

    # Verify we have enough data to proceed
    if not any([market_size, key_players, market_trends, tech_findings]):
        print("\nError: No research data was collected. Please try again.")
        return

    # Combine all research with proper formatting
    research_data = f"""# Comprehensive Research Data: {topic}

## Market Research Findings
{market_findings if market_findings.strip() else "No market research data available."}

## Technical Research Findings
{tech_findings if tech_findings.strip() else "No technical research data available."}
"""

    print("\nGenerating executive summary...")
    await user_proxy.a_initiate_chat(
        research_agent,
        message=f"""Based on the research data below, create an executive summary for {topic}.
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
    )

    # Extract and verify summary
    summary_content = extract_summary(user_proxy.chat_messages[research_agent])
    if not summary_content:
        print("Error: Failed to generate summary")
        return

    # Write report
    print("\nWriting final report...")
    report_file = write_summary_to_file(
        summary_content,
        research_data,
        topic,
        market_findings,
        tech_findings
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
