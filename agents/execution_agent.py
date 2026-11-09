import os
import csv
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

def log_trade_to_csv(symbol, side, qty, price, reason):
    """
    İşlem kayıtlarını 'trade_history.csv' dosyasına zaman damgasıyla birlikte ekler.
    İleride grafik çizdirmek ve botu optimize etmek için veri tabanı görevi görür.
    """
    csv_file = "trade_history.csv"
    file_exists = os.path.isfile(csv_file)
    
    # Kurumsal Defter Başlıkları
    headers = [
        "Zaman", 
        "Varlık", 
        "İşlem Yönü", 
        "Miktar", 
        "İşlem Fiyatı", 
        "Toplam Hacim (USD)", 
        "İşlem Nedeni"
    ]
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_volume = round(float(qty) * float(price), 2) if isinstance(price, (int, float)) else 0.0
    
    row = [current_time, symbol, side, qty, price, total_volume, reason]
    
    try:
        # 'a' modu (append) ile dosya varsa altına yazar, yoksa yeni oluşturur
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)  # Dosya ilk defa oluşuyorsa başlıkları koy
            writer.writerow(row)
    except Exception as e:
        print(f"⚠️ CSV Günlüğü Yazma Hatası: {e}")

def execute_trade(symbol, qty, side="BUY", optimized_price=None, reason="Strateji Sinyali"):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    try:
        trading_client = TradingClient(api_key, secret_key, paper=True)
        order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
        
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=round(qty, 5),
            side=order_side,
            time_in_force=TimeInForce.GTC
        )
        
        market_order = trading_client.submit_order(order_data=market_order_data)
        fiyat_mesaji = f"Piyasa Fiyatından" if not optimized_price else f"Dinamik Optimize Fiyat ({optimized_price}) Önünden"
        
        # Eğer optimize edilmiş bir fiyattan (örneğin ikili dip üzerinden front-run) girdiysek onu yazıyoruz
        trade_price = optimized_price if optimized_price else "Piyasa Fiyatı"
        
        # 👑 KRİTİK ADIM: Başarılı işlemi zamanı ve tam analitik sebebiyle CSV'ye kaydet
        log_trade_to_csv(symbol, side, qty, trade_price, reason)
        
        return {
            "Durum": "BAŞARILI",
            "Mesaj": f"🚀 {symbol} için {qty} adet {side} emri {fiyat_mesaji} Alpaca'ya başarıyla iletildi ve CSV defterine işlendi! Emir ID: {market_order.id}"
        }
    except Exception as e:
        return {"Durum": "HATA", "Mesaj": str(e)}