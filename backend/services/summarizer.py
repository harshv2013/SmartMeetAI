import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"


PROMPT_TEMPLATE = """You are SmartMeetAI, an expert meeting analyst and summarizer.

You will receive a full meeting transcript. Analyze it carefully and return **only valid JSON**
(no prose, no Markdown, no explanations) using this schema:

{{
  "summary": "A detailed multi-paragraph summary of the meeting covering all key points, examples, and discussions.",
  "key_topics": ["Major topics covered in the meeting"],
  "decisions": ["List of important decisions taken"],
  "action_items": ["Tasks or follow-ups assigned to participants"],
  "sentiment": "positive|neutral|negative"
}}

Make sure the summary is rich in detail — include what each speaker discussed,
examples, and the overall flow of the conversation.

Transcript:
{transcript}

Give output in json format, no extra keyword explaing it.
"""

def _force_json(text: str):
    """
    Tries hard to extract and fix JSON-like output from Ollama responses.
    Handles cases where JSON is truncated, nested, or malformed.
    """
    # Step 1: Clean up leading/trailing whitespace or quotes
    text = text.strip().strip("`").strip()

    # Step 2: If it looks like JSON but missing a closing brace, try to fix it
    if text.count("{") > text.count("}"):
        text = text + "}" * (text.count("{") - text.count("}"))

    # Step 3: Direct parse attempt
    try:
        obj = json.loads(text)
        # handle nested summary JSON
        if isinstance(obj, dict) and "summary" in obj and isinstance(obj["summary"], str):
            try:
                inner = json.loads(obj["summary"])
                if isinstance(inner, dict) and "summary" in inner:
                    obj = inner
            except Exception:
                pass
        return obj
    except json.JSONDecodeError:
        pass

    # Step 4: Try to extract first {...} block and auto-close it if needed
    match = re.search(r"\{.*", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        # Auto-close braces if truncated
        if candidate.count("{") > candidate.count("}"):
            candidate += "}" * (candidate.count("{") - candidate.count("}"))
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Step 5: Graceful fallback
    return {
        "summary": text[:500].strip(),
        "key_topics": [],
        "decisions": [],
        "action_items": [],
        "sentiment": "neutral"
    }


def _truncate_for_model(s: str, max_chars: int = 8000) -> str:
    # Simple guard against huge transcripts for small models
    return s if len(s) <= max_chars else s[:max_chars]

def summarize_transcript(transcript_text: str, model: str = DEFAULT_MODEL, timeout: int = 600):
    print(f"summarize called")
    """
    Call Ollama to summarize a transcript into structured JSON.
    """
    # prompt = PROMPT_TEMPLATE.format(transcript=_truncate_for_model(transcript_text))
    prompt = PROMPT_TEMPLATE.format(transcript=transcript_text)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    print(f"resp.text : {resp.text}")
    if resp.status_code != 200:
        raise RuntimeError(f"Ollama error {resp.status_code}: {resp.text}")

    # Ollama returns JSON with a "response" field that is text (which *should* be JSON)
    raw = resp.json().get("response", "").strip()
    print(f"raw: {raw}")
    return _force_json(raw)
