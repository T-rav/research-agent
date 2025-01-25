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
perplexity_search_agent = AssistantAgent(
    name="Perplexity_Search_Agent",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
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
            }
        ]
    },
    system_message="""You are a market research agent. Your task is to:
    1. Use perplexity_search to find market information about AI and technology
    2. Format the results in a clear structure
    3. Only use information from the search results
    
    When searching:
    1. Break down your search into specific aspects (market size, trends, players)
    2. Use clear, focused queries like:
       - "What is the current market size and growth rate of AI code generation?"
       - "Who are the major companies and startups in AI code generation?"
       - "What are the latest trends in AI code generation market?"
    3. If you get an error, try a simpler query
    
    Format your findings like this:
    <FINDINGS>
    # Market Overview
    [Market size, growth rates, and key statistics]
    
    # Key Players
    [Major companies, market leaders, and notable startups]
    
    # Market Trends
    [Current trends, emerging technologies, and market shifts]
    
    # Competitive Analysis
    [Market dynamics, competitive advantages, and challenges]
    TERMINATE
    """
)

arxiv_search_agent = AssistantAgent(
    name="Arxiv_Search_Agent",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "arxiv_search",
                "description": "Search arXiv papers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        ]
    },
    system_message="""You are a search agent. Your ONLY task is to:
    1. Call arxiv_search with the user's query
    2. Format the results in a structured way
    3. Never use your own knowledge, only use search results
    
    Example:
    User: Search for X
    You: Let me search for that information.
    *calls arxiv_search with appropriate query*
    <FINDINGS>
    [Format the search results here]
    TERMINATE"""
)

product_strategy_agent = AssistantAgent(
    name="Product_Strategy_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a skilled product strategist that creates comprehensive executive summaries.
    When creating a summary:
    1. Start with "<SUMMARY>"
    2. Include clear sections: Overview, Market Analysis, Technical Analysis, Opportunities, Challenges, and Recommendations
    3. Be specific and actionable
    4. End with "SUMMARY_COMPLETE"
    
    Example format:
    <SUMMARY>
    # Executive Summary
    
    ## Overview
    [Your content here]
    
    ## Market Analysis
    [Your content here]
    
    ## Technical Analysis
    [Your content here]
    
    ## Opportunities
    [Your content here]
    
    ## Challenges
    [Your content here]
    
    ## Recommendations
    [Your content here]
    SUMMARY_COMPLETE
    """
)

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

# Function to run the literature review
async def run_product_research(topic: str):
    """
    Run product research on the given topic
    """
    print(f"Starting product research on topic: {topic}")
    
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

    # Phase 1: Market Research
    print("\nPhase 1: Market Research")
    market_data = []
    
    # Search for market size and growth
    await user_proxy.a_initiate_chat(
        perplexity_search_agent,
        message=f"What is the current market size, value, and growth rate of {topic}? Include specific numbers and data."
    )
    market_size = extract_findings(user_proxy.chat_messages[perplexity_search_agent])
    market_data.append(("Market Size and Growth", market_size))
    
    # Search for key players
    await user_proxy.a_initiate_chat(
        perplexity_search_agent,
        message=f"Who are the major companies and key players in {topic}? List specific companies and their market positions."
    )
    key_players = extract_findings(user_proxy.chat_messages[perplexity_search_agent])
    market_data.append(("Key Players", key_players))
    
    # Search for market trends
    await user_proxy.a_initiate_chat(
        perplexity_search_agent,
        message=f"What are the latest market trends and developments in {topic}? Include recent changes and future predictions."
    )
    market_trends = extract_findings(user_proxy.chat_messages[perplexity_search_agent])
    market_data.append(("Market Trends", market_trends))

    # Combine market findings
    market_findings = "\n\n".join([f"# {title}\n{data}" for title, data in market_data if data])

    # Phase 2: Technical Research
    print("\nPhase 2: Technical Research")
    await user_proxy.a_initiate_chat(
        arxiv_search_agent,
        message=f"Find technical research papers about innovations and developments in {topic}."
    )
    tech_findings = extract_findings(user_proxy.chat_messages[arxiv_search_agent])

    # Combine all research
    research_data = f"""
Market Research Findings:
{market_findings}

Technical Research Findings:
{tech_findings}
"""

    # Phase 3: Generate Summary
    print("\nPhase 3: Product Strategy")
    await user_proxy.a_initiate_chat(
        product_strategy_agent,
        message=f"""Based on this research, create an executive summary for {topic}.
        Focus on key findings, market opportunities, and actionable insights.
        
        Research Data:
        {research_data}
        
        Format your response as:
        <SUMMARY>
        # Executive Summary
        [High-level overview]

        # Key Findings
        [Bullet points of most important discoveries]

        # Market Opportunities
        [Identified opportunities and potential areas for growth]

        # Recommendations
        [Actionable steps and strategic recommendations]
        SUMMARY_COMPLETE
        """
    )

    # Extract summary
    summary_content = extract_summary(user_proxy.chat_messages[product_strategy_agent])

    # Write report
    if summary_content and (market_findings or tech_findings):
        print("\nWriting final report...")
        report_file = write_summary_to_file(
            summary_content,
            "",
            topic,
            market_findings,
            tech_findings
        )
        print(f"\nReport has been written to: {report_file}")
    else:
        print("\nError: Failed to generate complete report")
        if not summary_content:
            print("Missing: Executive Summary")
        if not market_findings:
            print("Missing: Market Research Findings")
        if not tech_findings:
            print("Missing: Technical Research Findings")

def extract_findings(messages):
    """Extract findings from agent messages"""
    for msg in messages:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "<FINDINGS>" in content:
            start = content.find("<FINDINGS>") + len("<FINDINGS>")
            end = content.find("TERMINATE")
            if end != -1:
                return content[start:end].strip()
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
