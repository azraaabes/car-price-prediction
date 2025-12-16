from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def ilanlari_tarat(marka, seri, yil):
    
    # URL için metni uygun hale getirir (Örn: "3 Serisi" -> "3-serisi")
    def slugify(text):
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text).strip()
        text = re.sub(r'[\s_]+', '-', text)
        tr_map = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'}
        for k, v in tr_map.items():
            text = text.replace(k, v)
        return text

    # Ayarlar
    chrome_options = Options()
    chrome_options.add_argument("--incognito") # Gizli sekme
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # Tarayıcıyı kandırmak için User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    bulunan_fiyatlar = []
    
    try:
        # Tarayıcıyı başlat
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        marka_slug = slugify(marka)
        seri_slug = slugify(seri)
        
        # Site adresi oluşturuluyor
        target_url = (
            f"https://www.arabam.com/ikinci-el/otomobil/{marka_slug}-{seri_slug}"
            f"?minYear={yil}&maxYear={yil}"
        )
        print(f"Adrese gidiliyor: {target_url}")
        
        driver.get(target_url)
        
        # Çerez uyarısını kapatmayı dene
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
        except:
            pass 
        
        # Fiyatları topla
        xpath_genel_fiyat = "//tr[starts-with(@id, 'listing')]//td//span[contains(text(), 'TL')]"
        fiyat_elementleri = driver.find_elements(By.XPATH, xpath_genel_fiyat)

        for element in fiyat_elementleri[:15]: # İlk 15 ilana bak
            try:
                text = element.text.strip()
                # "1.250.000 TL" -> 1250000 yap
                temiz_fiyat = float(text.replace("TL", "").replace(".", "").replace(",", "").strip())
                if temiz_fiyat > 50000: 
                    bulunan_fiyatlar.append(temiz_fiyat)
            except:
                continue

        if len(bulunan_fiyatlar) > 0:
            return {
                "durum": "Başarılı",
                "ortalama_fiyat": sum(bulunan_fiyatlar) / len(bulunan_fiyatlar),
                "min_fiyat": min(bulunan_fiyatlar),
                "ilan_sayisi": len(bulunan_fiyatlar)
            }
        else:
            return {"durum": "Hata", "mesaj": "İlan bulunamadı."}

    except Exception as e:
        return {"durum": "Hata", "mesaj": str(e)}
    finally:
        if driver:
            driver.quit()