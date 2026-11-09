import sys
import os
import time
import schedule
import logging
from datetime import datetime
from binance.client import Client
from alpaca.trading.client import TradingClient # Canlı bakiye için eklendi
from dotenv import load_dotenv

proje_dizini = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, proje_dizini)
os.chdir(proje_dizini)

load_dotenv(override=True)

# Logger Kurulumu (Kayıtlar dosyaya ve konsola)
log_format = '%(asctime)s [%(levelname)s] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.hasHandlers(): logger.handlers.clear()

file_handler = logging.FileHandler("otonom_kayitlar.log", mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter(log_format, date_format))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format, date_format))
logger.addHandler(console_handler)

from agents.technical_indicator import get_technical_indicators
from agents.macro_analyst import analyze_crypto_harmonics
from agents.statistical_verifier import backtest_signal
from agents.execution_agent import execute_trade
from agents.logging_agent import check_system_health
from agents.communications_agent import send_telegram_message
from agents.kill_switch import check_kill_switch
from agents.risk_manager import calculate_position_size
from agents.correlation_agent import check_portfolio_correlation

def get_dynamic_top_30_watchlist():
    logging.info("🌐 Binance piyasasından en yüksek hacimli ilk 30 güvenli varlık dinamik olarak çekiliyor...")
    try:
        client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))
        tickers = client.get_ticker()
        usdt_pairs = []
        ignored_keywords = ["USDC", "BUSD", "EUR", "GBP", "DAI", "UP", "DOWN", "BEAR", "BULL", "PAX", "TUSD"]
        
        for t in tickers:
            symbol = t['symbol']
            if symbol.endswith("USDT") and not any(x in symbol for x in ignored_keywords):
                usdt_pairs.append({
                    "binance_ticker": symbol,
                    "alpaca_ticker": f"{symbol[:-4]}/USD",
                    "name": symbol[:-4],
                    "volume": float(t['quoteVolume'])
                })
        usdt_pairs.sort(key=lambda x: x['volume'], reverse=True)
        top_30 = usdt_pairs[:30]
        logging.info(f"✅ Dinamik liste başarıyla hazırlandı. Toplam {len(top_30)} aktif majör varlık taranacak.")
        return top_30
    except Exception as e:
        logging.error(f"❌ Dinamik liste hatası: {e}. Sabit listeye dönülüyor.")
        return [{"binance_ticker": "BTCUSDT", "alpaca_ticker": "BTC/USD", "name": "BTC"}]

def safe_telegram_broadcast(message):
    try: send_telegram_message(message)
    except Exception as e: logging.error(f"Telegram yayın hatası: {e}")

def autonomous_hedge_fund_cycle():
    logging.info("=== ORKESTRA UYANDI: .ENV TABANLI KURUMSAL DÖNGÜ BAŞLADI ===")
    logging.info(check_system_health())
    
    # 👑 ALPACA'DAN GERÇEK/SANAL CANLI BAKİYEYİ ÇEKİYORUZ
    try:
        trading_client = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True)
        account = trading_client.get_account()
        current_balance = float(account.cash)
        start_balance = float(account.equity) # Gün başı/mevcut varlık dengesi
        logging.info(f"💰 Canlı Hesap Bakiyesi (Nakit): ${current_balance} | Toplam Portföy Değeri: ${start_balance}")
    except Exception as e:
        logging.error(f"⚠️ Alpaca bakiye çekme hatası: {e}. Simüle bakiye kullanılıyor.")
        start_balance = 10000.0
        current_balance = 10000.0

    security_check = check_kill_switch(start_balance, current_balance, max_daily_loss_pct=5.0)
    logging.info(f"Kill-Switch Durumu: {security_check['Durum']}")
    if "🛑" in security_check['Durum']:
        safe_telegram_broadcast(f"🚨 *ACİL DURUM KİLİDİ:* {security_check['Mesaj']}")
        return

    watchlist = get_dynamic_top_30_watchlist()
    current_portfolio = [] 
    
    # Alpaca'daki mevcut açık pozisyonları çekip korelasyon ajanına dinamik besliyoruz
    try:
        positions = trading_client.get_all_positions()
        current_portfolio = [pos.symbol for pos in positions]
        logging.info(f"💼 Mevcut Alpaca Portföyü: {current_portfolio}")
    except Exception as e:
        logging.error(f"⚠️ Pozisyon çekme hatası: {e}")

    for asset in watchlist:
        logging.info(f"--------------------------------------------------")
        logging.info(f"🔍 {asset['name']} Analiz Süzgecine Giriyor...")
        
        tech_data = get_technical_indicators(asset['binance_ticker'])
        if not tech_data or isinstance(tech_data, str): continue
            
        if tech_data['Technical_Signal'] == "BULLISH":
            harmonic_report = analyze_crypto_harmonics(asset['name'], "BULLISH")
            logging.info(f"[{asset['name']}] Harmonik Sentez Raporu:\n{harmonic_report}")
            if "VETO" in harmonic_report: continue
                
            stats_data = backtest_signal(asset['binance_ticker'], tech_data['RSI'])
            logging.info(f"[{asset['name']}] Tarihsel Başarı Oranı: %{stats_data['Basari_Orani_Yuzde']} | Karar: {stats_data['Karar']}")
            if stats_data['Karar'] == "RISKLI (Iptal Edildi)": continue
                
            # Yenilenen dinamik korelasyon ajanı denetimi
            correlation_check = check_portfolio_correlation(asset['alpaca_ticker'], current_portfolio)
            if "RED" in correlation_check:
                logging.warning(f"❌ İPTAL: {asset['name']} için {correlation_check}")
                continue

            last_price = tech_data['Last_Price']
            optimized_entry = last_price
            if tech_data['Pattern_Signal'] == "DOUBLE_BOTTOM_ZONE":
                optimized_entry = tech_data['Local_Min'] * 1.004
                logging.info(f"🎯 Fiyatlama Optimize Edildi! Giriş: {optimized_entry} (Front-Running).")
            
            stop_loss = optimized_entry * 0.985 
            risk_plan = calculate_position_size(current_balance, optimized_entry, stop_loss, risk_percentage=1.0)
            qty_to_buy = risk_plan['Alinacak_Miktar']
            
            trade_reason = f"Teknik Sinyal: {tech_data['Durum_Detayi']} | Tarihsel Olasılık: %{stats_data['Basari_Orani_Yuzde']}"
            
            order_res = execute_trade(
                symbol=asset['alpaca_ticker'], 
                qty=qty_to_buy, 
                side="BUY", 
                optimized_price=optimized_entry,
                reason=trade_reason
            )
            logging.info(order_res)
            
            if order_res['Durum'] == "BAŞARILI":
                current_portfolio.append(asset['alpaca_ticker']) 
                safe_telegram_broadcast(
                    f"🔔 *OTONOM PORTFÖY EKLEMESİ*\n"
                    f"• *Varlık:* {asset['name']}\n"
                    f"• *Giriş Fiyatı:* {optimized_entry}\n"
                    f"• *İşlem Nedeni:* {trade_reason}\n"
                    f"🚀 {order_res['Mesaj']}"
                )
        else:
            logging.info(f"[{asset['name']}] Güçlü bir alım sinyali yok. Beklemeye geçiliyor.")
                
    logging.info("=== TÜM WATCHLIST TARANDI. ORKESTRA UYKU MODUNA GEÇİYOR ===\n")

if __name__ == "__main__":
    print("🤖 Kurumsal Düzey Akıllı Otonom Sistem Arayüzü Dinamik Tarama Modunda Başlatıldı.")
    safe_telegram_broadcast("👑 *Dinamik Hibrit Karar Motoru Aktif!* Sistem artık her 4 hours bir piyasanın en hacimli ilk 30 güvenli varlığını otomatik bulup süzgeçe alacak.")
    
    autonomous_hedge_fund_cycle()
    schedule.every(10).minutes.do(autonomous_hedge_fund_cycle)
    
    while True:
        schedule.run_pending()
        time.sleep(1)