import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def analyze_crypto_harmonics(symbol, technical_signal):
    api_key = os.getenv("VERTEX_API_KEY")
    if not api_key:
        return "VETO: Vertex AI API Key bulunamadı!"
        
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return "VETO: Vertex AI bağlantı hatası."

    prompt = f"""
    Sen kurumsal bir hedge fonunun baş kantitatif analistisin. 
    Teknik Analiz Ajanımız şu an {symbol} varlığı için şu sinyali üretti: {technical_signal}.
    
    Görevin: İnternetteki en güncel kurumsal raporları, blockchain ağ verilerini ve canlı piyasayı simüle ederek şu 3 katmanı analiz et:
    1. ON-CHAIN METRICS: Balina hareketleri (Exchange Inflows/Outflows), aktif cüzdan adresleri ve ağ sağlığı ne durumda?
    2. FUNDING RATES & OPEN INTEREST: Vadeli piyasada küçük yatırımcı çılgınca kaldıraçlı long mu açıyor (piyasa tepesi mi), yoksa bir akümülasyon mu var?
    3. MVRV Z-SCORE & SENTIMENT: Büyük döngüde varlık aşırı mı değerlendi, yoksa döngüsel olarak ucuz mu? Sosyal medya duyarlılığı aşırı coşkulu mu (contrarian risk)?

    Eğer {technical_signal} sinyali bu kurumsal verilerle HARMONİK olarak uyuşuyorsa "GECERLI" yanıtını ver.
    Eğer vadeli piyasa aşırı şişmişse veya on-chain tehlike varsa "VETO" yanıtını ver.

    Çıktı formatın KESİNLİKLE şu şablonda olmalı:
    HARMONIC_DECISION: [GECERLI veya VETO]
    EXPLANATION: [Analizini özetleyen tek bir kurumsal cümle]

    NOT: Piyasada çok büyük, sistemsel bir çöküş veya ekstrem bir tehlike (Black Swan) olmadığı sürece küçük fonlama ısınmalarını göz ardı et ve teknik sinyale güvenerek APPROVE kararı vermeye odaklan.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "VETO: LLM sentezleme hatası."