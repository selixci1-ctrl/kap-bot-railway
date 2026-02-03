import os
import requests
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN veya CHAT_ID eksik! Railway Variables kontrol et.")

API_URL = "https://www.kap.org.tr/tr/api/disclosures"  # Deneme endpoint
CHECK_INTERVAL = 90

def send(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def main():
    send("✅ KAP API Bot Başladı")
    old_ids = set()

    while True:
        try:
            r = requests.get(API_URL, timeout=30)
            data = r.json()  # Eğer JSON dönüyorsa

            # Örneğin: data["disclosures"] veya benzeri bir alan olabilir
            for item in data.get("disclosures", []):
                idx = item.get("disclosureIndex")
                text = item.get("announcementTitle") or str(item)
                if idx and idx not in old_ids:
                    send(f"📢 Yeni KAP Bildirimi:\n{text}")
                    old_ids.add(idx)

            print(f"[TEST] Toplam çekilen: {len(old_ids)}")

        except Exception as e:
            send(f"❌ Hata:\n{e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
