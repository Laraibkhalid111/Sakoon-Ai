"""
report.py — Sakoon AI
Builds a structured wellness report dict from st.session_state.profile /
SQLite data, then renders it as a PDF using fpdf2 with embedded Noto Nastaliq
Urdu TTF for correct Arabic-script Unicode rendering. Sections follow
IDEA.md §9 exactly. No medication names or dosages ever appear in output.
"""
# Logic implemented in M5
