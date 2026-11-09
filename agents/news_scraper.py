import os
import feedparser
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("VERTEX_API_KEY"))

def fetch_and_analyze_news(ticker="BTC"):
    # Yahoo Finance üzerinden varlığın en güncel RSS haberlerini çekiyoruz
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}-USD"
    feed = feedparser.parse(url)

    if not feed.entries:
        return "Haber bulunamadı."

    # En güncel 3 haberi alıp tek bir metin haline getiriyoruz
    news_titles = [entry.title for entry in feed.entries[:3]]
    news_text = "\n- ".join(news_titles)

    # Ajanın beynine (LLM) vereceğimiz prompt (talimat)
    prompt = f"""
    Sen otonom bir finansal Haber Kazıyıcı Ajansın.
    Şu anki analiz edilen varlık: {ticker}.
    
    Aşağıdaki en güncel haber başlıklarını analiz et ve varlık için genel duyarlılığı tek bir kelime ile belirt: (POZITIF, NEGATIF veya NOTR).
    Ardından bu kararın nedenini tek bir kısa cümleyle açıkla.

    Haberler:
    - {news_text}
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    return response.text

# Kodu doğrudan çalıştırdığımızda test etmesi için:
if __name__ == "__main__":
    print("Haber Kazıyıcı Ajan Çalışıyor...\n")
    print(fetch_and_analyze_news("BTC"))