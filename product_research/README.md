# AutoGen Product Research

This project implements an automated product research system using Microsoft's AutoGen framework. It uses AI agents to search, analyze, and synthesize market and technical information from multiple sources to create comprehensive product research reports.

## Features

- Multi-agent research team:
  - Research Lead: Coordinates research and synthesizes findings
  - Data Analyst: Focuses on market data and trends
  - Technical Researcher: Analyzes technical aspects and innovations
  - QA Reviewer: Validates research content for accuracy and completeness
- Multiple data sources:
  - Perplexity AI for market research
  - Serper API for fact-checking
  - arXiv for technical research
- Robust research process:
  - Iterative content validation
  - QA feedback loop for improvements
  - Maximum retry attempts for quality control
- JSON-based memory management for persistent storage
- Automated report generation with executive summaries

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up required API keys:

Create a file named `.env` with your API keys:
```bash
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key
SERPER_API_KEY=your-serper-key
```

3. Create an OpenAI API key configuration:
Create a file named `OAI_CONFIG_LIST` with your OpenAI API key:
```json
[
    {
        "model": "gpt-4o-mini",
        "api_key": "your-api-key-here"
    }
]
```

## Usage

Run the research agent with a topic:
```bash
python app.py "your research topic"
```

For example:
```bash
python app.py "AI code generation market and technology trends"
```

The agent will:
1. Research market size and growth rates using Perplexity AI
2. Identify key players and their market share
3. Analyze market trends and developments
4. Research technical innovations using arXiv
5. Validate content through QA review
6. Generate an executive summary
7. Create a detailed markdown report

## Output

The system generates several outputs:
- JSON memory files in `research_memory/` for persistent storage
- Markdown reports in `reports/` with:
  - Executive summary
  - Market size analysis
  - Competitor analysis
  - Trend analysis
  - Technical analysis
  - Recommendations

## Architecture

The system uses:
- AutoGen for multi-agent orchestration
- Perplexity AI for market research
- Serper API for fact-checking
- arXiv API for technical research
- JSON-based memory management for data persistence
- Markdown report generation for clean output

## Dependencies

Required Python packages:
```
autogen>=0.2
python-dotenv
requests
arxiv
```

## Error Handling

The system includes:
- Maximum retry attempts for research validation
- QA feedback loop for content improvement
- Clear error messages and logging
- Graceful fallback for API failures

## Debugging

The system provides detailed console output showing:
- Research team discussions
- Content validation status
- QA feedback
- Error messages and warnings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
