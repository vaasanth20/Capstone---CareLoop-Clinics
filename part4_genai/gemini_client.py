"""A small wrapper around the Gemini API.

The API key is typed when the script runs (hidden input). It is never written to a file.
The wrapper counts every call, so the scripts can report how many they made.
"""
import getpass

from google import genai
from google.genai import types

from part4_genai.prompts import SYSTEM_INSTRUCTION

# Use the Flash model name shown in your Session 22.1 notebook or in AI Studio.
MODEL_NAME = "gemini-2.5-flash"

# Forces the reply into this shape (JSON mode with a schema).
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "root_cause": {"type": "string"},
        "confidence": {"type": "number"},
        "summary": {"type": "string"},
        "recommended_action": {"type": "string"},
    },
    "required": ["root_cause", "confidence", "summary", "recommended_action"],
}


def ask_for_api_key():
    return getpass.getpass("Paste your Gemini API key (input is hidden): ")


class GeminiClient:
    def __init__(self, api_key):
        self._client = genai.Client(api_key=api_key)
        self.calls_made = 0

    def ask(self, prompt):
        """Send one prompt and return the reply text (JSON as a string)."""
        self.calls_made += 1
        response = self._client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0,
                max_output_tokens=1000,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                # Session 22.1 setting. If your model rejects it, delete this line.
                thinking_config=types.ThinkingConfig(thinking_level="minimal"),
            ),
        )
        return response.text
