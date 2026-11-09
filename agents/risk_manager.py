def calculate_position_size(account_balance, entry_price, stop_loss_price, risk_percentage=1.0):
    if entry_price <= stop_loss_price:
        return {"Hata": "Stop Loss fiyatı, giriş fiyatından düşük olmalıdır (Long pozisyon için)."}

    # Kaybetmeyi göze aldığımız maksimum dolar miktarı (Örn: 10.000$'ın %1'i = 100$)
    risk_amount = account_balance * (risk_percentage / 100)

    # Alacağımız 1 adet varlık başına alacağımız risk (Zarar mesafesi)
    risk_per_unit = entry_price - stop_loss_price

    # Bu riski aşmamak için almamız gereken kesin varlık adedi
    position_size = risk_amount / risk_per_unit

    return {
        "Bakiye_USD": account_balance,
        "Risk_Yuzdesi": f"%{risk_percentage}",
        "Riske_Edilen_USD": round(risk_amount, 2),
        "Giris_Fiyati": entry_price,
        "Stop_Loss": stop_loss_price,
        "Alinacak_Miktar": round(position_size, 6),
        "Toplam_Islem_Hacmi_USD": round(position_size * entry_price, 2)
    }

if __name__ == "__main__":
    print("Risk Yöneticisi Ajanı Çalışıyor...\n")
    
    # Senaryo: Hesabımızda 10.000 Dolar var. 
    # Bitcoin 78.000'de. Biz 75.000'e stop koyuyoruz. 
    # Sistem sadece %1 (100$) kaybetmek için ne kadarlık BTC almalı?
    sonuc = calculate_position_size(10000, 78000, 75000, 1.0)
    
    for anahtar, deger in sonuc.items():
        print(f"{anahtar}: {deger}")