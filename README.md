# LLM Judge-Enhancer Agent

A hybrid AI pipeline that combines a **local open-source LLM** (served by Ollama; 
defaults to Dolphin Mistral Nemo 12B) with the **Claude API** acting as an intelligent 
judge-enhancer agent. Both the local model and the Claude judge step are configurable.

## How It Works

1. User submits a query
2. The **local model** (running via Ollama) generates a fast draft response
3. **Claude Sonnet** (optional, on by default) evaluates the draft — scoring it, 
   identifying weaknesses, and producing an enhanced version
4. Both outputs are displayed for comparison

This implements a **judge-enhancer agent pattern**, a common architecture in 
production LLM systems for quality assurance and cost optimization.

## Error Handling

Each pipeline step is wrapped in its own error handling so a single failure 
doesn't crash the interactive session:

- If Ollama isn't running or the local draft call fails, the agent prints a 
  clear error and returns to the prompt instead of crashing.
- If the Claude call fails, or returns no usable text (e.g. it uses its full 
  token budget on extended thinking and never emits a text block), the agent 
  reports the failure — including the API's `stop_reason` when available — 
  rather than throwing an unhandled exception.

## Tech Stack

- Python 3.x
- [Ollama](https://ollama.com) — local LLM inference
- Local open-source model via Ollama (default: Dolphin Mistral Nemo 12B)
- Anthropic Claude API — judge/enhancer agent (optional)
- PyCharm — IDE

## Setup

1. Install [Ollama](https://ollama.com) and pull the default local model:
```bash
ollama pull hf.co/dphn/dolphin-2.9.3-mistral-nemo-12b-gguf:Q4_K_M
```
Any Ollama model works; see [Configuration](#configuration).

> Note: the `CognitiveComputations/dolphin-mistral-nemo` model in the Ollama library 
> fails to load on current Ollama (`unknown pre-tokenizer type: 'dolphin12b'`), so the 
> official fixed GGUF from Hugging Face is used instead.

2. Clone this repo and install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Anthropic API key (and any optional settings):
```
ANTHROPIC_API_KEY=your_key_here
```

4. Run the agent:
```bash
python agent.py
```

## Configuration

Set these in your environment or `.env` (which is git-ignored):

| Variable | Default | Description |
| --- | --- | --- |
| `LOCAL_MODEL` | `hf.co/dphn/dolphin-2.9.3-mistral-nemo-12b-gguf:Q4_K_M` | Ollama model tag used for the local draft |
| `USE_CLAUDE_JUDGE` | `true` | Set to `false` to skip the Claude judge and keep everything local |

Example: run fully local with the stock model:
```
LOCAL_MODEL=mistral
USE_CLAUDE_JUDGE=false
```

**Privacy note:** when `USE_CLAUDE_JUDGE` is `true`, each local draft is sent to 
Anthropic's API and is subject to Anthropic's usage policies. Claude may also decline 
or rewrite content it considers out of policy. If you are generating content you 
want to keep local, set `USE_CLAUDE_JUDGE=false`.

Some community models are uncensored. You are responsible for the content you 
generate with them.

## Why This Architecture?

Local models are fast and free to run but vary in quality. Cloud models like Claude 
are highly capable but have per-token costs. This pipeline gets the best of both: 
the local model handles the initial generation cheaply, and Claude only intervenes to 
evaluate and improve — a pattern used in production AI systems for cost efficiency 
and quality control.
