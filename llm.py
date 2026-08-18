"""Gemini LLM API client wrapper with retry and structured output support."""

import os
import time
from typing import Any

from google import genai
from google.genai import errors, types

import config

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def call_llm(system: str, user: str) -> str:
    """Send text prompts to Gemini with retry logic for API rate limits."""
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=system,
                ),
                contents=user,
            )
            return response.text
        except errors.APIError as e:
            if attempt == 4:
                raise e
            time.sleep(5 * (attempt + 1))


def call_llm_structured(system: str, user: str, schema: Any) -> Any:
    """Send text prompts to Gemini requesting a JSON output matching a Pydantic schema."""
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
                contents=user,
            )
            return response.parsed
        except errors.APIError as e:
            if attempt == 4:
                raise e
            time.sleep(5 * (attempt + 1))
