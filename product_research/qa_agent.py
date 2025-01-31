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
            system_message="""You are the QA Reviewer, responsible for validating research content.
            
            For each piece of content you review:
            1. Identify key claims, statistics, and facts
            2. Use the search_serper function to find supporting evidence
            3. Compare the claims against search results
            4. Flag any discrepancies or unverifiable claims
            5. Suggest corrections with citations
            
            Pay special attention to:
            - Market size numbers
            - Growth rates and projections
            - Company market shares
            - Technology adoption rates
            - Industry trends
            
            Always respond with either:
            VALID - If all claims are verified
            INVALID: <reason> - If any claims need correction
            
            Include citations from search results to support your validation.
            """
        )
        
    def get_agent(self) -> autogen.AssistantAgent:
        """Get the QA agent instance
        
        Returns:
            The QA agent
        """
        return self.agent
