import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://www.kap.org.tr/tr/Bildirimler"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(60)

try:
    driver.get(URL)
    time.sleep(18)  # Sayfanın tamamen yüklenmesini bekle

    # Tüm divleri çekiyoruz
    all_divs = driver.find_elements(By.CSS_SELECTOR, "div")
    print(f"Toplam div sayısı: {len(all_divs)}")

    # İlk 50 divin textlerini yazdır
    for i, div in enumerate(all_divs[:50]):
        print(f"[{i}] {div.text}\n---")

finally:
    driver.quit()
