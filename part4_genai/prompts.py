"""The prompts sent to Gemini, kept in one place so they are easy to read and change.

Two prompts are used:
  craft_prompt  the full CRAFT prompt (Context, Role, Action, Tone, Format). Used for all notes.
  simple_prompt the bare 'Classify this note' prompt, used only to compare in the stress test.
"""

ALLOWED_ROOT_CAUSES = [
    "forgot_or_no_reminder",
    "distance_or_transport",
    "cost_or_fee",
    "illness_or_emergency",
    "work_or_schedule",
    "other",
]

SYSTEM_INSTRUCTION = "You classify why a patient missed a clinic appointment. Reply with JSON only."


def craft_prompt(note_text):
    """A CRAFT prompt: context, role, action, tone and format, then the note itself."""
    allowed = ", ".join(ALLOWED_ROOT_CAUSES)
    return (
        # Context: where the note comes from
        "Context: CareLoop Clinics is an Indian outpatient clinic chain. A call-centre agent "
        "phoned a patient who missed an appointment and wrote a short note. Notes may be in "
        "English or Hinglish.\n"
        # Role: who is answering
        "Role: You are a careful analyst who codes the reason for missed visits.\n"
        # Action: what to do, including the rule for doubtful notes
        f"Action: Choose exactly one root_cause from this list: {allowed}. "
        "If the note does not clearly fit one of the categories, answer other rather than guess. "
        "Give a confidence between 0 and 1, a summary of at most 25 words, and one recommended_action.\n"
        # Tone
        "Tone: neutral and factual.\n"
        # Format
        "Format: JSON with the keys root_cause, confidence, summary and recommended_action.\n\n"
        f"Note: {note_text}"
    )


def simple_prompt(note_text):
    """The bare prompt (V1) used to show what a weak prompt does."""
    return f"Classify this note: {note_text}"
