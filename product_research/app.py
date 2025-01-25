import os
from typing import List, Dict
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat
from autogen.agentchat.contrib.text_analyzer_agent import TextAnalyzerAgent
import requests
import arxiv
from dotenv import load_dotenv
import perplexityai

# Load environment variables
load_dotenv()

def perplexity_search(query: str, num_results: int = 2) -> List[Dict]:
    """
    Search using Perplexity AI API
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("Perplexity API key not found in environment variables")

    perplexity = perplexityai.Perplexity()
    perplexity.token = api_key
    
    try:
        response = perplexity.search(query)
        print(f"Debug - Raw response: {response}")  # Debug line
        
        # Handle different response types
        if isinstance(response, str):
            text_response = response
        elif isinstance(response, dict) and 'text' in response:
            text_response = response['text']
        elif isinstance(response, dict) and 'answer' in response:
            text_response = response['answer']
        else:
            text_response = str(response)
            
        results = [{
            "title": "Perplexity Search Result",
            "link": "",
            "snippet": text_response,
            "body": text_response
        }]
        return results
    except Exception as e:
        print(f"Error in Perplexity search: {str(e)}")
        return []

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
    system_message="""You are a search agent. Your ONLY task is to:
    1. Call perplexity_search with the user's query
    2. Format the results in a structured way
    3. Never use your own knowledge, only use search results
    
    Example:
    User: Search for X
    You: Let me search for that information.
    *calls perplexity_search with appropriate query*
    <FINDINGS>
    [Format the search results here]
    TERMINATE"""
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
        }
    )

    # Phase 1: Market Research
    print("\nPhase 1: Market Research")
    market_data = await user_proxy.a_execute_function(
        function_name="perplexity_search",
        arguments={
            "query": f"market analysis and trends for {topic}",
            "num_results": 3
        }
    )
    
    # Phase 2: Technical Research
    print("\nPhase 2: Technical Research")
    technical_data = await user_proxy.a_execute_function(
        function_name="arxiv_search",
        arguments={
            "query": f"technical research and innovations in {topic}",
            "max_results": 5
        }
    )
    
    # Combine research data
    research_data = f"""
Market Research Data:
{market_data}

Technical Research Data:
{technical_data}
"""
    
    # Phase 3: Generate Summary
    print("\nPhase 3: Product Strategy")
    await user_proxy.a_initiate_chat(
        product_strategy_agent,
        message=f"Based on this research, create an executive summary for {topic}:\n\n{research_data}"
    )

    # Extract and write summary
    summary_content = ""
    for msg in user_proxy.chat_messages[product_strategy_agent]:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "<SUMMARY>" in content:
            start = content.find("<SUMMARY>") + len("<SUMMARY>")
            end = content.find("SUMMARY_COMPLETE")
            if end != -1:
                summary_content = content[start:end].strip()
                break

    # Write report
    if summary_content:
        print("\nWriting final report...")
        report_file = write_summary_to_file(
            summary_content, 
            "", 
            topic, 
            str(market_data), 
            str(technical_data)
        )
        print(f"\nReport has been written to: {report_file}")
    else:
        print("\nError: Failed to generate report")

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Get topic from command line argument, or use default
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI agents for product research"
    print(f"Researching topic: {topic}")
    asyncio.run(run_product_research(topic))
