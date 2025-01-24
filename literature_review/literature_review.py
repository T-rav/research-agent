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
    name="Perplexity_Search_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a helpful AI assistant that can search for information using Perplexity AI.
    When asked for information, use this function to search:
    ```python
    perplexity_search(query: str, num_results: int = 2) -> List[Dict]
    ```
    Analyze and summarize the search results effectively."""
)

arxiv_search_agent = AssistantAgent(
    name="Arxiv_Search_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a helpful AI assistant that can search for academic papers on arXiv.
    When asked for papers, use this function to search:
    ```python
    arxiv_search(query: str, max_results: int = 2) -> List[Dict]
    ```
    Take into consideration the user's request and craft search queries that are most likely to return relevant academic papers."""
)

report_agent = AssistantAgent(
    name="Report_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a helpful assistant that synthesizes information into high-quality literature reviews.
    Your task is to create a well-structured review that includes CORRECT references.
    Your response should end with the word 'TERMINATE'"""
)

executive_summary_agent = AssistantAgent(
    name="Executive_Summary_Agent",
    llm_config={"config_list": config_list},
    system_message="""You are a skilled executive summary writer.
    Create concise, clear, and impactful summaries focusing on key findings, implications, and recommendations.
    Format the summary in markdown with clear sections.
    Your response should end with the word 'SUMMARY_COMPLETE'"""
)

def write_summary_to_file(summary: str, topic: str):
    """
    Write the executive summary to a markdown file
    """
    # Create a safe filename from the topic
    safe_filename = "".join(x for x in topic if x.isalnum() or x in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    
    filename = f"executive_summary_{safe_filename}.md"
    
    with open(filename, 'w') as f:
        f.write(summary)
    
    return filename

# Function to run the literature review
async def run_literature_review(topic: str):
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
        code_execution_config={"work_dir": "literature_review", "use_docker": False},
        llm_config={"config_list": config_list},
    )

    # Register the search functions
    user_proxy.register_function(
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
        message=f"Write a literature review on {topic}",
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
        message=f"Create an executive summary of this literature review:\n\n{review_content}",
    )
    
    # Get the executive summary content
    summary_content = ""
    for msg in reversed(user_proxy.chat_messages[executive_summary_agent]):
        if msg["role"] == "assistant" and "SUMMARY_COMPLETE" in msg["content"]:
            summary_content = msg["content"].replace("SUMMARY_COMPLETE", "").strip()
            break
    
    # Write the summary to a file
    if summary_content:
        filename = write_summary_to_file(summary_content, topic)
        print(f"\nExecutive summary has been written to: {filename}")
    else:
        print("\nNo executive summary was generated.")

if __name__ == "__main__":
    import asyncio
    
    # Example usage
    topic = "no code tools for building multi agent AI systems"
    asyncio.run(run_literature_review(topic))
