# AutoGen Literature Review

This project implements an automated literature review system using Microsoft's AutoGen framework. It uses multiple AI agents to search, analyze, and synthesize information from both Perplexity AI and arXiv to create comprehensive literature reviews.

## Features

- Perplexity AI integration for web content search
- arXiv integration for academic papers
- Multi-agent system with specialized roles:
  - Perplexity Search Agent
  - arXiv Search Agent
  - Report Generation Agent
- Automated synthesis of information into a coherent literature review

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your API keys:
```
PERPLEXITY_API_KEY=your_perplexity_api_key
OPENAI_API_KEY=your_openai_api_key
```

3. Create an `OAI_CONFIG_LIST` file with your OpenAI configuration:
```json
[
    {
        "model": "gpt-4",
        "api_key": "your_openai_api_key"
    }
]
```

## Usage

Run the script with your desired research topic:

```python
python app.py
```

By default, it will generate a literature review on "no code tools for building multi agent AI systems". You can modify the topic in the script by changing the `topic` variable at the bottom of the file.

## How it Works

1. The system creates three specialized agents:
   - Perplexity Search Agent: Searches the web for relevant information using Perplexity AI
   - arXiv Search Agent: Searches academic papers
   - Report Agent: Synthesizes information into a coherent review

2. The agents work together in a round-robin fashion to:
   - Gather information from multiple sources
   - Analyze and synthesize the information
   - Generate a comprehensive literature review

3. The final report includes proper citations and references to both web and academic sources.

## Requirements

- Python 3.7+
- Perplexity API key
- OpenAI API key
- Internet connection for web and arXiv searches
