import os
import json
from typing import List, Dict
import autogen
from autogen import AssistantAgent, UserProxyAgent
import arxiv
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def perplexity_search(query: str, num_results: int = 2) -> str:
    """
    Search using Perplexity AI API via OpenAI client
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return "Error: Perplexity API key not found in environment variables"

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        
        print(f"Debug: Sending query to Perplexity API: {query}")
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful research assistant. Provide detailed, factual information with specific numbers and data when available."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            print(f"Debug: Got response: {result}")
            return result
        else:
            return "No results found"
            
    except Exception as e:
        print(f"Debug: Error in perplexity_search: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error in perplexity_search: {str(e)}"

def arxiv_search(query: str, max_results: int = 2) -> str:
    """
    Search Arxiv for papers and return the results including abstracts
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    formatted_results = []
    for paper in client.results(search):
        paper_info = (
            f"Title: {paper.title}\n"
            f"Authors: {', '.join(author.name for author in paper.authors)}\n"
            f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            f"Abstract: {paper.summary}\n"
            f"PDF URL: {paper.pdf_url}\n"
        )
        formatted_results.append(paper_info)

    if not formatted_results:
        return "No papers found matching the query."
        
    return "\n\n".join(formatted_results)

# Configure the OpenAI API
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview"],
    },
)

# Create agents
research_agent = AssistantAgent(
    name="Research_Agent",
    llm_config={
        "config_list": config_list,
        "temperature": 0.1,
        "functions": [{
            "name": "perplexity_search",
            "description": "Search using Perplexity AI",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 3}
                },
                "required": ["query"]
            }
        }]
    },
    system_message="""You are a research agent specializing in market and technical research.
    Your task is to:
    1. Call perplexity_search with the given query
    2. Analyze the search results
    3. Format the findings in a clear, structured way
    4. Include specific numbers, statistics, and quotes when available
    
    Always follow these steps:
    1. Call perplexity_search with the query
    2. Wait for the results
    3. Format the findings with the <FINDINGS> tag
    4. End with TERMINATE
    
    Example:
    Human: Research market size of X
    Assistant: I'll search for market size information.
    {
        "function": "perplexity_search",
        "arguments": {
            "query": "What is the current market size and growth rate of X industry? Include specific numbers and data"
        }
    }
    <FINDINGS>
    Based on the search results:
    
    Market Size:
    - Current value: $X billion (2023)
    - CAGR: X% (2023-2028)
    - Projected value: $X billion by 2028
    
    Key Statistics:
    - [Specific data point 1]
    - [Specific data point 2]
    TERMINATE
    """
)

# Create a user proxy agent
user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,
    llm_config={
        "config_list": config_list,
        "timeout": 120
    },
    function_map={
        "perplexity_search": perplexity_search,
        "arxiv_search": arxiv_search
    }
)

# Function to run the literature review
async def run_product_research(topic: str):
    """
    Run product research on the given topic
    """
    print(f"Starting product research on topic: {topic}")
    
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

def write_summary_to_file(summary: str, detailed_report: str, topic: str, market_findings: str, technical_findings: str):
    """
    Write a combined report with executive summary and detailed findings to a single markdown file
    """
    # Create a safe filename from the topic
    safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    
    filename = f"reports/product_research_report_{safe_filename}.md"
    
    # Ensure the reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    # Format the complete report
    report_content = f"""# Product Research Report: {topic}

## Executive Summary

{summary}

### Top 3 Product Opportunities
{detailed_report}

## Detailed Analysis

### Market Research Findings:
{market_findings}

### Technical Research Findings:
{technical_findings}
"""
    
    with open(filename, 'w') as f:
        f.write(report_content)
    
    return filename

def extract_findings(messages):
    """Extract findings from agent messages"""
    for msg in messages:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str):
            # First try to find content between tags
            if "<FINDINGS>" in content:
                start = content.find("<FINDINGS>") + len("<FINDINGS>")
                end = content.find("TERMINATE")
                if end != -1:
                    return content[start:end].strip()
            
            # If no tags found but we got a response, return the whole content
            if content.strip():
                return content.strip()
    return ""

def extract_summary(messages):
    """Extract summary from agent messages"""
    for msg in messages:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "<SUMMARY>" in content:
            start = content.find("<SUMMARY>") + len("<SUMMARY>")
            end = content.find("SUMMARY_COMPLETE")
            if end != -1:
                return content[start:end].strip()
    return ""

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Get topic from command line argument, or use default
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI agents for product research"
    print(f"Researching topic: {topic}")
    asyncio.run(run_product_research(topic))
