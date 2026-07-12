"""
safety.py — Sakoon AI
Deterministic crisis-keyword/pattern detector. Runs on EVERY user message
BEFORE it reaches Groq. Independent of LLM availability — cannot be prompted away.
Full implementation in M2. Stub returns False so M1 app runs cleanly.
"""


def check_crisis(text: str) -> bool:
    """
    Returns True if the message contains crisis-level language.
    Stub for M1 — always returns False. Full patterns added in M2.
    """
    return False
