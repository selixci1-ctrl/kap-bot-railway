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
        first_run = True  # İlk çalıştırmayı kontrol için flag

        while True:
            try:
                haberler = get_haberler(driver)

                for h in haberler:
                    # Eğer ilk çalıştırma veya haber daha önce gönderilmemişse
                    if first_run or h not in old:
                        send("📢 KAP Haberi:\n\n" + h)
                        old.add(h)

                first_run = False  # İlk döngü tamamlandı

                if not haberler and TEST_MODE:
                    print("[TEST] Yeni haber yok, bekleniyor...")

            except Exception as e:
                send("❌ Hata:\n" + str(e))
                if TEST_MODE:
                    print(f"[TEST] Hata oluştu: {e}")

            time.sleep(CHECK_INTERVAL)

    finally:
        driver.quit()
