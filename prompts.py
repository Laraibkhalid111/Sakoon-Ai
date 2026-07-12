"""
prompts.py — Sakoon AI
All system/task prompt templates and the JSON response schema string for the
Groq JSON-mode call. Kept separate from chatbot.py for clean organization.
Covers: persona, scope lock, bilingual behavior, one-thing-at-a-time question
flow, conversation_stage state machine, and the exact JSON output schema from
IDEA.md §7.
"""
# Logic implemented in M1
