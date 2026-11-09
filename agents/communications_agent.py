import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        return "HATA: Telegram Token veya Chat ID bulunamadı."
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return "Telegram mesajı başarıyla gönderildi!"
        else:
            return f"Telegram Hatası: {response.text}"
    except Exception as e:
        return f"Bağlantı Hatası: {e}"

if __name__ == "__main__":
    print("İletişim Ajanı .env Modunda Çalışıyor...\n")
    print(send_telegram_message("🚀 *Test:* İletişim Ajanı .env üzerinden başarıyla bağlandı!"))