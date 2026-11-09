import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

api_key = os.getenv("VERTEX_API_KEY")
client = genai.Client(api_key=api_key)

print("Yapay Zeka ile iletişim kuruluyor...")

# Eski 2.0 modeli yerine panelindeki güncel modeli çağırıyoruz
response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview", 
    contents="Algoritmik ticarette risk yönetiminin önemini tek bir cümleyle açıkla."
)

print("\nGelen Cevap:\n", response.text)