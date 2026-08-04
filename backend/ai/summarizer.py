"""Document summarization via Google's Gemini API."""
import logging
import os

import google.generativeai as genai

logger = logging.getLogger("preserve_ai.ai")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
INPUT_CHAR_LIMIT = int(os.getenv("SUMMARY_INPUT_CHAR_LIMIT", "15000"))

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PROMPTS = {
    "short": (
        "Summarize the following academic document in exactly 1-2 sentences, "
        "capturing only its core topic. Do not include any preamble like "
        "'This document is about' — start directly with the content.\n\n{text}"
    ),
    "medium": (
        "Summarize the following academic document in one concise paragraph "
        "(roughly 4-6 sentences), covering its main topics and key points. "
        "Do not include any preamble.\n\n{text}"
    ),
    "detailed": (
        "Write a detailed, structured summary of the following academic document. "
        "Cover the main sections, key concepts, and important details a student "
        "would need to decide whether to read the full document. Use short "
        "paragraphs. Do not include any preamble.\n\n{text}"
    ),
}


class SummarizationError(Exception):
    pass


def generate_summary(text: str, summary_type: str) -> str:
    if not GEMINI_API_KEY:
        raise SummarizationError("GEMINI_API_KEY is not configured")

    if summary_type not in PROMPTS:
        raise SummarizationError(f"Unknown summary type: {summary_type}")

    truncated_text = text[:INPUT_CHAR_LIMIT]
    prompt = PROMPTS[summary_type].format(text=truncated_text)

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini summarization failed (%s): %s", summary_type, exc)
        raise SummarizationError(str(exc)) from exc