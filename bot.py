import os
import requests
from bs4 import BeautifulSoup
import time

# Telegram bilgileri
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


URL = "https://www.kap.org.tr/tr/Bildirimler"

FILTER_WORDS = [
    "Yeni İş İlişkisi",
    "Finansal Rapor",
    "Sermaye Artırımı - Azaltımı İşlemlerine İlişkin Bildirim",
    "Payların Geri Alınmasına İlişkin Bildirim",
    "Esas Sözleşme Tadili"
]

CHECK_INTERVAL = 90  # saniye


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


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

        for word in FILTER_WORDS:
            if word in text:
                haberler.append(text)
                break

    return haberler


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
                print("Bekleniyor...")

        except Exception as e:
            send("❌ Hata:\n" + str(e))

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
