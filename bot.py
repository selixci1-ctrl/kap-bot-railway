import os
import time
import requests

# ===========================
# Ayarlar
# ===========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("MKK_API_KEY")  # MKK API Key

if not TOKEN or not CHAT_ID or not API_KEY:
    raise Exception("TOKEN, CHAT_ID veya MKK_API_KEY eksik! Railway Variables kontrol et.")

BASE_URL = "https://apiportal.mkk.com.tr/api"
DISCLOSURES_URL = f"{BASE_URL}/kap/v1/disclosures"
LAST_INDEX_URL = f"{BASE_URL}/kap/v1/lastDisclosureIndex"
DETAIL_URL = f"{BASE_URL}/kap/v1/disclosureDetail"

HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY}

CHECK_INTERVAL = 90      # saniye
TEST_MODE = True         # True olursa log ve test mesajı
RETRY_COUNT = 3          # API hatasında deneme sayısı
RETRY_DELAY = 5          # Denemeler arası bekleme (saniye)
TIMEOUT = 60             # requests timeout (saniye)

# ===========================
# Telegram gönderim fonksiyonu
# ===========================
def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        if TEST_MODE:
            print(f"[TEST] Telegrama gönderildi:\n{msg}\n---")
    except Exception as e:
        print(f"[TEST] Telegram gönderim hatası: {e}")

# ===========================
# requests.get için retry fonksiyonu
# ===========================
def get_with_retry(url, headers):
    for i in range(RETRY_COUNT):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"[Retry {i+1}] Hata: {e}")
            time.sleep(RETRY_DELAY)
    raise Exception(f"{url} için tüm denemeler başarısız oldu")

# ===========================
# Bot ana döngüsü
# ===========================
def main():
    send("✅ KAP API Bot Başladı")
    old_ids = set()
    first_run = True

    while True:
        try:
            # Son ID kontrolü
            r = get_with_retry(LAST_INDEX_URL, HEADERS)
            last_index = r.json().get("lastDisclosureIndex", 0)

            # Son 10 haberi çek
            r2 = get_with_retry(f"{DISCLOSURES_URL}?from={max(0,last_index-10)}", HEADERS)
            data = r2.json().get("disclosures", [])

            if TEST_MODE:
                print(f"[TEST] Toplam çekilen haber sayısı: {len(data)}")

            for item in data:
                idx = item.get("disclosureIndex")
                title = item.get("announcementTitle", "Başlık yok")

                if idx and (first_run or idx not in old_ids):
                    # Detayı çek
                    det = get_with_retry(f"{DETAIL_URL}/{idx}", HEADERS).json()
                    text = det.get("announcementDetail") or title

                    send(f"📢 KAP Yeni Bildirim:\n{title}\n\n{text}")
                    old_ids.add(idx)

            # --- TEST için sahte haber ---
            if TEST_MODE and first_run:
                test_haber = {
                    "disclosureIndex": 999999,
                    "announcementTitle": "TEST HABERİ - BOT ÇALIŞIYOR"
                }
                if 999999 not in old_ids:
                    send(f"📢 {test_haber['announcementTitle']}")
                    old_ids.add(999999)
            # --- TEST sonu ---

            first_run = False

        except Exception as e:
            send(f"❌ Hata:\n{e}")
            if TEST_MODE:
                print(f"[TEST] Hata oluştu: {e}")

        time.sleep(CHECK_INTERVAL)

# ===========================
# Çalıştır
# ===========================
if __name__ == "__main__":
    main()
