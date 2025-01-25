import autogen
from autogen import AssistantAgent, UserProxyAgent
from .search_engines import perplexity_search, arxiv_search

def create_agents():
    """Create and configure the research and user proxy agents"""
    
    # Configure the OpenAI API
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4-1106-preview"],
        },
    )

    # Create research agent
    research_agent = AssistantAgent(
        name="Research_Agent",
        llm_config={
            "config_list": config_list,
            "temperature": 0.1,
            "model": "gpt-4-1106-preview",
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
        """
    )

    # Create user proxy agent
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
        llm_config={
            "config_list": config_list,
            "model": "gpt-4-1106-preview",
            "timeout": 120
        },
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search
        }
    )

    return research_agent, user_proxy
