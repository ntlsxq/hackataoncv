import json
import re
from typing import List, Dict, Tuple
import asyncio

from google import genai
from google.genai import types

from src.config import settings


# Инициализация Gemini-клиента
client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def _generate_with_gemini(
    model: str,
    system_instruction: str,
    prompt: str,
    temperature: float = 0.4,
) -> str:

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
    )

    def _call():
        return client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

    response = await asyncio.to_thread(_call)
    return response.text


from typing import List, Dict

async def generate_interview_reply(
    messages: List[Dict[str, str]],
    model: str | None = None,
) -> str:
    has_assistant_messages = any(m.get("role") == "assistant" for m in messages)

    if not has_assistant_messages:
        return "Hello! What position are you applying for?"

    if model is None:
        model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    system_instruction: str | None = None
    conversation_lines: List[str] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system":
            if system_instruction is None:
                system_instruction = content
            else:
                conversation_lines.append(f"SYSTEM: {content}")
        else:
            conversation_lines.append(f"{role.upper()}: {content}")

    if system_instruction is None:
        system_instruction = (
            "You are a professional technical interviewer. "
            "Ask follow-up questions, assess answers and provide concise feedback."
        )

    prompt = "\n".join(conversation_lines)

    return await _generate_with_gemini(
        model=model,
        system_instruction=system_instruction,
        prompt=prompt,
        temperature=0.4,
    )


async def generate_chat_title(
    messages: List[Dict[str, str]],
    model: str | None = None,
) -> str:
    if model is None:
        model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    conversation_lines: List[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            continue
        conversation_lines.append(f"{role.upper()}: {content}")

    if not conversation_lines:
        conversation_lines.append("USER: Interview starts.")

    prompt = "\n".join(conversation_lines)

    system_instruction = (
        "Generate a short, clear headline for this interview chat."
        "Maximum 7 words. No quotation marks or unnecessary comments."
        "Just display one headline."
    )

    title = await _generate_with_gemini(
        model=model,
        system_instruction=system_instruction,
        prompt=prompt,
        temperature=0.3,
    )

    return title.strip()


async def score_resume_json(
    resume: dict | list | str,
) -> Tuple[int, str]:
    model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    if isinstance(resume, (dict, list)):
        resume_json_str = json.dumps(resume, ensure_ascii=False, indent=2)
    else:
        resume_json_str = str(resume)

    system_instruction = (
        "You are a strict technical recruiter. "
        "You will receive a candidate's resume as JSON. "
        "Evaluate the overall quality of the candidate and their suitability "
        "for a strong software engineering role on a scale from 1 to 100. "
        "1 = very poor candidate, 100 = outstanding candidate.\n\n"
        "Respond ONLY with a JSON object of the form:\n"
        '{"score": <integer 1-100>, "reason": "<short explanation>"}\n'
        "Do not include any other text, no markdown, no code fences."
    )

    prompt = (
        "Here is the candidate resume as JSON:\n"
        f"```json\n{resume_json_str}\n```"
    )

    raw = await _generate_with_gemini(
        model=model,
        system_instruction=system_instruction,
        prompt=prompt,
        temperature=0.2,
    )

    text = raw.strip()

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        raise ValueError(f"Cannot find JSON in Gemini response: {text!r}")

    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Cannot parse JSON from Gemini response: {text!r}") from e

    if "score" not in data:
        raise ValueError(f"No 'score' field in Gemini response: {data!r}")

    score = int(data["score"])
    score = max(1, min(100, score))

    reason = str(data.get("reason", "")).strip()

    return score, reason