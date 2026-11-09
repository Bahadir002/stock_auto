def check_portfolio_correlation(proposed_symbol, current_portfolio):
    # Eğer sembolün içinde '/' varsa veya 'USD' geçiyorsa bu bir kripto varlıktır (Dinamik Tarama Uyumu)
    proposed_is_crypto = "/" in proposed_symbol or "USD" in proposed_symbol
    proposed_is_tech = any(t in proposed_symbol for t in ["AAPL", "MSFT", "NVDA", "GOOGL"])
    
    crypto_count = sum(1 for asset in current_portfolio if "/" in asset or "USD" in asset)
    tech_count = sum(1 for asset in current_portfolio if any(t in asset for t in ["AAPL", "MSFT", "NVDA", "GOOGL"]))
    
    # Kural 1: Portföyde aynı anda maksimum 2 aktif kripto varlık olabilir
    if proposed_is_crypto and crypto_count >= 2:
        return "RED: Portföyde maksimum kripto riskine ulaşıldı. Korelasyon çok yüksek."
        
    # Kural 2: Portföyde maksimum 2 teknoloji hissesi olabilir
    if proposed_is_tech and tech_count >= 2:
        return "RED: Teknoloji sektörüne aşırı yığılma tespit edildi."
        
    return "ONAY: Korelasyon riski düşük, portföy dağılımı dengeli."

if __name__ == "__main__":
    print("Korelasyon Ajanı Çalışıyor...\n")
    # Mevcut portföyümüzde ETH ve SOL olduğunu, sistemin yeni olarak BTC almak istediğini varsayalım:
    test_portfolio = ["ETHUSDT", "SOLUSDT", "TSLA"]
    print(check_portfolio_correlation("BTCUSDT", test_portfolio))