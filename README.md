# 🧠 Sakoon AI
### AI-Powered Mental Wellness Assistant

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red?style=for-the-badge&logo=streamlit)
![OpenAI](https://img.shields.io/badge/LLM-AI-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</p>

---

## 📖 Overview

Sakoon AI is an AI-powered mental wellness assistant designed to provide users with a safe and supportive environment for emotional conversations. The application leverages Large Language Models (LLMs), sentiment analysis, and report generation to deliver personalized mental wellness insights.

The goal of Sakoon AI is **not to replace professional therapy**, but to encourage self-reflection, emotional awareness, and healthy coping practices through empathetic AI conversations.

---

## ✨ Features

- 💬 AI-powered empathetic chatbot
- 😊 Mood & sentiment analysis
- 📊 Session report generation
- 📧 Email summaries
- 📄 Downloadable wellness reports
- 🎨 Clean Streamlit interface
- 🔒 Secure API key management
- ⚡ Fast and lightweight deployment

---

# 🏗️ System Architecture

```
                User
                  │
                  ▼
          Streamlit Interface
                  │
                  ▼
        Conversation Manager
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
Prompt Builder  Sentiment   Memory
                Analysis
      │           │
      └──────┬────┘
             ▼
         OpenAI API
             │
      AI Response Generated
             │
      ┌──────┴────────┐
      ▼               ▼
 PDF Report      Email Service
      │               │
      └──────┬────────┘
             ▼
            User
```

---

# 🚀 Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Backend |
| Streamlit | Web Application |
| OpenAI API | AI Conversations |
| TextBlob / NLP | Sentiment Analysis |
| SMTP | Email Reports |
| FPDF / ReportLab | PDF Generation |
| TOML | Configuration |
| Git & GitHub | Version Control |

---

# 📂 Project Structure

```
Sakoon-AI/
│
├── app.py
├── chatbot.py
├── emailer.py
├── report_generator.py
├── sentiment.py
├── config.toml
├── requirements.txt
├── assets/
├── reports/
├── screenshots/
├── README.md
└── LICENSE
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Laraibkhalid111/Sakoon-AI.git

cd Sakoon-AI
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure API Keys

Create a `.streamlit/secrets.toml` or update `config.toml`

```toml
OPENAI_API_KEY="your_api_key_here"
EMAIL="example@gmail.com"
PASSWORD="your_app_password"
```

---

## Run Application

```bash
streamlit run app.py
```

---

# 🧠 How It Works

1. User opens Sakoon AI.
2. User starts a conversation.
3. Chat messages are sent to the LLM.
4. Sentiment analysis detects emotional tone.
5. AI generates supportive responses.
6. Session data is summarized.
7. A wellness report is created.
8. Report can be emailed or downloaded.

---

# 📊 Workflow

```
User Input
      │
      ▼
Preprocessing
      │
      ▼
Prompt Construction
      │
      ▼
OpenAI API
      │
      ▼
AI Response
      │
      ▼
Sentiment Analysis
      │
      ▼
Report Generation
      │
      ▼
Email / Download
```

---

# 💡 Future Improvements

- Multi-language support
- Therapist dashboard
- User authentication
- Personalized wellness plans
- Emotion trend analytics
- Google Calendar wellness reminders

---



---

# 📈 Skills Demonstrated

- Artificial Intelligence
- Prompt Engineering
- Natural Language Processing
- Sentiment Analysis
- Python Development
- Streamlit
- API Integration
- Email Automation
- PDF Generation
- UI Design
- Software Engineering
- Git & GitHub

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

---

# 👨‍💻 Author

**Laraib Khalid**

- GitHub: https://github.com/Laraibkhalid111


---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

---
