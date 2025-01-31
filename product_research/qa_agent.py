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
        
        return autogen.AssistantAgent(
            name="QA_Reviewer",
            system_message="""You are the QA Reviewer, responsible for validating research content.
            
            Your role is to:
            1. Verify the accuracy of research content by cross-referencing with reliable sources
            2. Check for completeness of required information
            3. Ensure clarity and coherence
            4. Verify citations and sources are provided where needed
            
            When validating content:
            1. Use the search_serper function to fact check key claims and data points
            2. Compare the research content against the search results
            3. Look for any missing important information
            4. Check that sources are reliable and current
            
            Respond with either:
            VALID: If the content meets all criteria
            INVALID: <reason> - If the content needs improvement
            
            Be thorough but efficient in your validation.
            """,
            llm_config={
                **config,
                "functions": [{
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
            },
            function_map={
                "search_serper": search_serper
            }
        )
        
    def get_agent(self) -> autogen.AssistantAgent:
        """Get the QA agent instance
        
        Returns:
            The QA agent
        """
        return self.agent

    def validate_content(self, content: str, section: str, topic: str, proxy) -> Tuple[bool, str]:
        """Validate research content
        
        Args:
            content: The content to validate
            section: The section being validated
            topic: The topic being researched
            proxy: The user proxy for chat initiation
            
        Returns:
            Tuple of (is_valid: bool, feedback: str)
        """
        print("\nSending content to QA reviewer...")
        qa_response = proxy.initiate_chat(
            self.agent,
            message=f"""Please validate this research content for {section} of {topic}. 
            Check for:
            1. Accuracy and factual correctness
            2. Completeness of required information
            3. Clarity and coherence
            4. Citations and sources where needed
            
            Content to validate:
            {content}
            
            Respond with either:
            VALID - If the content meets all criteria
            INVALID: <reason> - If the content needs improvement
            """,
            silent=False
        )
        
        # Get QA's response
        print("\nChecking QA response...")
        if hasattr(qa_response, 'chat_history'):
            messages = list(qa_response.chat_history)
        elif hasattr(qa_response, 'messages'):
            messages = list(qa_response.messages)
        else:
            messages = list(qa_response) if qa_response else []
            
        if not messages:
            print("\nWarning: No messages from QA")
            return False, "No messages from QA"
            
        # Find last message from QA
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("name") == self.agent.name:
                response = msg.get("content", "")
                if response:
                    if response.startswith("VALID"):
                        return True, ""
                    elif "INVALID:" in response:
                        feedback = response.split("INVALID:", 1)[1].strip()
                        print(f"\nQA found issues:")
                        print("-" * 40)
                        print(feedback)
                        print("-" * 40)
                        return False, feedback
                        
        return False, "No valid QA response found"
