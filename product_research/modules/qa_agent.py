import json
from typing import Dict, List, Tuple
import autogen
from .search_engines import search_serper

class QAAgent:
    """Agent responsible for fact-checking and validating research content"""
    
    def __init__(self):
        # Create specialized QA agents
        self.agents = self._create_agents()
        
    def _create_agents(self) -> Dict:
        """Create specialized agents for different QA tasks"""
        # Fact checker focuses on verifying claims against Serper search results
        fact_checker = autogen.AssistantAgent(
            name="fact_checker",
            system_message="""You are a meticulous fact checker. Your role is to:
                1. Verify factual claims using Serper search results
                2. Flag any claims that cannot be verified or appear incorrect
                3. Suggest corrections with supporting evidence
                4. Pay special attention to numbers, statistics, and specific claims
                
                Always cite your sources when suggesting corrections.""",
            llm_config={"temperature": 0.3}  # Lower temperature for more factual responses
        )
        
        # Style reviewer focuses on writing quality and consistency
        style_reviewer = autogen.AssistantAgent(
            name="style_reviewer",
            system_message="""You are a professional editor focusing on style and clarity. Your role is to:
                1. Check for consistent tone and voice throughout the content
                2. Identify and remove redundant information
                3. Ensure proper flow between sections
                4. Flag any unclear or ambiguous statements
                5. Suggest improvements for readability
                
                Focus on making the content professional and accessible.""",
            llm_config={"temperature": 0.7}  # Higher temperature for more creative suggestions
        )
        
        # User proxy for orchestrating the QA process
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("REVIEW_COMPLETE"),
            system_message="""You are coordinating the QA review process. Your role is to:
                1. Send content to appropriate agents for review
                2. Collect and aggregate their feedback
                3. Ensure all aspects are reviewed
                4. Signal completion with 'REVIEW_COMPLETE'"""
        )
        
        return {
            "fact_checker": fact_checker,
            "style_reviewer": style_reviewer,
            "proxy": user_proxy
        }
    
    async def validate_content(self, section: str, content: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate content for factual accuracy and style
        Returns: (is_valid, corrections, improvements)
        """
        # Create group chat for collaborative review
        groupchat = autogen.GroupChat(
            agents=[
                self.agents["fact_checker"],
                self.agents["style_reviewer"],
                self.agents["proxy"]
            ],
            messages=[],
            max_round=5
        )
        manager = autogen.GroupChatManager(groupchat=groupchat)
        
        # Prepare review message
        review_msg = f"""Review the following {section} content for factual accuracy and style:

Content to Review:
{content}

Please provide:
1. Fact check results with any corrections needed
2. Style and clarity improvements
3. Suggestions for better flow or organization

Use Serper search to verify key claims."""
        
        try:
            # Initiate the review process
            await self.agents["proxy"].initiate_chat(
                self.agents["fact_checker"],
                message=review_msg
            )
            
            # Extract feedback from the conversation
            chat_history = groupchat.messages
            corrections = []
            improvements = []
            
            for msg in chat_history:
                if msg["sender"] == "fact_checker":
                    corrections.extend(self._extract_corrections(msg["content"]))
                elif msg["sender"] == "style_reviewer":
                    improvements.extend(self._extract_improvements(msg["content"]))
            
            # Content is valid if there are no corrections needed
            is_valid = len(corrections) == 0
            
            return is_valid, corrections, improvements
            
        except Exception as e:
            print(f"Error during content validation: {str(e)}")
            return False, [f"Validation error: {str(e)}"], []
    
    def _extract_corrections(self, feedback: str) -> List[str]:
        """Extract factual corrections from feedback"""
        corrections = []
        # Split feedback into lines and look for correction markers
        for line in feedback.split('\n'):
            if any(marker in line.lower() for marker in ['correction:', 'incorrect:', 'error:', 'fix:']):
                corrections.append(line.strip())
        return corrections
    
    def _extract_improvements(self, feedback: str) -> List[str]:
        """Extract style improvements from feedback"""
        improvements = []
        # Split feedback into lines and look for improvement markers
        for line in feedback.split('\n'):
            if any(marker in line.lower() for marker in ['improve:', 'suggest:', 'enhance:', 'revise:']):
                improvements.append(line.strip())
        return improvements
