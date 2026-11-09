import os
import pandas as pd
import pandas_ta as ta
import logging
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

def get_technical_indicators(symbol="BTCUSDT"):
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY")
    
    try:
        client = Client(api_key, api_secret)
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_15MINUTE, "2 days ago UTC")
        
        if not klines or len(klines) < 30:
            logging.warning(f"[{symbol}] Yetersiz geçmiş veri veya sembol aktif değil.")
            return None
            
        df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
    except Exception as e:
        logging.error(f"Binance veri çekme hatası ({symbol}): {e}")
        return None

    # ------------------------------------------------------------------
    # 🛠️ GÜVENLİ İNDİKATÖR HESAPLAMA VE KORUMA KATMANI
    # ------------------------------------------------------------------
    try:
        df['RSI'] = ta.rsi(df['close'], length=14)
        
        # MACD Hesaplama ve Boş Veri (NoneType) Kontrolü
        macd_df = ta.macd(df['close'], fast=12, slow=26, signal=9)
        if macd_df is None or macd_df.empty:
            logging.warning(f"[{symbol}] MACD hesaplanamadı, veri setinde pürüz var.")
            return None
            
        df['MACD'] = macd_df.iloc[:, 0]
        df['MACD_Signal'] = macd_df.iloc[:, 2]
        
        df['Vol_Avg'] = ta.sma(df['volume'], length=20)
        df['ADL'] = ta.ad(df['high'], df['low'], df['close'], df['volume'])
        
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx_df is None or adx_df.empty:
            return None
        df['ADX'] = adx_df.iloc[:, 0]
        
        aroon_df = ta.aroon(df['high'], df['low'], length=14)
        df['Aroon_Up'] = aroon_df.iloc[:, 2]
        
        stoch_df = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
        df['Stoch_K'] = stoch_df.iloc[:, 0]
        df['Stoch_D'] = stoch_df.iloc[:, 1]
        
        bb_df = ta.bbands(df['close'], length=20, std=2)
        df['BB_Lower'] = bb_df.iloc[:, 0]   
        df['BB_Middle'] = bb_df.iloc[:, 1]  
        df['BB_Upper'] = bb_df.iloc[:, 2]   
        
    except Exception as ind_error:
        logging.error(f"[{symbol}] İndikatör hesaplama hatası: {ind_error}")
        return None

    # Eğer kritik sütunlarda NaN (boş) veri kaldıysa temizle veya kontrol et
    if df['RSI'].isnull().iloc[-1] or df['ADX'].isnull().iloc[-1]:
        return None

    # ------------------------------------------------------------------
    # ÖRÜNTÜ TANIMA VE HAFİZA MOTORU (Double Top & Double Bottom)
    # ------------------------------------------------------------------
    local_max = df['high'].iloc[-100:-5].max()
    local_min = df['low'].iloc[-100:-5].min()
    
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    last_price = last_row['close']
    
    pattern_signal = "NEUTRAL"
    pattern_detail = "Belirgin bir fiyat örüntüsü tespit edilemedi."
    
    if abs(last_price - local_max) / local_max <= 0.015:
        pattern_signal = "DOUBLE_TOP_ZONE"
        pattern_detail = f"⚠️ İKİLİ TEPE (DOUBLE TOP) BÖLGESİ GÖRÜLDÜ: Fiyat geçmiş zirve direncine ({local_max}) çok yakın!"
    elif abs(last_price - local_min) / local_min <= 0.015:
        pattern_signal = "DOUBLE_BOTTOM_ZONE"
        pattern_detail = f"🟢 İKİLİ DİP (DOUBLE BOTTOM) BÖLGESİ GÖRÜLDÜ: Fiyat geçmiş güçlü dip desteğine ({local_min}) çok yakın!"

    # ------------------------------------------------------------------
    # REJİM TABANLI AKILLI KARAR MEKANİZMASI
    # ------------------------------------------------------------------
    decision = "NEUTRAL"
    durum_detayi = "İndikatör kombinasyonları kararsız durumda."
    
    if last_row['ADX'] < 22:
        if (last_price <= last_row['BB_Lower'] * 1.015 or pattern_signal == "DOUBLE_BOTTOM_ZONE") and last_row['Stoch_K'] > last_row['Stoch_D']:
            if last_row['ADL'] >= prev_row['ADL']: 
                decision = "BULLISH"
                durum_detayi = f"🔵 Bollinger Alt Bant / İkili Dip Uyum Dönüşü (Yatay Rejim). {pattern_detail}"
        elif last_price >= last_row['BB_Upper'] * 0.985 or pattern_signal == "DOUBLE_TOP_ZONE" or last_row['RSI'] > 70:
            decision = "BEARISH"
            durum_detayi = f"🛑 Üst Sınır Direnç Doygunluğu (Yatay Rejim). {pattern_detail}"

    else:
        if last_row['Aroon_Up'] > 70 and last_row['MACD'] > last_row['MACD_Signal'] and last_row['volume'] > last_row['Vol_Avg']:
            if pattern_signal != "DOUBLE_TOP_ZONE": 
                decision = "BULLISH"
                durum_detayi = "🔥 Güçlü Hacimli Boğa Trendi Kırılımı (Trend Rejimi). Önü açık."
        elif last_price < last_row['BB_Middle'] and last_row['MACD'] < last_row['MACD_Signal']:
            decision = "BEARISH"
            durum_detayi = "⚠️ Trend Kaybı ve Orta Bandın Altına Sarkma (Trend Rejimi)."

    return {
        'Symbol': symbol,
        'Last_Price': last_price,
        'Technical_Signal': decision,
        'Pattern_Signal': pattern_signal,
        'RSI': round(last_row['RSI'], 2),
        'ADX': round(last_row['ADX'], 2),
        'Durum_Detayi': durum_detayi,
        'Local_Max': local_max,
        'Local_Min': local_min
    }