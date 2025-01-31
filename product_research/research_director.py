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
    """Manages and orchestrates the research process"""
    
    def __init__(self, max_rounds: int = 12, human_input_mode: str = "NEVER"):
        """Initialize the research director
        
        Args:
            max_rounds: Maximum number of conversation rounds
            human_input_mode: When to request human input
        """
        # Create research team
        self.research = ResearchAgent()
        research_agents = self.research.get_agents()
        
        # Create QA reviewer
        self.qa = QAAgent().get_agent()
        
        # Create user proxy
        self.proxy = create_user_proxy()
        
        # Create group chat for research team
        self.research_chat = autogen.GroupChat(
            agents=list(research_agents.values()),
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="round_robin"
        )
        
        # Create group chat manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.research_chat,
            llm_config={
                "config_list": autogen.config_list_from_json(
                    "OAI_CONFIG_LIST",
                    filter_dict={"model": ["gpt-4o-mini"]}
                ),
                "temperature": 0.1
            }
        )
        
        # Track reports by topic
        self.reports: Dict[str, ResearchReport] = {}
    
    def research_topic(self, topic: str, section: str, attempt: int = 1, max_attempts: int = 3, qa_feedback: str = None) -> str:
        """Research a topic
        
        Args:
            topic: The product/technology to research
            section: Which section to research
            attempt: Current attempt number
            max_attempts: Maximum number of attempts before giving up
            qa_feedback: Feedback from previous QA validation
            
        Returns:
            Path to the research report
        """
        print(f"\n{'='*80}")
        print(f"Starting research for {topic} - {section} (Attempt {attempt}/{max_attempts})")
        print(f"{'='*80}")
        
        if attempt > max_attempts:
            print("\n⚠️  Max attempts reached. Using best available content.")
            return "Error: Max attempts reached without valid content"
        
        # Get or create report
        report = self.reports.get(topic)
        if not report:
            print(f"\nCreating new report for {topic}")
            report = ResearchReport(topic)
            self.reports[topic] = report
        
        # Create research task message
        task = self._get_research_prompt(section, topic)
        if qa_feedback:
            task += f"""\n\nPrevious attempt was rejected by QA for the following reasons:
            {qa_feedback}
            
            Please address these issues in your research."""
        
        print("\nStarting research team discussion...")
        print("-" * 40)
        
        # Start research chat
        chat_response = self.proxy.initiate_chat(
            self.manager,
            message=task
        )
        
        # Extract research content from chat
        content = self._extract_research_content(chat_response)
        print(f"\nResearch team completed their discussion")
        print(f"Content length: {len(content)} characters")
        print("-" * 40)
        print("Content preview:")
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 40)
        
        # Have QA validate in a separate chat
        print("\nStarting QA validation...")
        is_valid, feedback = self.qa.validate_content(content, section, topic, self.proxy)
        
        if is_valid:
            print("\n✓ Content validated by QA")
            # Save validated content
            report.set_section(section, content)
            print(f"\nSaved to report: {report.get_path()}")
            return report.get_path()
        
        print(f"\n✗ Content needs revision - attempt {attempt}/{max_attempts}")
        # If not valid, retry research with QA feedback
        return self.research_topic(topic, section, attempt + 1, max_attempts, feedback)
    
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
    
    def _extract_research_content(self, chat_response: List[Dict]) -> str:
        """Extract research content from chat response"""
        content = None
        for msg in reversed(chat_response):
            if isinstance(msg, dict) and msg.get("name") == "Research_Lead":
                content = msg.get("content", "")
                if "TERMINATE" in content:
                    return content.split("TERMINATE")[0].strip()
        
        if not content:
            raise ValueError("No research content found in chat")
        return content
    
    def research_full_topic(self, topic: str) -> Tuple[str, List[str]]:
        """Research all sections for a topic
        
        Args:
            topic: The product/technology to research
            
        Returns:
            Tuple of (report_path, List[warnings])
        """
        warnings = []
        report_path = None
        
        # Just do market size section for testing
        section = ReportSection.MARKET_SIZE.value
        result = self.research_topic(topic, section)
        if result.startswith("Error"):
            warnings.append(f"Error researching {section}: {result}")
        else:
            report_path = result
            
        return report_path or "", warnings
