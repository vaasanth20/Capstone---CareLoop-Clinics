"""Task 4.2: analyse the first 10 notes and save outputs/notes_analysed.csv.

Rules followed:
  - A blank note is never sent to the API. It is recorded as 'skipped_blank'.
  - Each reply is checked with Pydantic and the allowed list.
  - A bad reply does not stop the loop. It is saved as 'invalid', exactly as it came back.
  - A short pause between calls keeps us under the free-tier rate limit.

Run from the project folder:
    python -m part4_genai.analyse_notes
"""
import time

import pandas as pd
from pydantic import ValidationError

from common.paths import DATA_DIR, OUTPUT_DIR
from part4_genai.gemini_client import GeminiClient, ask_for_api_key
from part4_genai.prompts import craft_prompt
from part4_genai.schemas import fields_present, parse_reply

NOTES_TO_ANALYSE = 10
PAUSE_SECONDS = 13      # the free tier allows about 5 requests a minute
OUTPUT_FILE = OUTPUT_DIR / "notes_analysed.csv"


def is_blank(note_text):
    """pandas reads an empty cell as NaN, so check for that first."""
    return pd.isna(note_text) or str(note_text).strip() == ""


def blank_note_row(note):
    return {
        "note_id": note["note_id"], "appointment_id": note["appointment_id"],
        "root_cause": "other", "confidence": 0.0, "summary": "No note recorded",
        "recommended_action": "Re-call patient", "validation_status": "skipped_blank",
        "raw_response": "",
    }


def analyse_one_note(client, note):
    """Return one result row for a note: valid, invalid, or skipped_blank."""
    if is_blank(note["note_text"]):
        return blank_note_row(note)

    try:
        raw_reply = client.ask(craft_prompt(note["note_text"]))
    except Exception as error:      # network or quota problem: record it and carry on
        return {"note_id": note["note_id"], "appointment_id": note["appointment_id"],
                "root_cause": "", "confidence": "", "summary": "", "recommended_action": "",
                "validation_status": "invalid", "raw_response": f"API error: {error}"}

    try:
        insight = parse_reply(raw_reply)
        status = "valid"
        fields = insight.model_dump()
    except (ValueError, ValidationError):
        status = "invalid"
        fields = fields_present(raw_reply)   # copy what is there; leave the rest empty

    return {
        "note_id": note["note_id"], "appointment_id": note["appointment_id"],
        "root_cause": fields.get("root_cause", ""),
        "confidence": fields.get("confidence", ""),
        "summary": fields.get("summary", ""),
        "recommended_action": fields.get("recommended_action", ""),
        "validation_status": status,
        "raw_response": raw_reply,
    }


def main():
    notes = pd.read_csv(DATA_DIR / "followup_notes.csv").head(NOTES_TO_ANALYSE)
    client = GeminiClient(ask_for_api_key())

    rows = []
    for _, note in notes.iterrows():
        rows.append(analyse_one_note(client, note))
        if not is_blank(note["note_text"]):
            time.sleep(PAUSE_SECONDS)

    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_FILE, index=False)
    print(result[["note_id", "root_cause", "validation_status"]].to_string(index=False))
    print(f"\nSaved {OUTPUT_FILE.name}. API calls made: {client.calls_made}")


if __name__ == "__main__":
    main()
