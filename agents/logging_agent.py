import psutil

def check_system_health():
    # İşlemci ve RAM kullanım yüzdelerini okuyoruz
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    
    status = "HEALTHY"
    if cpu_usage > 85 or ram_usage > 85:
        status = "WARNING - Yüksek Kaynak Kullanımı!"
        
    report = f"Sistem Durumu: {status} | CPU: %{cpu_usage} | RAM: %{ram_usage}"
    return report

if __name__ == "__main__":
    print("Loglama Ajanı Çalışıyor...\n")
    print(check_system_health())