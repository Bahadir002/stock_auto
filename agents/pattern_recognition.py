import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
client = genai.Client(api_key=os.getenv("VERTEX_API_KEY"))

def detect_price_patterns(symbol, recent_prices):
    prompt = f"""
    Sen otonom bir Desen Tanıma Ajansın (Pattern Recognition Agent).
    {symbol} varlığına ait son günlerin kapanış fiyatları aşağıda sırasıyla verilmiştir.
    
    Fiyat Geçmişi (Eskiden Yeniye): {recent_prices}
    
    Bu fiyat dizilimine bakarak piyasanın genel yapısını (yükselen trend, düşen trend veya yatay konsolidasyon) analiz et. Olası bir formasyon veya kırılım ihtimali görüyorsan bunu belirt.
    
    Çıktı Formatın şu şekilde olmalı:
    PATTERN: [Tespit edilen desen veya trend]
    ANALYSIS: [Nedenini açıklayan tek bir cümle]
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    print("Desen Tanıma Ajanı Çalışıyor...\n")
    # Temsili bir fiyat hareketi (Örn: Fiyat sıkışıp yukarı kırıyor)
    sample_prices = [61000, 61500, 61200, 61800, 61500, 62000, 62200, 62100, 64500, 65200]
    print(detect_price_patterns("BTC", sample_prices))