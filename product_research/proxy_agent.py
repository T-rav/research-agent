"""User proxy agent for managing interactions"""
import autogen
from typing import Dict, List, Tuple
from search_engines import perplexity_search, arxiv_search

def create_user_proxy() -> autogen.UserProxyAgent:
    """Create the User Proxy agent
    
    Returns:
        The configured User Proxy agent
    """
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4o-mini"],
        },
    )
    
    base_config = {
        "config_list": config_list,
        "temperature": 0.1,
        "model": "gpt-4o-mini",
        "timeout": 120
    }
    
    return autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: isinstance(x.get("content", ""), str) and x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
        llm_config=base_config,
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search
        }
    )
