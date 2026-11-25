"""Task 4.3: break the validation on purpose, then compare two prompts.

(a) Two bad replies go into Pydantic. Each error is caught and printed. No API needed.
(b) Notes N007 (Hinglish) and N009 (ambiguous) are sent with the simple prompt (V1) and
    the CRAFT prompt (V2). Temperature 0 and the same settings for both.

Run from the project folder:
    python -m part4_genai.stress_test            (part a only: add --offline)
"""
import json
import sys
import time

import pandas as pd
from pydantic import ValidationError

from common.paths import DATA_DIR
from part4_genai.gemini_client import GeminiClient, ask_for_api_key
from part4_genai.prompts import ALLOWED_ROOT_CAUSES, craft_prompt, simple_prompt
from part4_genai.schemas import FollowupInsight

COMPARE_NOTES = ["N007", "N009"]
PAUSE_SECONDS = 13


def show_validation_errors():
    print("== (a) Two deliberately bad replies ==")
    bad_replies = {
        "confidence = 1.7": {"root_cause": "other", "confidence": 1.7,
                             "summary": "Test summary here", "recommended_action": "Call back"},
        "missing recommended_action": {"root_cause": "other", "confidence": 0.5,
                                       "summary": "Test summary here"},
    }
    for label, data in bad_replies.items():
        try:
            FollowupInsight(**data)
            print(f"{label}: no error (this is unexpected)")
        except ValidationError as error:
            print(f"{label}: caught. Pydantic says:")
            print(error, "\n")


def compare_prompts(client):
    print("== (b) V1 (simple) versus V2 (CRAFT) at temperature 0 ==")
    notes = pd.read_csv(DATA_DIR / "followup_notes.csv").set_index("note_id")
    rows = []
    for note_id in COMPARE_NOTES:
        note_text = notes.loc[note_id, "note_text"]
        for name, build_prompt in [("V1", simple_prompt), ("V2", craft_prompt)]:
            reply = client.ask(build_prompt(note_text))
            try:
                root_cause = json.loads(reply).get("root_cause", "")
            except (ValueError, AttributeError):
                root_cause = "(reply was not a JSON object)"
            rows.append({"note": note_id, "prompt": name, "root_cause": root_cause,
                         "allowed": root_cause in ALLOWED_ROOT_CAUSES})
            time.sleep(PAUSE_SECONDS)
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    show_validation_errors()
    if "--offline" in sys.argv:
        return
    client = GeminiClient(ask_for_api_key())
    compare_prompts(client)
    print(f"\nAPI calls made in this script: {client.calls_made}")


if __name__ == "__main__":
    main()
