import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

# ===========================
# Ayarlar
# ===========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN veya CHAT_ID eksik! Railway Variables kontrol et.")

URL = "https://www.kap.org.tr/tr/Bildirimler"

FILTER_WORDS = [
    "Yeni İş İlişkisi",
    "Finansal Rapor",
    "Sermaye Artırımı - Azaltımı İşlemlerine İlişkin Bildirim",
    "Payların Geri Alınmasına İlişkin Bildirim",
    "Esas Sözleşme Tadili"
]

CHECK_INTERVAL = 90  # saniye
TEST_MODE = True     # True olursa loglar

PAGE_LOAD_TIMEOUT = 60  # Sayfa yükleme timeout
SLEEP_AFTER_LOAD = 12    # Sayfa yüklenince bekleme süresi

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
# Selenium ile KAP'tan haber çekme
# ===========================
def get_haberler(driver):
    driver.get(URL)
    time.sleep(SLEEP_AFTER_LOAD)  # Sayfanın tamamen yüklenmesini bekle

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    haberler = []

    for row in rows:
        text = row.text.strip()
        for word in FILTER_WORDS:
            if word in text:
                haberler.append(text)
                if TEST_MODE:
                    print(f"[TEST] Haber bulundu: {text}")
                break

    if TEST_MODE:
        print(f"[TEST] Toplam haber sayısı: {len(haberler)}")

    return haberler

# ===========================
# Ana döngü
# ===========================
def main():
    send("✅ KAP Bot Başladı")

    old = set()

    # Selenium ayarları
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Railway için headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    try:
        while True:
            try:
                haberler = get_haberler(driver)

                for h in haberler:
                    if h not in old:
                        send("📢 Yeni KAP Haberi:\n\n" + h)
                        old.add(h)

                if not haberler and TEST_MODE:
                    print("[TEST] Yeni haber yok, bekleniyor...")

            except Exception as e:
                send("❌ Hata:\n" + str(e))
                if TEST_MODE:
                    print(f"[TEST] Hata oluştu: {e}")

            time.sleep(CHECK_INTERVAL)

    finally:
        driver.quit()

# ===========================
# Çalıştır
# ===========================
if __name__ == "__main__":
    main()
