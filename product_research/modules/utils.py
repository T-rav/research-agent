def extract_findings(messages):
    """Extract findings from agent messages"""
    if not messages:
        return ""
    
    # Get messages in reverse order
    messages = list(reversed(messages))
    
    # Debug print
    print("\nDEBUG Messages:")
    for msg in messages:
        content = msg.get("content", "")
        if content:
            content_preview = content[:100] + "..."
        else:
            content_preview = "<no content>"
        print(f"Role: {msg.get('role')}, Content: {content_preview}")
        
        # Check for function call results
        function_call = msg.get("function_call")
        if function_call:
            print(f"Function call: {function_call.get('name')}")
            print(f"Function result: {msg.get('function_call_result', '<no result>')[:100]}...")
    
    # Get the last function call result first
    for msg in messages:
        result = msg.get("function_call_result")
        if result and isinstance(result, str):
            return result.strip()
    
    # Fall back to last assistant message if no function results
    for msg in messages:
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, str):
                return content.strip()
    return ""

def extract_summary(messages):
    """Extract summary from agent messages"""
    if not messages:
        return ""
    
    # Get messages in reverse order
    messages = list(reversed(messages))
    
    # Debug print
    print("\nDEBUG Messages:")
    for msg in messages:
        content = msg.get("content", "")
        if content:
            content_preview = content[:100] + "..."
        else:
            content_preview = "<no content>"
        print(f"Role: {msg.get('role')}, Content: {content_preview}")
        
        # Check for function call results
        function_call = msg.get("function_call")
        if function_call:
            print(f"Function call: {function_call.get('name')}")
            print(f"Function result: {msg.get('function_call_result', '<no result>')[:100]}...")
    
    # For summary, we still want the assistant message with tags
    for msg in messages:
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, str):
                if "<SUMMARY>" in content:
                    start = content.find("<SUMMARY>") + len("<SUMMARY>")
                    end = content.find("SUMMARY_COMPLETE")
                    if end != -1:
                        return content[start:end].strip()
                return content.strip()
    return ""
