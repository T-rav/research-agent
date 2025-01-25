import autogen
from autogen import AssistantAgent, UserProxyAgent
from .search_engines import perplexity_search, arxiv_search

def create_agents():
    """Create and configure the research and user proxy agents.
    
    This function sets up two agents: a research agent and a user proxy agent.
    The research agent is responsible for conducting market and technical research
    using the Perplexity AI and Arxiv search functions. It is configured with a low
    temperature for deterministic responses and is specialized in formatting and 
    presenting structured findings.
    
    The user proxy agent is configured to handle user interactions automatically,
    with a set limit on consecutive auto-replies and a termination condition based
    on message content. It utilizes the same configuration list for consistency and
    has a defined function map for executing specific search functions.
    """
    
    # Configure the OpenAI API
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4o-mini"],
        },
    )

    # Create research agent
    research_agent = AssistantAgent(
        name="Research_Agent",
        llm_config={
            "config_list": config_list,
            "temperature": 0.1,
            "model": "gpt-4o-mini",
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
        
        For each research query:
        1. First use perplexity_search for:
           - Market data and statistics
           - Current trends and developments
           - Company and product information
           - General industry insights
           
        2. Then use arxiv_search when relevant for:
           - Technical innovations
           - Research papers
           - Scientific methodologies
           - Academic perspectives
        
        Combine the findings by:
        1. Leading with the most relevant and recent information
        2. Supporting market insights with technical research when available
        3. Including specific numbers, statistics, and direct quotes
        4. Citing sources clearly for all information
        5. Highlighting any conflicts between sources
        
        Format your response in clear sections:
        - Key Findings
        - Market Data
        - Technical Details (if relevant)
        - Sources
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
            "model": "gpt-4o-mini",
            "timeout": 120
        },
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search
        }
    )

    return research_agent, user_proxy
