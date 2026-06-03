"""Безопасный AI Ассистент для Windows"""

import asyncio
import json
import re
import base64
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import httpx
from secrets import SecretManager

# === КОНФИГ ===
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar"
]

# === ФУНКЦИИ ===
def get_google_services():
    """Авторизация Google (1 раз)"""
    creds = None
    token_file = "token.json"
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_file, "w") as f:
                f.write(creds.to_json())
        print("✅ Google авторизован")
    
    return {
        "gmail": build("gmail", "v1", credentials=creds),
        "calendar": build("calendar", "v3", credentials=creds)
    }

def get_emails(gmail, max_results=15):
    """Чтение непрочитанных писем"""
    results = gmail.users().messages().list(
        userId="me", maxResults=max_results, q="is:unread"
    ).execute()
    
    messages = results.get("messages", [])
    emails = []
    
    for msg in messages:
        m = gmail.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = m.get("payload", {})
        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
        
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")[:400]
                        break
        else:
            data = payload.get("body", {}).get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")[:400]
        
        emails.append({
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "body": body
        })
    
    return emails

def create_calendar_event(calendar, title, datetime_str, description=""):
    """Создание встречи"""
    try:
        start = datetime.fromisoformat(datetime_str)
        if start.tzinfo is None:
            start = start.replace(tzinfo=None)
        end = start + timedelta(hours=1)
        
        event = {
            "summary": title,
            "description": description + "\n\nАвтоматически создано AI",
            "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Warsaw"},
            "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Warsaw"},
        }
        calendar.events().insert(calendarId="primary", body=event).execute()
        print(f"✅ Встреча: {title}")
        return True
    except Exception as e:
        print(f"⚠️ Ошибка создания встречи: {e}")
        return False

async def ask_groq(prompt):
    """Запрос к Groq"""
    api_key = SecretManager.get("GROQ_API_KEY")
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1500
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]

async def send_telegram(text):
    """Отправка в Telegram"""
    bot_token = SecretManager.get("TG_BOT_TOKEN")
    chat_id = SecretManager.get("TG_CHAT_ID")
    
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text[:4000],
                "parse_mode": None
            }
        )
    print("✅ Сообщение отправлено в Telegram")

async def main():
    print("🚀 Запуск AI Ассистента...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Google сервисы
    services = get_google_services()
    
    # Читаем почту
    print("📧 Читаю Gmail...")
    emails = get_emails(services["gmail"])
    print(f"   Писем: {len(emails)}")
    
    # Формируем текст для AI
    email_text = "\n\n".join([
        f"От: {e['from']}\nТема: {e['subject']}\n{e['body'][:300]}"
        for e in emails[:10]
    ]) or "Нет новых писем"
    
    prompt = f"""
Ты — AI Ассистент. Сделай утренний брифинг (коротко, 10-15 строк):

ПИСЬМА:
{email_text[:2000]}

Ответь в формате:

📊 ВАЖНОЕ НА СЕГОДНЯ:
(список)

📧 ТРЕБУЮТ ОТВЕТА:
(для каждого письма: от кого, суть, короткий шаблон ответа)

🎯 ЧТО СДЕЛАТЬ ПЕРВЫМ ДЕЛОМ:
(1-2 пункта)

JSON (в конце, строго):
{{"meetings": []}}
"""

    # Запрос к AI
    print("🤖 Анализирую через Groq...")
    response = await ask_groq(prompt)
    
    # Парсим встречи
    try:
        json_match = re.search(r'\{.*"meetings".*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            for meeting in data.get("meetings", []):
                if meeting.get("datetime"):
                    create_calendar_event(
                        services["calendar"],
                        meeting.get("title", "Встреча"),
                        meeting["datetime"],
                        meeting.get("description", "")
                    )
    except Exception as e:
        print(f"⚠️ Ошибка парсинга встреч: {e}")
    
    # Отправляем
    await send_telegram(response)
    print("\n✅ Готово!")

if __name__ == "__main__":
    asyncio.run(main())