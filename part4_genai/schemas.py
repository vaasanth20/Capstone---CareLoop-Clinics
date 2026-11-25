"""Checking Gemini's reply with Pydantic (Task 4.2).

parse_reply() does three checks in order:
  1. The text is valid JSON.
  2. The fields have the right types and ranges (Pydantic).
  3. root_cause is one of the allowed values.
Any failure raises an error, and the caller records the reply as 'invalid'.
"""
import json

from pydantic import BaseModel, Field

from part4_genai.prompts import ALLOWED_ROOT_CAUSES


class FollowupInsight(BaseModel):
    root_cause: str = Field(min_length=3)
    confidence: float = Field(ge=0, le=1)
    summary: str = Field(min_length=5)
    recommended_action: str = Field(min_length=5)


def check_allowed(insight):
    """The allowed-list check. Pydantic cannot do it here because root_cause is a plain string."""
    if insight.root_cause not in ALLOWED_ROOT_CAUSES:
        raise ValueError(f"root_cause '{insight.root_cause}' is not in the allowed list")


def parse_reply(reply_text):
    """Parse and check one reply. Returns a FollowupInsight or raises an error."""
    data = json.loads(reply_text)
    insight = FollowupInsight(**data)
    check_allowed(insight)
    return insight


def fields_present(reply_text):
    """Copy whatever fields the reply did contain, even if it is invalid. Never repairs anything."""
    try:
        data = json.loads(reply_text)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}
