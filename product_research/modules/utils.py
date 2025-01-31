import os
import json
from typing import Dict, List, Optional

def extract_findings(messages) -> str:
    """Extract findings from agent messages"""
    if isinstance(messages, str):
        return messages.strip()
    
    if isinstance(messages, dict):
        content = messages.get("content", "")
        return content.strip()
    
    if isinstance(messages, list):
        # Get the last non-empty message
        for message in reversed(messages):
            if isinstance(message, dict):
                content = message.get("content", "").strip()
                if content:
                    return content
    
    return ""

def extract_summary(messages) -> str:
    """Extract summary from agent messages"""
    content = extract_findings(messages)
    
    if not content:
        return ""
    
    # Extract content between SUMMARY_START and SUMMARY_COMPLETE
    start_marker = "SUMMARY_START"
    end_marker = "SUMMARY_COMPLETE"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        return content
    
    summary = content[start_idx + len(start_marker):end_idx].strip()
    return summary
