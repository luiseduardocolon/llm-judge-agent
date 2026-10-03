import os
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

load_dotenv()


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# Local model served by Ollama. Override with LOCAL_MODEL in your environment or .env.
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "CognitiveComputations/dolphin-mistral-nemo:12b")

# When false, skip the Claude judge/enhancer and keep everything local.
USE_CLAUDE_JUDGE = _env_flag("USE_CLAUDE_JUDGE", True)

# Local model via Ollama (OpenAI-compatible API)
local_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama doesn't need a real key
)

# Claude via Anthropic API
claude_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def get_local_draft(query: str) -> str:
    """Step 1: Get a fast local draft from the local model."""
    print(f"\n🔵 {LOCAL_MODEL} drafting response...")
    response = local_client.chat.completions.create(
        model=LOCAL_MODEL,
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content


def get_claude_enhancement(query: str, draft: str) -> dict:
    """Step 2: Claude judges and enhances the draft."""
    print("🟠 Claude reviewing and enhancing...")

    prompt = f"""You are an expert AI judge and editor. A local LLM produced the following draft response to a user query.

USER QUERY: {query}

DRAFT RESPONSE:
{draft}

Your tasks:
1. Score the draft from 1-10 on accuracy, clarity, and completeness
2. Identify any weaknesses or gaps
3. Provide an enhanced version of the response

Format your response exactly like this:
SCORE: [number]/10
WEAKNESSES: [brief bullet points]
ENHANCED RESPONSE:
[your improved response]"""

    response = claude_client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    text_block = next((block for block in response.content if block.type == "text"), None)
    if text_block is None:
        raise ValueError(f"Claude returned no text content (stop_reason: {response.stop_reason})")
    raw = text_block.text

    # Parse the structured response
    lines = raw.split("\n")
    score_line = next((l for l in lines if l.startswith("SCORE:")), "SCORE: N/A")

    enhanced_start = raw.find("ENHANCED RESPONSE:")
    enhanced = raw[enhanced_start + len("ENHANCED RESPONSE:"):].strip() if enhanced_start != -1 else raw

    weaknesses_start = raw.find("WEAKNESSES:")
    weaknesses_end = raw.find("ENHANCED RESPONSE:")
    weaknesses = raw[weaknesses_start + len("WEAKNESSES:"):weaknesses_end].strip() if weaknesses_start != -1 else ""

    return {
        "score": score_line.replace("SCORE:", "").strip(),
        "weaknesses": weaknesses,
        "enhanced": enhanced
    }


def run_agent(query: str):
    """Orchestrate the full judge-enhancer pipeline."""
    print(f"\n{'=' * 60}")
    print(f"QUERY: {query}")
    print(f"{'=' * 60}")

    # Step 1: Local draft
    try:
        draft = get_local_draft(query)
    except Exception as e:
        print(f"\n❌ Failed to get local draft (is Ollama running and is '{LOCAL_MODEL}' pulled?): {e}")
        return
    print(f"\n📝 LOCAL DRAFT ({LOCAL_MODEL}):\n{draft}")

    if not USE_CLAUDE_JUDGE:
        print(f"\n{'=' * 60}\n")
        return

    # Step 2: Claude enhancement
    try:
        result = get_claude_enhancement(query, draft)
    except Exception as e:
        print(f"\n❌ Failed to get Claude enhancement: {e}")
        return

    print(f"\n⚖️  CLAUDE'S SCORE: {result['score']}")
    print(f"\n🔍 WEAKNESSES IDENTIFIED:\n{result['weaknesses']}")
    print(f"\n✅ ENHANCED RESPONSE:\n{result['enhanced']}")
    print(f"\n{'=' * 60}\n")


def main():
    print("🤖 LLM Judge-Enhancer Agent")
    if USE_CLAUDE_JUDGE:
        print(f"Local model: {LOCAL_MODEL} | Judge: Claude Sonnet")
        print("⚠️  Local drafts are sent to Anthropic's API for judging. "
              "Set USE_CLAUDE_JUDGE=false to keep everything local.")
    else:
        print(f"Local model: {LOCAL_MODEL} | Judge: disabled (fully local)")
    print("Type 'quit' to exit\n")

    while True:
        query = input("Ask something: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if query:
            run_agent(query)


if __name__ == "__main__":
    main()
