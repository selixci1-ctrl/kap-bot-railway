import os
import time
import requests

# ======================
# ENV
# ======================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("MKK_API_KEY")

if not all([TOKEN, CHAT_ID, API_KEY]):
    raise Exception("TOKEN / CHAT_ID / MKK_API_KEY eksik")

# ======================
# URLS
# ======================
BASE = "https://apiportal.mkk.com.tr/api"
LAST = f"{BASE}/kap/v1/lastDisclosureIndex"
LIST = f"{BASE}/kap/v1/disclosures"
DETAIL = f"{BASE}/kap/v1/disclosureDetail"

HEADERS = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

CHECK_INTERVAL = 90
TIMEOUT = 15


# ======================
# TELEGRAM
# ======================
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=15
        )
    except:
        pass


# ======================
# FREE PROXY LIST
# ======================
def get_free_proxies():

    url = "https://www.proxy-list.download/api/v1/get?type=https"

    r = requests.get(url, timeout=20)

    proxies = r.text.splitlines()

    print("Proxy bulundu:", len(proxies))

    return proxies


# ======================
# FIND WORKING PROXY
# ======================
def find_working_proxy():

    proxies = get_free_proxies()

    test_url = LAST

    for p in proxies:

        proxy = {
            "http": f"http://{p}",
            "https": f"http://{p}"
        }

        try:

            r = requests.get(
                test_url,
                headers=HEADERS,
                proxies=proxy,
                timeout=8
            )

            if r.status_code == 200:
                print("ÇALIŞAN PROXY:", p)
                send("✅ Proxy bulundu: " + p)
                return proxy

        except:
            continue

    return None


# ======================
# MAIN
# ======================
def main():

    send("🚀 Proxy Tarama Botu Başladı")

    proxy = find_working_proxy()

    if not proxy:
        send("❌ Çalışan proxy bulunamadı")
        return

    seen = set()
    first = True

    while True:

        try:

            last = requests.get(
                LAST,
                headers=HEADERS,
                proxies=proxy,
                timeout=TIMEOUT
            ).json()["lastDisclosureIndex"]

            r = requests.get(
                f"{LIST}?from={max(0,last-10)}",
                headers=HEADERS,
                proxies=proxy,
                timeout=TIMEOUT
            ).json()

            data = r.get("disclosures", [])

            print("Haber:", len(data))

            for item in data:

                idx = item["disclosureIndex"]

                if idx in seen and not first:
                    continue

                title = item.get("announcementTitle","")

                det = requests.get(
                    f"{DETAIL}/{idx}",
                    headers=HEADERS,
                    proxies=proxy,
                    timeout=TIMEOUT
                ).json()

                text = det.get("announcementDetail","")

                send(f"📢 {title}\n\n{text}")

                seen.add(idx)

            first = False

        except Exception as e:

            print("HATA:", e)
            send("⚠️ Proxy düştü, yenisi aranıyor...")

            proxy = find_working_proxy()

            if not proxy:
                send("❌ Yeni proxy bulunamadı")

        time.sleep(CHECK_INTERVAL)


# ======================
# RUN
# ======================
if __name__ == "__main__":
    main()
