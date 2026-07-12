"""
safety.py — Sakoon AI
Deterministic crisis-keyword/pattern detector — runs on EVERY user message
BEFORE it reaches the Groq LLM. Matches self-harm, harm-to-others, and
acute-crisis language in English, Urdu script, and Roman Urdu. Returns a
boolean flag; does NOT depend on LLM availability or response — this layer
cannot be prompted away.
"""
# Logic implemented in M2
