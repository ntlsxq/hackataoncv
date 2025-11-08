from typing import List, Dict
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


async def generate_interview_reply(
    messages: List[Dict[str, str]],
    model: str | None = None,
) -> str:

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