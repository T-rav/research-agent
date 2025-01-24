import os
from openai import OpenAI
import arxiv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def perplexity_search(query: str, num_results: int = 2) -> str:
    """
    Search using Perplexity AI API via OpenAI client
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return "Error: Perplexity API key not found in environment variables"

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        
        print(f"Debug: Sending query to Perplexity API: {query}")
        response = client.chat.completions.create(
            model="sonar",  # Using the standard Perplexity model
            messages=[
                {
                    "role": "system",
                    "content": """You are a specialized market research assistant. Your responses should:
                    1. Focus on reliable sources like industry reports, market analyses, and academic research
                    2. Always include sources and citations for data points
                    3. Prioritize recent data and statistics
                    4. Indicate if data is estimated or projected
                    5. Compare multiple sources when possible
                    6. Include URLs or references to original sources
                    Format your response with clear sections and bullet points."""
                },
                {
                    "role": "user",
                    "content": f"{query}\n\nPlease include sources and citations for all data points and statistics."
                }
            ]
        )
        
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            print(f"Debug: Got response: {result}")
            return result
        else:
            return "No results found"
            
    except Exception as e:
        print(f"Debug: Error in perplexity_search: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error in perplexity_search: {str(e)}"

def arxiv_search(query: str, max_results: int = 3) -> str:
    """
    Search Arxiv for papers and return the results including abstracts
    """
    client = arxiv.Client()
    
    # Add relevant categories to the search
    categories = ["cs.RO", "cs.AI", "cs.HC"]  # Robotics, AI, Human-Computer Interaction
    category_filter = " OR ".join(f"cat:{cat}" for cat in categories)
    
    # Enhance query with category filter
    enhanced_query = f"({query}) AND ({category_filter})"
    
    search = arxiv.Search(
        query=enhanced_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    formatted_results = []
    for paper in client.results(search):
        # Calculate citation impact if available
        citation_info = ""
        
        paper_info = (
            f"Title: {paper.title}\n"
            f"Authors: {', '.join(author.name for author in paper.authors)}\n"
            f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            f"Categories: {', '.join(paper.categories)}\n"
            f"Abstract: {paper.summary}\n"
            f"PDF URL: {paper.pdf_url}\n"
            f"{citation_info}"
        )
        formatted_results.append(paper_info)

    if not formatted_results:
        return "No papers found matching the query."
        
    return "\n\n".join(formatted_results)
