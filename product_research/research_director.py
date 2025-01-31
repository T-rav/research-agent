"""Research Director for orchestrating research process"""
import os
import json
import asyncio
import autogen
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from proxy_agent import create_user_proxy
from research_agent import ResearchAgent
from research_report import ResearchReport
from report_sections import ReportSection
from qa_agent import QAAgent
from search_engines import perplexity_search

class ResearchDirector:
    """Director for coordinating product research"""
    
    def __init__(self):
        """Initialize research director"""
        # Create user proxy
        self.proxy = create_user_proxy()
        
        # Create research team
        self.lead = self._create_research_lead()
        self.analyst = self._create_data_analyst()
        self.researcher = self._create_tech_researcher()
        self.qa = QAAgent().get_agent()
        
        # Create group chat
        self.group_chat = autogen.GroupChat(
            agents=[self.lead, self.analyst, self.researcher, self.qa],
            messages=[],
            max_round=12
        )
        
        # Create manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.lead.llm_config
        )
        
        # Track reports by topic
        self.reports: Dict[str, ResearchReport] = {}
        
    async def research_topic(self, topic: str, section: str, attempt: int = 1, max_attempts: int = 3, qa_feedback: str = None) -> str:
        """Research a topic asynchronously
        
        Args:
            topic: The product/technology to research
            section: Which section to research
            attempt: Current attempt number
            max_attempts: Maximum number of attempts before giving up
            qa_feedback: Feedback from previous QA validation
            
        Returns:
            Path to the research report
        """
        print(f"\n{'=' * 80}")
        print(f"Starting research for {topic} - {section} (Attempt {attempt}/{max_attempts})")
        print(f"{'=' * 80}\n")
        
        if attempt > max_attempts:
            print("\n⚠️  Max attempts reached. Using best available content.")
            return f"Error: Failed to produce valid content after {max_attempts} attempts"
            
        # Get or create report
        report = self.reports.get(topic)
        if not report:
            print(f"\nCreating new report for {topic}")
            report = ResearchReport(topic)
            self.reports[topic] = report
            
        # Create research task message
        task = f"""Research task for {topic} - {section}
        
        Research Lead (@Research_Lead), please coordinate with:
        1. Data Analyst (@Data_Analyst) for market data and trends
        2. Technical Researcher (@Tech_Researcher) for technical details
        3. QA Reviewer (@QA_Reviewer) to validate the final content
        
        {self._get_research_prompt(section, topic)}
        
        If QA approves the content with "VALID", save it and finish.
        If QA responds with "INVALID", address the feedback and try again.
        
        Previous QA feedback to address:
        {qa_feedback if qa_feedback else 'None'}
        """
        
        print("\nStarting research team discussion...")
        print("-" * 40)
        
        # Start group chat
        chat_response = await asyncio.to_thread(
            self.proxy.initiate_chat,
            self.manager,
            message=task,
            silent=False
        )
        
        # Extract final content from chat
        content = self._extract_research_content(chat_response)
        
        # Check if QA approved in the chat
        messages = chat_response.chat_history if hasattr(chat_response, 'chat_history') else chat_response.messages
        is_valid = False
        feedback = ""
        
        for msg in reversed(messages):
            if msg.get("name") == "QA_Reviewer":
                response = msg.get("content", "")
                if response.startswith("VALID"):
                    is_valid = True
                    break
                elif "INVALID:" in response:
                    feedback = response.split("INVALID:", 1)[1].strip()
                    break
        
        if is_valid:
            print("\n✓ Content validated by QA")
            # Save validated content
            report.set_section(section, content)
            print(f"\nSaved to report: {report.get_path()}")
            return report.get_path()
            
        print(f"\n✗ Content needs revision - attempt {attempt}/{max_attempts}")
        return await self.research_topic(topic, section, attempt + 1, max_attempts, feedback)
        
    async def research_full_topic(self, topic: str) -> Tuple[str, List[str]]:
        """Research all sections for a topic asynchronously
        
        Args:
            topic: The product/technology to research
            
        Returns:
            Tuple of (report_path, List[warnings])
        """
        warnings = []
        report_path = None
        
        # Just do market size section for testing
        section = ReportSection.MARKET_SIZE.value
        result = await self.research_topic(topic, section)
        if isinstance(result, str) and result.startswith("Error"):
            warnings.append(f"Error researching {section}: {result}")
        else:
            report_path = result
            
        return report_path or "", warnings
    
    def _get_research_prompt(self, section: str, topic: str) -> str:
        """Get the research prompt for a section"""
        prompts = {
            ReportSection.MARKET_SIZE: """Research the market size for {topic}.
                Focus on:
                1. Current market value
                2. Growth projections
                3. Market segmentation
                4. Regional distribution
                
                Collaborate with the team to ensure comprehensive analysis.
                End with TERMINATE when complete.""",
                
            ReportSection.COMPETITORS: """Research the competitors in the {topic} market.
                Focus on:
                1. Key players
                2. Market shares
                3. Competitive advantages
                4. Recent developments
                
                Collaborate with the team to ensure comprehensive analysis.
                End with TERMINATE when complete.""",
                
            ReportSection.TRENDS: """Research market trends for {topic}.
                Focus on:
                1. Current trends
                2. Emerging patterns
                3. Consumer behavior shifts
                4. Future outlook
                
                Collaborate with the team to ensure comprehensive analysis.
                End with TERMINATE when complete.""",
                
            ReportSection.TECHNICAL: """Research technical aspects of {topic}.
                Focus on:
                1. Implementation considerations
                2. Architecture and design
                3. Technology stack
                4. Technical challenges
                
                Collaborate with the team to ensure comprehensive analysis.
                End with TERMINATE when complete.""",
                
            ReportSection.SUMMARY: """Create an executive summary of the research on {topic}.
                Focus on:
                1. Key findings from all sections
                2. Critical insights
                3. Main recommendations
                4. Next steps
                
                Collaborate with the team to ensure comprehensive analysis.
                End with TERMINATE when complete."""
        }
        
        if section not in [s.value for s in ReportSection]:
            raise ValueError(f"Unknown research section: {section}")
            
        return prompts[ReportSection(section)].format(topic=topic)
    
    def _extract_research_content(self, chat_response):
        """Extract research content from chat response
        
        Args:
            chat_response: The chat response from autogen
            
        Returns:
            The research content
        """
        # Get last message from the chat
        if hasattr(chat_response, 'chat_history'):
            # Handle ChatResult object
            if chat_response.chat_history:
                last_msg = chat_response.chat_history[-1]
                if isinstance(last_msg, dict):
                    content = last_msg.get("content", "")
                else:
                    content = str(last_msg)
        elif hasattr(chat_response, 'last_message'):
            content = chat_response.last_message.get("content", "")
        else:
            # Fallback for older versions or different response types
            messages = chat_response.messages if hasattr(chat_response, 'messages') else chat_response
            if not messages:
                raise ValueError("No messages in chat response")
            
            # Get the last message
            last_msg = messages[-1] if isinstance(messages, (list, tuple)) else messages
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
            else:
                content = str(last_msg)

        if not content:
            raise ValueError("No research content found in chat")
            
        # Remove any TERMINATE markers
        if "TERMINATE" in content:
            content = content.split("TERMINATE")[0].strip()
            
        return content

    def _create_research_lead(self):
        # Create research lead agent
        lead = ResearchAgent().get_agent()
        lead.name = "Research_Lead"
        lead.llm_config = {
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4o-mini"]}
            ),
            "temperature": 0.1
        }
        return lead

    def _create_data_analyst(self):
        # Create data analyst agent
        analyst = ResearchAgent().get_agent()
        analyst.name = "Data_Analyst"
        analyst.llm_config = {
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4o-mini"]}
            ),
            "temperature": 0.1
        }
        return analyst

    def _create_tech_researcher(self):
        # Create technical researcher agent
        researcher = ResearchAgent().get_agent()
        researcher.name = "Tech_Researcher"
        researcher.llm_config = {
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4o-mini"]}
            ),
            "temperature": 0.1
        }
        return researcher
