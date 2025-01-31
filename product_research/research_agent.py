"""Research Agent for conducting product research"""
import autogen
from typing import Dict, List, Tuple
from search_engines import perplexity_search, arxiv_search

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
            system_message="""You are the Research Lead, responsible for:
            1. Breaking down research requests into specific tasks
            2. Delegating tasks to specialized team members
            3. Reviewing and synthesizing findings
            4. Ensuring quality and completeness
            5. Providing final recommendations
            """,
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
            function_map={
                "perplexity_search": perplexity_search
            }
        )

    def _create_data_analyst(self) -> autogen.AssistantAgent:
        """Create the Data Analyst agent"""
        config = self._get_base_config()
        return autogen.AssistantAgent(
            name="Data_Analyst",
            system_message="""You are the Data Analyst, focusing on:
            1. Current year market size and growth metrics (prioritize latest available data)
            2. Recent industry trends within the last 12 months
            3. Current competitive landscape analysis
            4. Latest user behavior and demographics
            5. Up-to-date financial metrics and projections
            
            Always validate data sources and provide confidence levels.
            Focus on getting the most recent data available, ideally from the current year.
            When searching, explicitly request data for the current year.
            """,
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
            function_map={
                "perplexity_search": perplexity_search
            }
        )

    def _create_tech_researcher(self) -> autogen.AssistantAgent:
        """Create the Technical Researcher agent"""
        config = self._get_base_config()
        return autogen.AssistantAgent(
            name="Technical_Researcher",
            system_message="""You are the Technical Researcher, focusing on:
            1. Technical feasibility analysis
            2. Implementation requirements
            3. Technical architecture and design
            4. Latest technical developments
            5. Technical risks and challenges
            """,
            llm_config={
                **config,
                "functions": [{
                    "name": "arxiv_search",
                    "description": "Search arXiv papers",
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
            function_map={
                "arxiv_search": arxiv_search
            }
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
