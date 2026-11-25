"""Task 4.1: one validated call on note N001.

Run from the project folder:
    python -m part4_genai.first_call
"""
import json

import pandas as pd

from common.paths import DATA_DIR
from part4_genai.gemini_client import GeminiClient, ask_for_api_key
from part4_genai.prompts import craft_prompt


def main():
    notes = pd.read_csv(DATA_DIR / "followup_notes.csv")
    note = notes.loc[notes["note_id"] == "N001", "note_text"].iloc[0]

    client = GeminiClient(ask_for_api_key())
    reply = client.ask(craft_prompt(note))
    print(json.dumps(json.loads(reply), indent=2))
    print("Expected root_cause: forgot_or_no_reminder")


if __name__ == "__main__":
    main()
