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

    perplexity = perplexityai.Perplexity(api_key=api_key)
    
    try:
        response = perplexity.search(query)
        results = []
        results.append({
            "title": "Perplexity Search Result",
            "link": "",
            "snippet": response,
            "body": response
        })
        return results
    except Exception as e:
        print(f"Error in Perplexity search: {str(e)}")
        return []

def arxiv_search(query: str, max_results: int = 2) -> List[Dict]:
    """
    Search Arxiv for papers and return the results including abstracts
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = []
    for paper in client.results(search):
        results.append({
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "published": paper.published.strftime("%Y-%m-%d"),
            "abstract": paper.summary,
            "pdf_url": paper.pdf_url,
        })

    return results

# Configure the OpenAI API
config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0613", "gpt-4-32k-0314"],
    },
)

# Create agents
perplexity_search_agent = AssistantAgent(
    name="Market_Research_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a market research specialist that searches for product and market insights.
    Focus on finding information about:
    - Market trends and opportunities
    - Competitor products and features
    - User needs and pain points
    - Industry developments
    - Technology trends
    
    When searching, use:
    ```python
    perplexity_search(query: str, num_results: int = 2) -> List[Dict]
    ```
    Analyze search results to extract key product and market insights."""
)

arxiv_search_agent = AssistantAgent(
    name="Technology_Research_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a technology research specialist that searches for relevant technical innovations and research.
    Focus on finding papers about:
    - Technical innovations in the field
    - Novel approaches and methodologies
    - System architectures and designs
    - Performance improvements and optimizations
    - Technical feasibility studies
    
    Use this function to search:
    ```python
    arxiv_search(query: str, max_results: int = 2) -> List[Dict]
    ```
    Extract technical insights that could inform product development."""
)

report_agent = AssistantAgent(
    name="Product_Research_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a product research specialist that synthesizes market and technical information into actionable insights.
    Create a well-structured report that includes:
    
    1. Market Overview
       - Market size and growth
       - Key trends and drivers
       - Target audience analysis
       - Industry dynamics
    
    2. Competitive Analysis
       - Key players and their offerings
       - Feature comparison matrix
       - Market positioning map
       - Competitive advantages/disadvantages
    
    3. Technical Landscape
       - Current technological capabilities
       - Innovation opportunities
       - Technical constraints
       - Implementation considerations
    
    4. Product Opportunities
       - Unmet needs and pain points
       - Feature recommendations
       - Differentiation strategies
       - Unique value propositions
    
    5. Risk Analysis
       - Market risks
       - Technical risks
       - Mitigation strategies
       - Dependencies
    
    6. Product Ideas
       - Detailed feature concepts
       - User experience suggestions
       - Integration possibilities
       - Potential expansions
    
    7. Sources and References
       - Market research sources
       - Technical papers
       - Competitor information
       - Industry reports
    
    Format the report in markdown with clear sections and subsections.
    Include specific examples, data points, and sources where available.
    Your response should end with the word 'TERMINATE'"""
)

executive_summary_agent = AssistantAgent(
    name="Product_Strategy_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a product strategy specialist that creates impactful executive summaries.
    Focus on key strategic insights:
    - Market opportunity and size
    - Competitive advantage
    - Key differentiators
    - Technical feasibility
    - Recommended next steps
    
    Format the summary in markdown with clear sections and bullet points.
    Keep it actionable and business-focused.
    Your response should end with the word 'SUMMARY_COMPLETE'"""
)

def write_summary_to_file(summary: str, detailed_report: str, topic: str):
    """
    Write both executive summary and detailed report to markdown files in the summaries directory
    """
    # Create a safe filename from the topic
    safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    
    # Create summaries directory if it doesn't exist
    summaries_dir = os.path.join(os.path.dirname(__file__), "summaries")
    os.makedirs(summaries_dir, exist_ok=True)
    
    # Write executive summary
    summary_filename = f"executive_summary_{safe_filename}.md"
    summary_filepath = os.path.join(summaries_dir, summary_filename)
    with open(summary_filepath, 'w') as f:
        f.write("# Executive Summary\n\n")
        f.write(summary)
    
    # Write detailed report
    report_filename = f"detailed_report_{safe_filename}.md"
    report_filepath = os.path.join(summaries_dir, report_filename)
    with open(report_filepath, 'w') as f:
        f.write(f"# Detailed Product Research Report: {topic}\n\n")
        f.write(detailed_report)
    
    return summary_filename, report_filename

# Function to run the literature review
async def run_product_research(topic: str):
    """
    Run a literature review on the given topic
    """
    print(f"Starting literature review on topic: {topic}")
    
    # Create a user proxy agent
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "product_research", "use_docker": False},
        llm_config={"config_list": config_list},
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search,
        }
    )

    # Create the group chat for literature review
    review_chat = GroupChat(
        agents=[user_proxy, perplexity_search_agent, arxiv_search_agent, report_agent],
        messages=[],
        max_round=50,
        speaker_selection_method="round_robin"
    )
    
    # Create a manager for the review chat
    manager = autogen.GroupChatManager(
        groupchat=review_chat,
        llm_config={"config_list": config_list},
    )
    
    # Start the conversation for the literature review
    await user_proxy.a_initiate_chat(
        manager,
        message=f"Write a product research report on {topic}. Use perplexity_search and arxiv_search functions to gather information.",
    )
    
    # Get the last message from the report agent (the complete review)
    review_content = ""
    for msg in reversed(user_proxy.chat_messages[report_agent]):
        if msg["role"] == "assistant":
            review_content = msg["content"]
            break
    
    # Create a new chat for the executive summary
    summary_chat = GroupChat(
        agents=[user_proxy, executive_summary_agent],
        messages=[],
        max_round=3,
        speaker_selection_method="round_robin"
    )
    
    # Create a manager for the summary chat
    summary_manager = autogen.GroupChatManager(
        groupchat=summary_chat,
        llm_config={"config_list": config_list},
    )
    
    # Request the executive summary
    await user_proxy.a_initiate_chat(
        summary_manager,
        message=f"Create an executive summary of this product research report:\n\n{review_content}",
    )
    
    # Get the executive summary content
    summary_content = None
    for msg in summary_manager.chat_messages[user_proxy]:
        if "SUMMARY_COMPLETE" in msg:
            summary_content = msg.replace("SUMMARY_COMPLETE", "").strip()
            break
    
    # Get the detailed report content
    detailed_report = None
    for msg in manager.chat_messages[user_proxy]:
        if "TERMINATE" in msg:
            detailed_report = msg.replace("TERMINATE", "").strip()
            break
    
    # Write both summary and report to files
    if summary_content and detailed_report:
        summary_file, report_file = write_summary_to_file(summary_content, detailed_report, topic)
        print(f"\nExecutive summary has been written to: {summary_file}")
        print(f"Detailed report has been written to: {report_file}")
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
