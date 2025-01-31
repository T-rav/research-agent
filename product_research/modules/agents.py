import autogen
from autogen import AssistantAgent, UserProxyAgent
from .search_engines import perplexity_search, arxiv_search

def create_agents():
    """Create and configure a team of research agents with specialized roles."""
    
    # Configure the OpenAI API
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4o-mini"],
        },
    )

    # Base configuration for all agents
    base_config = {
        "config_list": config_list,
        "temperature": 0.1,
        "model": "gpt-4o-mini",
    }

    # Create Research Lead agent
    research_lead = AssistantAgent(
        name="Research_Lead",
        llm_config={
            **base_config,
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
        system_message="""You are the Research Lead, responsible for:
        1. Breaking down research requests into specific tasks
        2. Delegating tasks to specialized team members
        3. Reviewing and synthesizing findings
        4. Ensuring quality and completeness
        5. Providing final recommendations
        
        Coordinate with:
        - Data Analyst for metrics and trends
        - Technical Researcher for academic/technical aspects
        - QA Reviewer for validation
        """
    )

    # Create Data Analyst agent
    data_analyst = AssistantAgent(
        name="Data_Analyst",
        llm_config={
            **base_config,
            "functions": [{
                "name": "perplexity_search",
                "description": "Search using Perplexity AI for market data",
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
        system_message="""You are the Data Analyst, focusing on:
        1. Market size and growth metrics
        2. Industry trends and patterns
        3. Competitive analysis
        4. User behavior and demographics
        5. Financial metrics and projections
        
        Always validate data sources and provide confidence levels.
        """
    )

    # Create Technical Researcher agent
    tech_researcher = AssistantAgent(
        name="Technical_Researcher",
        llm_config={
            **base_config,
            "functions": [{
                "name": "arxiv_search",
                "description": "Search academic papers on Arxiv",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer", "default": 3}
                    },
                    "required": ["query"]
                }
            }]
        },
        system_message="""You are the Technical Researcher, focusing on:
        1. Technical feasibility analysis
        2. Academic research findings
        3. Patent and innovation landscape
        4. Technology trends and adoption
        5. Technical risk assessment
        
        Provide technical depth while maintaining clarity.
        """
    )

    # Create QA Reviewer agent
    qa_reviewer = AssistantAgent(
        name="QA_Reviewer",
        llm_config=base_config,
        system_message="""You are the QA Reviewer, responsible for:
        1. Fact-checking and validation
        2. Identifying gaps in research
        3. Challenging assumptions
        4. Ensuring source credibility
        5. Maintaining research standards
        
        Be thorough and critical in your review.
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
            **base_config,
            "timeout": 120
        },
        function_map={
            "perplexity_search": perplexity_search,
            "arxiv_search": arxiv_search
        }
    )

    return {
        "lead": research_lead,
        "analyst": data_analyst,
        "researcher": tech_researcher,
        "reviewer": qa_reviewer,
        "proxy": user_proxy
    }
