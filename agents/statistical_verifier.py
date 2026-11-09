import os
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

def backtest_signal(symbol="BTCUSDT", current_rsi=50.0):
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY")
    
    try:
        client = Client(api_key, api_secret)
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "5 years ago UTC")
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        
        df.ta.rsi(length=14, append=True)
        similar_cases = df[(df['RSI_14'] >= current_rsi - 3) & (df['RSI_14'] <= current_rsi + 3)]
        
        if len(similar_cases) == 0:
            return {"Basari_Orani_Yuzde": 0, "Karar": "BELIRSIZ"}
            
        success_count = 0
        total_cases = 0
        
        for index in similar_cases.index:
            if index + 7 < len(df): 
                total_cases += 1
                if df.loc[index + 7, 'close'] > df.loc[index, 'close']:
                    success_count += 1
                    
        win_rate = (success_count / total_cases) * 100 if total_cases > 0 else 0
        decision = "GECERLI" if win_rate >= 60.0 else "RISKLI (Iptal Edildi)"
        
        return {
            "Basari_Orani_Yuzde": round(win_rate, 2),
            "Karar": decision
        }
    except Exception as e:
        return {"Basari_Orani_Yuzde": 0, "Karar": f"HATA: {e}"}