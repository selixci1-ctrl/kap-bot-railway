import os
import time
import requests

# ===========================
# Ayarlar
# ===========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("TOKEN veya CHAT_ID eksik! Railway Variables kontrol et.")

# Deneme API endpointi (JSON dönüyorsa çalışır)
API_URL = "https://www.kap.org.tr/tr/api/disclosures"
CHECK_INTERVAL = 90  # saniye
TEST_MODE = True      # True olursa loglara basar

# ===========================
# Telegram bildirim fonksiyonu
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
# Bot ana döngüsü
# ===========================
def main():
    send("✅ KAP API Bot Başladı")
    old_ids = set()

    while True:
        try:
            r = requests.get(API_URL, timeout=30)
            data = r.json()  # JSON dönüyorsa parse edilir

            # data["disclosures"] veya benzeri bir alan olabilir
            disclosures = data.get("disclosures", [])
            if TEST_MODE:
                print(f"[TEST] Toplam çekilen haber sayısı: {len(disclosures)}")

            for item in disclosures:
                # Örnek alanlar: disclosureIndex (unique), announcementTitle (başlık)
                idx = item.get("disclosureIndex")
                title = item.get("announcementTitle") or str(item)

                if idx and idx not in old_ids:
                    send(f"📢 Yeni KAP Bildirimi:\n{title}")
                    old_ids.add(idx)

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
