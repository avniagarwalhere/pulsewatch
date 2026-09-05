import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except Exception:
    client = None

async def generate_morning_brief(digest_events: list, user_name: str) -> str:
    if not client or not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_anthropic_key":
        return f"Good morning {user_name}. (AI mock) The market saw high volume in several sectors and a massive breakout in TSLA."

    prompt = f"""You are summarizing watchlist changes for a retail investor named {user_name}.
Data (JSON): {digest_events}

Write a 3-4 sentence, neutral, plain-English summary of what changed.
- Group related movers by shared cause where the data suggests one.
- Mention any custom alert that was hit.
- Do NOT give buy/sell advice or price predictions.
- If nothing significant happened, say so plainly and briefly."""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

async def generate_headline(symbol, score_result, snapshot) -> str:
    if not client or not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_anthropic_key":
        return f"{symbol} showed unusual activity today."

    prompt = f"""Symbol: {symbol}
Move: {score_result['pct_move']}%
Tags: {score_result['reason_tags']}
Volume vs average: {snapshot.get('volume', 1) / max(snapshot.get('avg_volume_30d', 1), 1):.1f}x

Write ONE short factual sentence (under 20 words) describing this change. No advice, no speculation beyond the data given."""
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=40,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
