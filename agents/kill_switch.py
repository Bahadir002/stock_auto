def check_kill_switch(start_of_day_balance, current_balance, max_daily_loss_pct=5.0):
    # Günlük kar/zarar oranını hesaplıyoruz
    drawdown_amount = start_of_day_balance - current_balance
    drawdown_pct = (drawdown_amount / start_of_day_balance) * 100
    
    if drawdown_pct >= max_daily_loss_pct:
        return {
            "Durum": "🛑 KILL-SWITCH AKTIF 🛑",
            "Gunluk_Kayıp_Yuzdesi": round(drawdown_pct, 2),
            "Aksiyon": "Tüm açık pozisyonlar acilen kapatılıyor. Yeni işlem açılması DURDURULDU.",
            "Mesaj": f"Sistem güvenliği sağlandı. Maksimum günlük kayıp limiti (%{max_daily_loss_pct}) aşıldığı için otonom ticaret askıya alındı."
        }
    elif drawdown_pct > 0:
        return {
            "Durum": "🟢 SISTEM GUVENDE 🟢",
            "Gunluk_Kayıp_Yuzdesi": round(drawdown_pct, 2),
            "Aksiyon": "İşlemlere devam ediliyor.",
            "Mesaj": "Günlük düşüş limitler dahilinde."
        }
    else:
        return {
            "Durum": "🟢 SISTEM GUVENDE (KARDA) 🟢",
            "Gunluk_Kayıp_Yuzdesi": 0.0,
            "Aksiyon": "İşlemlere devam ediliyor.",
            "Mesaj": f"Sistem artıda. Günlük Kar: +{abs(round(drawdown_pct, 2))}%"
        }

if __name__ == "__main__":
    print("Hard Kill-Switch Ajanı Test Ediliyor...\n")
    
    # Senaryo 1: Güvenli durum (10.000$ ile başladık, 9.700$'a düştük -> %3 kayıp)
    print("--- Senaryo 1: Normal Dalgalanma ---")
    sonuc_guvenli = check_kill_switch(10000, 9700)
    for k, v in sonuc_guvenli.items():
        print(f"{k}: {v}")
        
    print("\n-----------------------------------\n")
    
    # Senaryo 2: Felaket durumu (10.000$ ile başladık, 9.400$'a düştük -> %6 kayıp)
    print("--- Senaryo 2: Piyasa Çöküşü (Acil Durum) ---")
    sonuc_tehlike = check_kill_switch(10000, 9400)
    for k, v in sonuc_tehlike.items():
        print(f"{k}: {v}")