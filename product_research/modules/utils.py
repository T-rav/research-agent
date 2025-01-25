def extract_findings(messages):
    """Extract findings from agent messages"""
    for msg in messages:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str):
            # First try to find content between tags
            if "<FINDINGS>" in content:
                start = content.find("<FINDINGS>") + len("<FINDINGS>")
                end = content.find("TERMINATE")
                if end != -1:
                    return content[start:end].strip()
            
            # If no tags found but we got a response, return the whole content
            if content.strip():
                return content.strip()
    return ""

def extract_summary(messages):
    """Extract summary from agent messages"""
    for msg in messages:
        content = msg.get("content", "")
        if msg["role"] == "assistant" and isinstance(content, str) and "<SUMMARY>" in content:
            start = content.find("<SUMMARY>") + len("<SUMMARY>")
            end = content.find("SUMMARY_COMPLETE")
            if end != -1:
                return content[start:end].strip()
    return ""
