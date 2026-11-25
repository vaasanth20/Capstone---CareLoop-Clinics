# Part 4: reading call-centre notes with Gemini

The notes say *why* patients missed a visit. This part asks Gemini to put each note into one of six fixed categories, then checks every reply before trusting it.

## The key rule

Gemini's replies are never trusted on their own. Each reply goes through three checks, and any failure is recorded rather than repaired.

1. The text must be valid JSON.
2. The fields must have the right types and ranges (Pydantic).
3. `root_cause` must be one of the six allowed values.

## `prompts.py`

Holds the wording sent to Gemini, in one place.

- **`ALLOWED_ROOT_CAUSES`** is the list of six categories. The same list is used in the prompt and in the check.
- **`craft_prompt(note_text)`** builds the full prompt in five labelled parts: Context, Role, Action, Tone, Format. It also tells the model to answer `other` rather than guess when a note is unclear.
- **`simple_prompt(note_text)`** is a deliberately weak prompt, used in the stress test to show the difference.

## `schemas.py`

- **`FollowupInsight`** is a Pydantic model. `confidence` must be between 0 and 1, and the text fields must have minimum lengths.
- **`check_allowed(insight)`** handles the one rule Pydantic cannot: `root_cause` must be in the allowed list. It is a plain string, so Pydantic cannot know the list.
- **`parse_reply(text)`** runs all three checks in order and returns the valid insight, or raises an error.
- **`fields_present(text)`** copies whatever fields a bad reply did contain, so the output shows what came back. It never fills in or corrects a field.

## `gemini_client.py`

- **`ask_for_api_key()`** asks for the key with a hidden prompt. The key is never written to a file.
- **`GeminiClient`** wraps the API. `ask(prompt)` sends one request and returns the reply text. The request asks for JSON with a fixed schema, at temperature 0 so the answers are repeatable. It also counts calls, so the scripts can report how many were used.

## `first_call.py` (Task 4.1)

One call on note N001, printed in full. The reply should be `forgot_or_no_reminder`.

## `analyse_notes.py` (Task 4.2)

Analyses the first 10 notes and saves `outputs/notes_analysed.csv`.

- **`is_blank(note_text)`** checks for missing or whitespace-only notes. pandas reads an empty cell as `NaN`, which has no `.strip()`, so `pd.isna` is checked first.
- **`blank_note_row`** records a blank note as `skipped_blank` without calling the API. This saves a call and keeps the row in the output.
- **`analyse_one_note(client, note)`** calls the API, then runs the three checks. A reply that fails a check is saved as `invalid` with its raw text, so nothing is hidden. An error from the network is caught too, so one failure cannot stop the loop.
- A 13-second pause after each real call keeps the script under the free-tier limit.

## `stress_test.py` (Task 4.3)

- **Part (a)** sends two bad replies into Pydantic and prints the errors. This needs no API key. Run it with `--offline` to do only this part.
- **Part (b)** runs two notes (N007 and N009) through both the simple prompt and the CRAFT prompt. The table shows whether each reply uses an allowed category, so you can see which prompt you would deploy.

## `crosstab.py` (Task 4.4)

Joins each note's reason to its booking, then counts reasons against `reminder_sent`. The question it answers: do patients who said "forgot" have bookings where no reminder was sent? The result is saved to `outputs/root_cause_by_reminder.csv`.
