import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You turn articles into a short two-host podcast-style dialogue.
Hosts are named Alex and Sam. Alex introduces the topic and asks questions; Sam explains
and adds color. Keep it conversational, not a dry summary. Target 60-90 seconds of spoken
audio (roughly 150-220 words total). Return ONLY valid JSON: a list of objects with
"speaker" ("alex" or "sam") and "line" (the spoken text), nothing else."""


def generate_dialogue(article_text: str) -> list[dict]:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": article_text[:8000]}],
    )

    raw = next(block.text for block in response.content if block.type == "text").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw

    return json.loads(raw)
