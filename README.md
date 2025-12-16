🚗 İkinci El Araç Fiyat Tahmin Sistemi
Bu proje, ikinci el araç piyasasındaki verileri Web Scraping yöntemleriyle toplayan, temizleyen, makine öğrenmesi algoritmalarıyla eğiten ve kullanıcılara araç özelliklerine (marka, model, yıl, km vb.) göre en doğru fiyat tahminini sunmak amacıyla geliştirilmiştir bir Web Arayüzü sunan uçtan uca bir veri bilimi projesidir.

🌟 Temel Özellikler
Makine Öğrenmesi Modeli: Toplanan verilerle eğitilen fiyat tahmin modeli.
Otomatik Veri Toplama (Web Scraping): Selenium kullanılarak popüler araç sitesinden güncel veriler dinamik olarak çekilir.
Veri Ön İşleme & Mühendisliği: Eksik verilerin temizlenmesi, Label Encoding ile kategorik verilerin sayısallaştırılması.
Git LFS Entegrasyonu: Büyük boyutlu model dosyalarının (.pkl) versiyon kontrol sistemiyle yönetimi.

🚀 Kurulum ve Çalıştırma
1. Projeyi Klonlayın:
   ```bash
git clone [https://github.com/azraaabes/car-price-prediction.git](https://github.com/azraaabes/car-price-prediction.git)
cd car-price-prediction
```
2. Sanal Ortamı Oluşturun:
```bash
python -m venv venv
# Windows için:
.\venv\Scripts\activate
# Mac/Linux için:
source venv/bin/activate
```
3. Gerekli Kütüphaneleri Yükleyin:
```bash
pip install -r requirements.txt
```
4. Uygulamayı Başlatın
```bash
streamlit run app.py
```
