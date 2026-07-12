# Sakoon AI 🫶

> **A calm space to talk** / بات کرنے کی ایک پرسکون جگہ

Sakoon AI is a free, bilingual (Urdu + English, voice or text) mental wellness companion built with Streamlit and Groq. It listens without judgment, gently explores what you're going through, offers grounding techniques in the moment, builds a personalized recovery plan, and delivers a clean PDF summary — while a deterministic safety layer ensures anyone in genuine crisis is never left with just a chatbot reply.

---

## Author
- **Laraib Khalid**

---

## Key Features

1. **Bilingual Conversational Interface:** Support for English, Urdu Script, and Roman Urdu. Mirrors the user's language/script choice instantly.
2. **Bilingual Speech-to-Text:** Integration with Groq Whisper (`whisper-large-v3-turbo`) for natural, audio-based inputs.
3. **Structured Session Profile & Extraction:** Dynamically extracts name, email, phone, primary concern, mood, symptoms, and risk flags via Groq JSON mode.
4. **Interactive Self-Care:** Offers grounding/breathing exercises directly in the UI with interactive step-by-step guides.
5. **Deterministic Safety Layer:** Built-in keyword patterns for English, Urdu, and Roman Urdu to intercept crisis topics immediately, show a pinned helpline banner, and send supportive replies.
6. **PDF Wellness Report:** Generates formatted A4 PDF reports (with embedded Urdu font rendering support).
7. **Email Delivery:** Automatically emails the PDF report to the user using secure SMTP.
8. **Secure Database Logging:** Maintains conversation history and risk levels inside SQLite (`sakoon.db`) with zero plain-text secrets.

---

## Tech Stack

| Concern | Tool |
|---|---|
| UI / App | Streamlit (≥1.38) |
| LLM | Groq API (`llama-3.3-70b-versatile`) |
| Speech-to-Text | Groq Whisper (`whisper-large-v3-turbo`) |
| Storage | SQLite (`sakoon.db`) |
| PDF generation | fpdf2 |
| Email | Gmail SMTP (smtplib stdlib) |
| Deployment | Streamlit Community Cloud |

---

## Directory Structure

```
Sakoon-Ai/
├── app.py                      # Main Streamlit application and layout logic
├── chatbot.py                  # Groq client wrapper, JSON mode parser, and Whisper STT
├── safety.py                   # Deterministic regex-based crisis keyword detector
├── database.py                 # SQLite session storage and message logger
├── report.py                   # PDF generator (fpdf2) with Unicode Urdu font support
├── emailer.py                  # SMTP email dispatch utility
├── prompts.py                  # System instructions, redirect texts, and intake flows
├── NotoNastaliqUrdu-Regular.ttf # Unicode Urdu font for report rendering
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Laraibkhalid111/Sakoon-Ai.git
cd Sakoon-Ai

# 2. Create + activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets
cp env.example .env                         # fill in real values
mkdir -p .streamlit
cp .env .streamlit/secrets.toml             # or fill secrets.toml manually
# Required keys: GROQ_API_KEY, EMAIL_ADDRESS, EMAIL_APP_PASSWORD

# 5. Run the application
streamlit run app.py
```

---

## Required Secrets

See [`env.example`](env.example) for documentation of all required keys. Never commit real values — use `.streamlit/secrets.toml` locally (gitignored) and the Streamlit Cloud Secrets panel for deployment.

| Key | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq LLM + Whisper STT — free at [console.groq.com](https://console.groq.com) |
| `EMAIL_ADDRESS` | Gmail address that sends wellness reports |
| `EMAIL_APP_PASSWORD` | 16-char Gmail App Password (not your normal password) |

---

## Disclaimer

Sakoon AI is a self-care support tool, **not** a clinical diagnostic instrument. It is not a substitute for professional mental health care. If you are in crisis, please contact the **Umang Mental Health Helpline (Pakistan): 0311-7786264** or your local emergency services.

---

*Built by Laraib Khalid with Streamlit · Groq · fpdf2 · sqlite3*
