"""QA Agent for validating research content"""
import autogen
import json
from typing import Dict, List, Tuple
from search_engines import search_serper

class QAAgent:
    """QA Agent for validating research"""
    
    def __init__(self):
        """Initialize QA agent"""
        self.agent = self._create_agent()
        
    def _get_base_config(self) -> dict:
        """Get base configuration for QA agent"""
        config_list = autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4o-mini"],
            },
        )
        
        return {
            "config_list": config_list,
            "temperature": 0.1,
            "model": "gpt-4o-mini"
        }
    
    def _create_agent(self) -> autogen.AssistantAgent:
        """Create the QA agent
        
        Returns:
            The configured QA agent
        """
        config = self._get_base_config()
        config["functions"] = [{
            "name": "search_serper",
            "description": "Search the web for fact checking",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }]
        
        return autogen.AssistantAgent(
            name="QA_Reviewer",
            llm_config=config,
            system_message="""You are the QA Reviewer, responsible for:
            1. Real-time fact-checking during research
            2. Validating claims and statistics
            3. Ensuring proper citations
            4. Checking writing style and clarity
            5. Suggesting improvements
            
            Actively participate in discussions to catch issues early.
            Flag any concerns immediately for the team to address.
            """
        )
        
    def get_agent(self) -> autogen.AssistantAgent:
        """Get the QA agent instance
        
        Returns:
            The QA agent
        """
        return self.agent
