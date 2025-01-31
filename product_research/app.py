import os
import json
from typing import Dict, List
import autogen
from modules.agents import create_agents
from modules.research_report import ResearchReport
from datetime import datetime

def extract_findings(content: str) -> str:
    """Extract research findings from agent response."""
    return content.strip() if content else ""

def extract_summary(content: str) -> str:
    """Extract summary from agent response."""
    if not content:
        return ""
    
    # Extract content between SUMMARY_START and SUMMARY_COMPLETE
    start_marker = "SUMMARY_START"
    end_marker = "SUMMARY_COMPLETE"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        return content.strip()
    
    summary = content[start_idx + len(start_marker):end_idx].strip()
    return summary

async def run_product_research(topic: str):
    """Run product research on a given topic"""
    # Initialize agents
    researcher = autogen.AssistantAgent(
        name="researcher",
        system_message="""You are an expert product researcher. Your task is to:
            1. Research the given topic thoroughly
            2. Analyze market size, competitors, and trends
            3. Provide technical analysis and recommendations
            4. Write clear, concise, and factual content
            5. Always cite your sources""",
        llm_config={"temperature": 0.7}
    )
    
    fact_checker = autogen.AssistantAgent(
        name="fact_checker",
        system_message="""You are a meticulous fact checker. Your role is to:
            1. Verify factual claims using Serper search results
            2. Flag any claims that cannot be verified
            3. Check numbers and statistics for accuracy
            4. Ensure all claims have proper citations
            5. Suggest corrections if needed
            
            Always cite your sources when suggesting corrections.""",
        llm_config={"temperature": 0.3}
    )
    
    style_reviewer = autogen.AssistantAgent(
        name="style_reviewer",
        system_message="""You are a professional editor focusing on style and clarity. Your role is to:
            1. Check for consistent tone and voice
            2. Remove redundant information
            3. Ensure proper flow between sections
            4. Flag unclear or ambiguous statements
            5. Improve readability
            
            Focus on making the content professional and accessible.""",
        llm_config={"temperature": 0.7}
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TASK_COMPLETE")
    )
    
    # Create group chat for collaborative research and review
    groupchat = autogen.GroupChat(
        agents=[researcher, fact_checker, style_reviewer, user_proxy],
        messages=[],
        max_round=12
    )
    manager = autogen.GroupChatManager(groupchat=groupchat)
    
    report = ResearchReport(topic)
    
    try:
        # Research market size
        market_size_query = f"""Task: Research and write about market size for {topic}.
            
            Requirements:
            1. Research current market value, growth rate, and projections
            2. Verify all numbers and statistics
            3. Ensure clear writing style and flow
            4. Include proper citations
            
            Process:
            1. Researcher: Conduct initial research and write content
            2. Fact Checker: Verify all claims and numbers
            3. Style Reviewer: Review writing quality
            4. All: Iterate until content is accurate and well-written
            
            End your message with TASK_COMPLETE when finished."""
        
        content = await user_proxy.initiate_chat(
            manager,
            message=market_size_query
        )
        report.set_market_size(content)
        
        # Research competitors
        competitor_query = f"""Task: Research and write about competitors in {topic} market.
            
            Requirements:
            1. Research market share, strengths, and weaknesses
            2. Verify company information and statistics
            3. Ensure clear writing style and flow
            4. Include proper citations
            
            Process:
            1. Researcher: Conduct initial research and write content
            2. Fact Checker: Verify all claims and numbers
            3. Style Reviewer: Review writing quality
            4. All: Iterate until content is accurate and well-written
            
            End your message with TASK_COMPLETE when finished."""
        
        content = await user_proxy.initiate_chat(
            manager,
            message=competitor_query
        )
        report.set_competitors(content)
        
        # Research trends
        trends_query = f"""Task: Research and write about trends in {topic} market.
            
            Requirements:
            1. Research technological, consumer, and regulatory trends
            2. Verify trend information and predictions
            3. Ensure clear writing style and flow
            4. Include proper citations
            
            Process:
            1. Researcher: Conduct initial research and write content
            2. Fact Checker: Verify all claims and predictions
            3. Style Reviewer: Review writing quality
            4. All: Iterate until content is accurate and well-written
            
            End your message with TASK_COMPLETE when finished."""
        
        content = await user_proxy.initiate_chat(
            manager,
            message=trends_query
        )
        report.set_trends(content)
        
        # Technical analysis
        technical_query = f"""Task: Research and write about technical aspects of {topic}.
            
            Requirements:
            1. Research implementation considerations and challenges
            2. Verify technical claims and solutions
            3. Ensure clear writing style and flow
            4. Include proper citations
            
            Process:
            1. Researcher: Conduct initial research and write content
            2. Fact Checker: Verify all technical claims
            3. Style Reviewer: Review writing quality
            4. All: Iterate until content is accurate and well-written
            
            End your message with TASK_COMPLETE when finished."""
        
        content = await user_proxy.initiate_chat(
            manager,
            message=technical_query
        )
        report.set_technical_findings(content)
        
        # Generate executive summary
        summary_query = f"""Task: Write executive summary for {topic} research.
            
            Requirements:
            1. Synthesize key points from all sections
            2. Verify summary matches source content
            3. Ensure clear writing style and flow
            4. Include proper citations
            
            Process:
            1. Researcher: Write initial summary
            2. Fact Checker: Verify accuracy against source sections
            3. Style Reviewer: Review writing quality
            4. All: Iterate until summary is accurate and well-written
            
            End your message with TASK_COMPLETE when finished."""
        
        content = await user_proxy.initiate_chat(
            manager,
            message=summary_query
        )
        report.set_summary(content)
        
        print(f"\nResearch complete! Report saved to: {report.report_path}")
        return report
        
    except Exception as e:
        print(f"Error during research: {str(e)}")
        raise

async def run_team_research(query: str, user_proxy, research_lead, manager):
    """Run a research query through the multi-agent team."""
    try:
        await user_proxy.initiate_chat(
            research_lead,
            message=query
        )
        return user_proxy.last_message()
    except Exception as e:
        print(f"Error in team research: {str(e)}")
        return ""

if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python app.py 'research topic'")
        sys.exit(1)
    
    topic = sys.argv[1]
    asyncio.run(run_product_research(topic))
