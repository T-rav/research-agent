"""Research Director module for orchestrating the research process"""
import autogen
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from .qa_agent import QAAgent
from .proxy_agent import create_user_proxy
from .research_agent import ResearchAgent
from .research_report import ResearchReport

class ResearchDirector:
    """Manages and orchestrates the research process"""
    
    def __init__(self, max_rounds: int = 12, human_input_mode: str = "NEVER"):
        """Initialize the research director
        
        Args:
            max_rounds: Maximum number of conversation rounds
            human_input_mode: When to request human input
        """
        # Create all agents
        self.qa = QAAgent().get_agent()
        self.proxy = create_user_proxy()
        self.research = ResearchAgent()
        
        # Get research team
        research_agents = self.research.get_agents()
        
        # Combine all agents
        self.agents = {
            **research_agents,
            "qa": self.qa,
            "proxy": self.proxy
        }
        
        # Create group chat for team collaboration
        self.groupchat = autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=max_rounds
        )
        self.manager = autogen.GroupChatManager(groupchat=self.groupchat)
        
        # Track reports by topic
        self.reports: Dict[str, ResearchReport] = {}
        
    async def research_topic(self, topic: str, section: str) -> str:
        """Research a topic
        
        Args:
            topic: The product/technology to research
            section: Which section to research
            
        Returns:
            Path to the research report
        """
        # Get/create report for this topic
        if topic not in self.reports:
            self.reports[topic] = ResearchReport(topic)
        report = self.reports[topic]
        
        # Check if section exists and is recent
        if report.has_section(section):
            last_updated = report.get_section_updated(section)
            if last_updated and (datetime.now() - datetime.fromisoformat(last_updated)).days < 7:
                return report.get_path()
                
        # Map sections to research prompts
        prompts = {
            "market_size": """Research and analyze the total addressable market size for {topic}.
                Focus on:
                1. Current market value
                2. Growth rate and projections
                3. Key market segments
                4. Regional distribution
                
                QA Reviewer will fact-check in real-time.
                All team members collaborate to ensure accuracy and clarity.
                End with TERMINATE when complete.""",
                
            "competitors": """Research and analyze the competitive landscape for {topic}.
                Focus on:
                1. Key competitors and market share
                2. Competitor strengths/weaknesses
                3. Market positioning
                4. Competitive advantages
                
                QA Reviewer will fact-check in real-time.
                All team members collaborate to ensure accuracy and clarity.
                End with TERMINATE when complete.""",
                
            "trends": """Research and analyze market trends for {topic}.
                Focus on:
                1. Current market trends
                2. Emerging technologies
                3. Consumer behavior shifts
                4. Future outlook
                
                QA Reviewer will fact-check in real-time.
                All team members collaborate to ensure accuracy and clarity.
                End with TERMINATE when complete.""",
                
            "technical": """Provide technical analysis of {topic}.
                Focus on:
                1. Implementation considerations
                2. Architecture and design
                3. Technology stack
                4. Technical challenges
                
                QA Reviewer will fact-check in real-time.
                All team members collaborate to ensure accuracy and clarity.
                End with TERMINATE when complete.""",
                
            "summary": """Create an executive summary of the research on {topic}.
                Focus on:
                1. Key findings from all sections
                2. Critical insights
                3. Main recommendations
                4. Next steps
                
                QA Reviewer will fact-check in real-time.
                All team members collaborate to ensure accuracy and clarity.
                End with TERMINATE when complete."""
        }
        
        if section not in prompts:
            raise ValueError(f"Unknown research section: {section}")
            
        while True:  # Keep trying until we get valid research
            # Start research task
            message = prompts[section].format(topic=topic)
            try:
                # Use proxy to initiate research
                await self.proxy.initiate_chat(
                    self.manager,
                    message=message
                )
                
                # Get research findings
                content = None
                for msg in reversed(self.manager.chat_history):
                    if msg.get("name") != self.proxy.name:
                        content = msg.get("content", "")
                        break
                        
                if not content:
                    raise ValueError("No research content found")
                
                # Have QA validate the content
                await self.proxy.initiate_chat(
                    self.qa,
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
                    """
                )
                
                # Get QA response
                qa_response = None
                for msg in reversed(self.manager.chat_history):
                    if msg.get("name") == self.qa.name:
                        qa_response = msg.get("content", "")
                        break
                
                if not qa_response:
                    raise ValueError("No QA response found")
                    
                if qa_response.startswith("VALID"):
                    # Store validated content in report
                    if section == "market_size":
                        report.set_market_size(content)
                    elif section == "competitors":
                        report.set_competitors(content)
                    elif section == "trends":
                        report.set_trends(content)
                    elif section == "technical":
                        report.set_technical_findings(content)
                    elif section == "summary":
                        report.set_summary(content)
                        
                    return report.get_path()
                else:
                    # Extract reason for invalidity
                    reason = qa_response.split("INVALID:", 1)[1].strip()
                    
                    # Request improvements
                    message = f"""The previous research for {section} of {topic} needs improvement:
                    {reason}
                    
                    Please revise and improve the research addressing these issues.
                    Previous content for reference:
                    {content}"""
                    
                    # Continue loop to try again
                    continue
                    
            except Exception as e:
                return f"Error in research: {str(e)}"

    async def research_full_topic(self, topic: str) -> Tuple[str, List[str]]:
        """Research all sections for a topic
        
        Args:
            topic: The product/technology to research
            
        Returns:
            Tuple of (report_path, List[warnings])
        """
        warnings = []
        report_path = None
        
        # Research each section
        sections = ["market_size", "competitors", "trends", "technical", "summary"]
        for section in sections:
            result = await self.research_topic(topic, section)
            if result.startswith("Error"):
                warnings.append(result)
            else:
                report_path = result
                
        return report_path, warnings
