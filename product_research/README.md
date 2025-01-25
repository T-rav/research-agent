# AutoGen Product Research

This project implements an automated product research system using Microsoft's AutoGen framework. It uses AI agents to search, analyze, and synthesize market and technical information from Perplexity AI to create comprehensive product research reports.

## Features

- Perplexity AI integration for market research
- Multi-agent system for specialized research tasks:
  - Market size analysis
  - Key player identification
  - Market trends analysis
  - Technical innovation research
- JSON-based memory management for persistent storage
- Automated report generation with executive summaries

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create an OpenAI API key configuration:
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
1. Research market size and growth rates
2. Identify key players and their market share
3. Analyze market trends and developments
4. Research technical innovations
5. Generate an executive summary
6. Create a detailed markdown report

## Output

The system generates several outputs:
- JSON memory files in `research_memory/` for persistent storage
- Markdown reports in `reports/` with:
  - Executive summary
  - Key findings
  - Market opportunities
  - Recommendations

## Architecture

The system uses:
- AutoGen for multi-agent orchestration
- Perplexity AI for market research
- JSON-based memory management for data persistence
- Markdown report generation for clean output

## Dependencies

- Python 3.8+
- AutoGen
- Other dependencies listed in `requirements.txt`
