"""
safety.py — Sakoon AI
Deterministic crisis-keyword/pattern detector. Matches self-harm, harm-to-others,
and acute-crisis language across English, Urdu script, and Roman Urdu.
Runs on EVERY user message BEFORE it reaches the Groq LLM.
Returns a boolean flag. This layer cannot be bypassed or prompted away.
"""

import re

# Comprehensive list of regex patterns for crisis detection
# Matches keywords with word boundaries to avoid false positives (e.g. "side" matching "suicide")
CRISIS_PATTERNS = [
    # --- English ---
    r"\bsuicide\b",
    r"\bself[- ]?harm\b",
    r"\bkill myself\b",
    r"\bkilling myself\b",
    r"\bend my life\b",
    r"\bwant to die\b",
    r"\bwish i was dead\b",
    r"\bbetter off dead\b",
    r"\bhurt(?:ing)? myself\b",
    r"\bcut(?:ting)? myself\b",
    r"\boverdose\b",
    r"\bdon't want to live\b",
    r"\bdo not want to live\b",
    r"\bno reason to live\b",
    
    # --- Roman Urdu ---
    r"\bkhud[- ]?kushi\b",
    r"\bkhud[- ]?khushi\b",
    r"\bmarna chahta\b",
    r"\bmarna chahti\b",
    r"\bmarna hai\b",
    r"\bmar jana\b",
    r"\bmar jaane\b",
    r"\bmar jaon\b",
    r"\bmar jaoon\b",
    r"\bjaan de(ni|ne)?\b",
    r"\bzindagi khatam\b",
    r"\bapne aap ko nuksan\b",
    r"\bapnay aap ko nuksan\b",
    r"\bapni jaan\b",
    
    # --- Urdu Script (Unicode range) ---
    r"خودکشی",
    r"خود کشی",
    r"مرنا چاہتا",
    r"مرنا چاہتی",
    r"جان دے",
    r"زندگی ختم",
    r"خود کو نقصان",
    r"مر جاؤں",
    r"مر جانا",
    r"مجھے مرنا",
    r"مار ڈالوں",
    r"مارنا چاہتا",
    r"مارنا چاہتی",
]

# Compile patterns for efficiency and case-insensitivity
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in CRISIS_PATTERNS]


def check_crisis(text: str) -> bool:
    """
    Scan the input text against all compiled crisis regex patterns.
    Returns True if any pattern matches, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    
    # Normalize whitespace
    normalized_text = " ".join(text.split())
    
    for pattern in COMPILED_PATTERNS:
        if pattern.search(normalized_text):
            return True
            
    return False
