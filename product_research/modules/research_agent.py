"""Research Agent for conducting product research"""
import autogen
from typing import Dict, List, Tuple
from .search_engines import perplexity_search, arxiv_search

class ResearchAgent:
    """Conducts product research tasks"""
    
    def __init__(self):
        """Initialize research agent"""
        # Create research team
        self.lead = self._create_research_lead()
        self.analyst = self._create_data_analyst()
        self.researcher = self._create_tech_researcher()

    def _get_base_config(self) -> dict:
        """Get base configuration for research agents"""
        config_list = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4o-mini"],
            },
        )
        
        return {
            "config_list": config_list,
            "temperature": 0.1,
            "model": "gpt-4o-mini",
        }

    def _create_research_lead(self) -> autogen.AssistantAgent:
        """Create the Research Lead agent"""
        config = self._get_base_config()
        return autogen.AssistantAgent(
            name="Research_Lead",
            llm_config={
                **config,
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
            """
        )

    def _create_data_analyst(self) -> autogen.AssistantAgent:
        """Create the Data Analyst agent"""
        config = self._get_base_config()
        return autogen.AssistantAgent(
            name="Data_Analyst",
            llm_config={
                **config,
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

    def _create_tech_researcher(self) -> autogen.AssistantAgent:
        """Create the Technical Researcher agent"""
        config = self._get_base_config()
        return autogen.AssistantAgent(
            name="Technical_Researcher",
            llm_config={
                **config,
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
        
    def get_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Get all research agents
        
        Returns:
            Dictionary of agent name to agent instance
        """
        return {
            "lead": self.lead,
            "analyst": self.analyst,
            "researcher": self.researcher
        }
