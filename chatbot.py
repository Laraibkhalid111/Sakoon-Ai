"""
chatbot.py — Sakoon AI
Groq API client wrapper: builds the structured LLM request using JSON mode
(response_format={"type": "json_object"}), parses and validates the JSON
response with fallback defaults, and exposes a single function used by
app.py on every user turn.
"""
# Logic implemented in M1
