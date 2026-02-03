import os
import time
import requests

# ===========================
# Telegram
# ===========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN veya CHAT_ID eksik!")

# ===========================
# KAP API
# ===========================
API_KEY = os.getenv("MKK_API_KEY")  # MKK API portalından aldığın key
BASE_URL = "https://apiportal.mkk.com.tr/api"

DISCLOSURES_URL = f"{BASE_URL}/kap/v1/disclosures"
LAST_INDEX_URL = f"{BASE_URL}/kap/v1/lastDisclosureIndex"
DETAIL_URL = f"{BASE_URL}/kap/v1/disclosureDetail"

HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY}
CHECK_INTERVAL = 90

# ===========================
# Telegram gönderim fonksiyonu
# ===========================
def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

# ===========================
# Bot döngüsü
# ===========================
def main():
    send("✅ KAP Bot Başladı")
    old_ids = set()

    while True:
        try:
            # Son haber ID
            r = requests.get(LAST_INDEX_URL, headers=HEADERS, timeout=30)
            r.raise_for_status()
            last_index = r.json().get("lastDisclosureIndex")

            # Son 10 haberi çek
            r2 = requests.get(f"{DISCLOSURES_URL}?from={last_index-10}", headers=HEADERS, timeout=30)
            r2.raise_for_status()
            data = r2.json().get("disclosures", [])

            for item in data:
                idx = item.get("disclosureIndex")
                title = item.get("announcementTitle")

                if idx and idx not in old_ids:
                    # Detayı al
                    det = requests.get(f"{DETAIL_URL}/{idx}", headers=HEADERS, timeout=30).json()
                    text = det.get("announcementDetail") or title

                    send(f"📢 KAP Yeni Bildirim:\n{title}\n\n{text}")
                    old_ids.add(idx)

        except Exception as e:
            send(f"❌ Hata:\n{e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
