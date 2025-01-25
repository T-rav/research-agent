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
    name="Market_Research_Agent",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "perplexity_search",
                "description": "Search using Perplexity AI API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 2
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    },
    system_message="""You are a market research specialist that searches for product and market insights.
    Focus on finding information about:
    - Market trends and opportunities
    - Competitor products and features
    - User needs and pain points
    - Industry developments
    - Technology trends
    
    Use the perplexity_search function to gather real market insights. After each search, analyze the results and provide structured findings.
    
    After analyzing search results, provide your findings in this format:
    
    <FINDINGS>
    [Your detailed analysis here]
    TERMINATE
    </FINDINGS>"""
)

arxiv_search_agent = AssistantAgent(
    name="Technology_Research_Agent",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "arxiv_search",
                "description": "Search Arxiv for papers and return the results including abstracts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 2
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    },
    system_message="""You are a technology research specialist that breaks down topics into key technical components and explores related areas.
    
    When given a topic, first break it down into:
    1. Core Technology Components
       - Key technical elements
       - Required capabilities
       - Supporting technologies
    
    2. Related Technical Areas
       - Adjacent technologies
       - Complementary solutions
    
    Use the arxiv_search function to find relevant research papers and extract key insights.
    
    After your analysis, provide your findings in this format:
    
    <FINDINGS>
    [Your detailed analysis here]
    TERMINATE
    </FINDINGS>"""
)

product_strategy_agent = AssistantAgent(
    name="Product_Strategy_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a product strategy specialist that creates impactful executive summaries.
    
    Your role is to:
    1. Review market and technology research
    2. Identify key opportunities and challenges
    3. Propose specific product ideas and features
    4. Highlight competitive advantages
    5. Suggest implementation priorities
    
    After your analysis, provide your findings in this format:
    
    <SUMMARY>
    [Your executive summary here]
    SUMMARY_COMPLETE
    </SUMMARY>"""
)

def write_summary_to_file(summary: str, detailed_report: str, topic: str):
    """
    Write a combined report with executive summary and detailed findings to a single markdown file
    """
    # Create a safe filename from the topic
    safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Write combined report
    report_filename = f"product_research_report_{safe_filename}.md"
    report_filepath = os.path.join(reports_dir, report_filename)
    
    # Extract top 3 product ideas from the detailed report
    import re
    product_ideas = re.findall(r'(?:^|\n)(\d+\.\s+.*?)(?=\n\d+\.|\n\n|$)', detailed_report, re.MULTILINE)
    top_3_ideas = product_ideas[:3] if product_ideas else []
    
    with open(report_filepath, 'w') as f:
        # Write title
        f.write(f"# Product Research Report: {topic}\n\n")
        
        # Write executive summary with top 3 ideas
        f.write("## Executive Summary\n\n")
        f.write(summary)
        f.write("\n\n### Top 3 Product Opportunities\n\n")
        for idx, idea in enumerate(top_3_ideas, 1):
            f.write(f"{idx}. {idea.strip()}\n")
        f.write("\n")
        
        # Write detailed report
        f.write("## Detailed Analysis\n\n")
        f.write(detailed_report)
    
    return report_filename

# Function to run the literature review
async def run_product_research(topic: str):
    """
    Run a literature review on the given topic
    """
    print(f"Starting literature review on topic: {topic}")
    
    # Create a group chat
    groupchat = GroupChat(
        agents=[perplexity_search_agent, arxiv_search_agent, product_strategy_agent],
        messages=[],
        max_round=12
    )

    # Create a user proxy agent
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "product_research",
            "use_docker": False,
            "last_n_messages": 3,
            "timeout": 60
        },
        llm_config={
            "config_list": config_list,
            "timeout": 120
        },
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search,
        }
    )

    # Start the group chat
    print("Phase 1: Market Research")
    await user_proxy.a_initiate_chat(
        perplexity_search_agent,
        message=f"Research market trends and competitors for {topic}. Use perplexity_search to gather information."
    )

    # Extract findings from market research
    market_findings = ""
    for msg in user_proxy.chat_messages[perplexity_search_agent]:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "FINDINGS" in content:
            start = content.find("<FINDINGS>") + len("<FINDINGS>")
            end = content.find("TERMINATE")
            if end != -1:
                market_findings = content[start:end].strip()
                break

    print("\nPhase 2: Technical Research")
    await user_proxy.a_initiate_chat(
        arxiv_search_agent,
        message=f"Research technical aspects and innovations for {topic}. Use arxiv_search to find relevant papers."
    )

    # Extract findings from technical research
    technical_findings = ""
    for msg in user_proxy.chat_messages[arxiv_search_agent]:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "FINDINGS" in content:
            start = content.find("<FINDINGS>") + len("<FINDINGS>")
            end = content.find("TERMINATE")
            if end != -1:
                technical_findings = content[start:end].strip()
                break

    # Combine market and technical findings
    combined_findings = f"""
Market Research Findings:
{market_findings}

Technical Research Findings:
{technical_findings}
"""

    print("\nPhase 3: Product Strategy")
    await user_proxy.a_initiate_chat(
        product_strategy_agent,
        message=f"Based on this research, create an executive summary for {topic}:\n\n{combined_findings}"
    )

    # Extract executive summary
    summary_content = ""
    for msg in user_proxy.chat_messages[product_strategy_agent]:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "SUMMARY" in content:
            start = content.find("<SUMMARY>") + len("<SUMMARY>")
            end = content.find("SUMMARY_COMPLETE")
            if end != -1:
                summary_content = content[start:end].strip()
                break

    # Write both summary and report to files
    if summary_content and combined_findings:
        print("\nDebug: About to write files...")
        print(f"Debug: Summary content exists: {bool(summary_content)}")
        print(f"Debug: Detailed report exists: {bool(combined_findings)}")
        report_file = write_summary_to_file(summary_content, combined_findings, topic)
        print(f"\nCombined report has been written to: {report_file}")
        print("\nExecutive Summary:")
        print("-" * 80)
        print(summary_content)
        print("-" * 80)
    else:
        print("\nNo summary or report was generated.")

if __name__ == "__main__":
    import asyncio
    import sys
    
    # Get topic from command line argument, or use default
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI agents for product research"
    print(f"Researching topic: {topic}")
    asyncio.run(run_product_research(topic))
