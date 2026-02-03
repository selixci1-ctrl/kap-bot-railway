import os
import requests
from bs4 import BeautifulSoup
import time

# ===========================
# Ayarlar
# ===========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN veya CHAT_ID eksik! Railway Variables kontrol et.")

URL = "https://www.kap.org.tr/tr/Bildirimler"

# FILTER_WORDS geçici olarak kaldırıldı, test için tüm haberleri çekecek
FILTER_WORDS = []

CHECK_INTERVAL = 90  # saniye
TEST_MODE = True     # True olursa her haberi log'a yazdırır

# ===========================
# Telegram bildirim fonksiyonu
# ===========================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ===========================
# KAP'tan haberleri çekme
# ===========================
def get_haberler():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("tbody tr")

    haberler = []

    for row in rows:
        text = row.get_text(" ", strip=True)

        # Filtreyi geçici olarak kaldırıyoruz, tüm haberler loglanacak
        haberler.append(text)

        if TEST_MODE:
            print(f"[TEST] Haber bulundu: {text}")

    if TEST_MODE:
        print(f"[TEST] Toplam haber sayısı: {len(haberler)}")

    return haberler

# ===========================
# Ana döngü
# ===========================
def main():
    send("✅ KAP Bot Başladı")

    old = set()

    while True:
        try:
            haberler = get_haberler()

            for h in haberler:
                if h not in old:
                    send("📢 Yeni KAP Haberi:\n\n" + h)
                    old.add(h)

            if not haberler:
                if TEST_MODE:
                    print("[TEST] Yeni haber yok, bekleniyor...")

        except Exception as e:
            send("❌ Hata:\n" + str(e))
            if TEST_MODE:
                print(f"[TEST] Hata oluştu: {e}")

        time.sleep(CHECK_INTERVAL)

# ===========================
# Çalıştır
# ===========================
if __name__ == "__main__":
    main()
