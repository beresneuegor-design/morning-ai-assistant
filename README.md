# 🤖 Morning AI Assistant

> Reads your Gmail → analyzes with Groq LLM → delivers a smart briefing to Telegram — every morning, fully automated.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=flat-square&logo=telegram)
![Gmail](https://img.shields.io/badge/Gmail-API-EA4335?style=flat-square&logo=gmail&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ✨ What it does

Every morning the assistant:

1. **Connects to Gmail** via Google OAuth 2.0 and fetches unread emails
2. **Sends them to Groq AI** (LLaMA 3.3 70B) for analysis
3. **Generates a structured briefing** — key items, emails needing reply, first action of the day
4. **Delivers it to your Telegram** in seconds

No UI. No bloat. Pure automation.

---

## 🏗️ Architecture

```
Gmail API ──► get_emails()
                  │
                  ▼
            build_prompt()
                  │
                  ▼
         Groq API (LLaMA 3.3 70B)
                  │
                  ▼
        send_telegram() ──► Your Telegram
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/morning-ai-assistant.git
cd morning-ai-assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up credentials

**Google (Gmail + Calendar):**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable Gmail API + Google Calendar API
3. Create OAuth 2.0 credentials → Desktop app
4. Download as `credentials.json` and place in project root

**Groq API:**
- Get free key at [console.groq.com](https://console.groq.com)

**Telegram Bot:**
- Create bot via [@BotFather](https://t.me/BotFather) → copy token
- Get your chat ID via [@userinfobot](https://t.me/userinfobot)

### 3. Configure `.env`

```bash
cp .env.example .env
```

Fill in your keys:

```env
GROQ_API_KEY="gsk_..."
TG_BOT_TOKEN="123456:AAF..."
TG_CHAT_ID="123456789"
```

### 4. Run

```bash
python main.py
```

On first run, a browser window will open for Google OAuth. After that — fully headless.

---

## ⏰ Automate (run every morning)

**macOS / Linux — cron:**
```bash
crontab -e
# Add:
0 8 * * * cd /path/to/morning-ai-assistant && venv/bin/python main.py
```

**Windows — Task Scheduler:**
- Action: `python C:\path\to\morning-ai-assistant\main.py`
- Trigger: Daily at 08:00

---

## 🔒 Security

- All secrets stored in `.env` — **never committed to git**
- `token.json` and `credentials.json` are in `.gitignore`
- OAuth 2.0 with token refresh — no passwords stored
- Minimal Gmail scope: **read-only**

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| AI Model | Groq — LLaMA 3.3 70B Versatile |
| Email | Gmail API (google-api-python-client) |
| Auth | Google OAuth 2.0 |
| Messaging | Telegram Bot API |
| HTTP | httpx (async) |
| Config | python-dotenv |

---

## 📁 Project Structure

```
morning-ai-assistant/
├── main.py              # Core logic
├── requirements.txt     # Dependencies
├── .env.example         # Config template (safe to commit)
├── .env                 # Your secrets (git-ignored)
├── credentials.json     # Google OAuth (git-ignored)
├── token.json           # Auto-generated OAuth token (git-ignored)
└── README.md
```

---

## 🔧 Customization

**Change AI model** — edit `ask_groq()`:
```python
model="llama-3.3-70b-versatile"   # fast & smart
model="mixtral-8x7b-32768"        # larger context
```

**Change email filter** — edit `get_emails()`:
```python
q="is:unread"           # unread only (default)
q="is:unread newer_than:1d"  # last 24h
q="from:boss@company.com"    # specific sender
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built with ❤️ as part of [VinteliVision](https://vintelivision.com) AI automation portfolio.*
