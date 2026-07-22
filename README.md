# Sakoon AI 🫶

> **A calm space to talk** / بات کرنے کی ایک پرسکون جگہ

Sakoon AI is a free, bilingual (Urdu + English, voice or text) mental wellness companion built with Streamlit and Groq. It listens without judgment, gently explores what you're going through, offers grounding techniques in the moment, builds a personalized recovery plan, and delivers a clean PDF summary — while a deterministic safety layer ensures anyone in genuine crisis is never left with just a chatbot reply.

---

## Author
- **Laraib Khalid**

---

## Key Features

1. **Interactive Self-Care:** Offers grounding/breathing exercises and a gentle journal directly in the UI with interactive step-by-step guides.
2. **Wellness room:** Persistent mood check-ins, journal history, daily affirmations, and emergency support resources (EN / Urdu / Roman Urdu).
3. **Insights dashboard:** Mood trends, check-in streaks, daily activity charts, and a weekly summary from your real logs.
4. **Premium chat UI:** Light/dark calm themes, markdown replies, copy buttons, thinking status, and loadable conversation history.
5. **Bilingual Conversational Interface:** Support for English, Urdu Script, and Roman Urdu. Mirrors the user's language/script choice instantly.
6. **Bilingual Speech-to-Text:** Integration with Groq Whisper (`whisper-large-v3-turbo`) for natural, audio-based inputs.
7. **Structured Session Profile & Extraction:** Dynamically extracts name, email, phone, primary concern, mood, symptoms, and risk flags via Groq JSON mode.
8. **Deterministic Safety Layer:** Built-in keyword patterns for English, Urdu, and Roman Urdu to intercept crisis topics immediately, show a pinned helpline banner, and send supportive replies.
9. **PDF Wellness Report:** Generates formatted A4 PDF reports (with embedded Urdu font rendering support).
10. **Email Delivery:** Automatically emails the PDF report to the user using secure SMTP.
11. **Secure Database Logging:** Maintains conversation history, mood logs, journal entries, and risk levels inside SQLite (`sakoon.db`).

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
| Deployment | Streamlit Community Cloud **or** Docker (`Dockerfile` / `docker compose`) |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the production upgrade roadmap (evolutionary — no greenfield rewrite).

---

## Directory Structure

```
Sakoon-Ai/
├── app.py                 # Thin Streamlit entrypoint (orchestration)
├── sakoon/                # Application package (Phase 1+)
│   ├── core/              # config, logging, validation, security, paths
│   ├── db/                # SQLite schema + repositories
│   ├── services/          # chatbot, safety, report, emailer, prompts
│   └── ui/                # CSS + chat chrome helpers
├── chatbot.py … emailer.py  # Thin shims → sakoon.* (compat)
├── Dockerfile             # Container image (Phase 6)
├── docker-compose.yml     # App + optional backup profile
├── scripts/backup_db.py   # SQLite backup CLI
├── .github/workflows/ci.yml
├── tests/
├── ARCHITECTURE.md        # Production upgrade roadmap
├── requirements.txt
└── README.md
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

### Docker

```bash
cp env.example .env   # fill GROQ_API_KEY (and optional email / ENCRYPTION_KEY)
docker compose up --build
# App: http://localhost:8501
# Health: Streamlit built-in GET /_stcore/health (used by Docker HEALTHCHECK)

# One-shot SQLite backup into the data volume:
docker compose run --rm backup
```

Local backup without Docker:

```bash
python scripts/backup_db.py
python scripts/backup_db.py --list
```

### CI

Pushes/PRs to `main`/`master` run pytest (Python 3.11 + 3.12). Image build runs on push after tests pass.

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
