# Sakoon AI 🫶

> **A calm space to talk** / بات کرنے کی ایک پرسکون جگہ

Sakoon AI is a free, bilingual (Urdu + English, voice or text) mental wellness companion built with Streamlit and Groq. It listens without judgment, gently explores what you're going through, offers grounding techniques in the moment, builds a personalized recovery plan, and delivers a clean PDF summary — while a deterministic safety layer ensures anyone in genuine crisis is never left with just a chatbot reply.

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

## Local Setup

```bash
# 1. Clone
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

# 5. Run
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

*Built with Streamlit · Groq · fpdf2 · sqlite3*
