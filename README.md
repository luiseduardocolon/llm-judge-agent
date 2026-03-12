# LLM Judge-Enhancer Agent

A hybrid AI pipeline that combines a **local open-source LLM** (Mistral 7B via Ollama) 
with the **Claude API** acting as an intelligent judge-enhancer agent.

## How It Works

1. User submits a query
2. **Mistral 7B** (running locally) generates a fast draft response
3. **Claude Sonnet** evaluates the draft — scoring it, identifying weaknesses, 
   and producing an enhanced version
4. Both outputs are displayed for comparison

This implements a **judge-enhancer agent pattern**, a common architecture in 
production LLM systems for quality assurance and cost optimization.

## Tech Stack

- Python 3.x
- [Ollama](https://ollama.com) — local LLM inference
- Mistral 7B — local open-source model
- Anthropic Claude API — judge/enhancer agent
- PyCharm — IDE

## Setup

1. Install [Ollama](https://ollama.com) and pull Mistral:
```bash
ollama pull mistral
```

2. Clone this repo and install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_key_here
```

4. Run the agent:
```bash
python agent.py
```

## Why This Architecture?

Local models are fast and free to run but vary in quality. Cloud models like Claude 
are highly capable but have per-token costs. This pipeline gets the best of both: 
Mistral handles the initial generation cheaply, and Claude only intervenes to 
evaluate and improve — a pattern used in production AI systems for cost efficiency 
and quality control.
