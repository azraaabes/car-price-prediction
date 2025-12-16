import streamlit as st
import pandas as pd
import joblib
import datetime
from selenium_scraper import ilanlari_tarat 

# -------------------------------------------------------------------------
# 1. AYARLAR
# -------------------------------------------------------------------------
st.set_page_config(page_title="AI Araç Fiyat", layout="wide")

# Şu anki yılı sabitliyoruz (İstersen burayı değiştirebilirsin)
GUNCEL_YIL = 2025 

# Hafıza Başlatma
if 'ai_tahmin' not in st.session_state: st.session_state['ai_tahmin'] = None
if 'piyasa_ortalamasi' not in st.session_state: st.session_state['piyasa_ortalamasi'] = None

# -------------------------------------------------------------------------
# 2. DOSYALARI YÜKLEME
# -------------------------------------------------------------------------
@st.cache_data
def load_data():
    try: return pd.read_csv("araba_verileri.csv")
    except: return None

@st.cache_resource
def load_model():
    try:
        model = joblib.load("araba_fiyat_modeli.pkl")
        encoders = joblib.load("label_encoders.pkl")
        return model, encoders
    except: return None, None

df = load_data()
model, encoders = load_model()

if df is None or model is None:
    st.error("HATA: Dosyalar bulunamadı. Lütfen önce 'python train_model.py' çalıştırın.")
    st.stop()

st.title("🚗 İkinci El Araç Fiyat Tahmin Sistemi")

# -------------------------------------------------------------------------
# 3. SOL MENÜ (SADECE ARAÇ SEÇİMİ)
# -------------------------------------------------------------------------
st.sidebar.header("Araç Özellikleri")

# Marka - Seri - Model Zinciri
marka_listesi = sorted(df['marka'].astype(str).unique())
secilen_marka = st.sidebar.selectbox("Marka", marka_listesi)

df_marka = df[df['marka'] == secilen_marka]
secilen_seri = st.sidebar.selectbox("Seri", sorted(df_marka['seri'].astype(str).unique()))

df_seri = df_marka[df_marka['seri'] == secilen_seri]
secilen_model = st.sidebar.selectbox("Model", sorted(df_seri['model'].astype(str).unique()))

# Model Yılı (Aracın Ruhsattaki Yılı)
uretim_yili_listesi = list(range(GUNCEL_YIL, 1999, -1))
secilen_uretim_yili = st.sidebar.selectbox("Model Yılı", uretim_yili_listesi)

st.sidebar.markdown("---")
secilen_vites = st.sidebar.selectbox("Vites Tipi", df['vites_tipi'].unique())
secilen_yakit = st.sidebar.selectbox("Yakıt Tipi", df['yakit_tipi'].unique())

# ENFLASYON AYARI (Sadece model eski kaldıysa düzeltmek için)
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Piyasa Düzeltmesi")
st.sidebar.caption("Modelin eğitimi eski kaldıysa bu oranı artırın.")
# Varsayılan olarak %100 (2 katı) enflasyon farkı ekledik. İstersen 0 yaparsın.
enflasyon_orani = st.sidebar.slider("Enflasyon / Piyasa Farkı (%)", 0, 300, 100, 10)


# -------------------------------------------------------------------------
# 4. OTOMATİK HESAPLAMA MOTORU (MANTIKSAL KISIM)
# -------------------------------------------------------------------------

# 1. Araç Yaşı (Bugüne Göre)
arac_yasi = GUNCEL_YIL - secilen_uretim_yili
if arac_yasi < 0: arac_yasi = 0 # 2025 modelse 0 yaş

# 2. Kilometre (Yaşa göre otomatik artar)
# Formül: 6.000 (Başlangıç) + (Yaş * 15.000)
hesaplanan_km = 6000.0 + (arac_yasi * 15000.0) 

# 3. Yıpranma (Yaşa göre)
tahmini_boyali = round(float(arac_yasi / 4.0), 1)
tahmini_degisen = round(float(arac_yasi / 6.0), 1)

# 4. Teknik Veriler (Veriden Çekme)
df_secilen_model = df_seri[df_seri['model'] == secilen_model]
ort_hacim = df_secilen_model['motor_hacmi'].mean()
hesaplanan_hacim = round(float(ort_hacim), 1) if not pd.isna(ort_hacim) else 1600.0
ort_guc = df_secilen_model['motor_gucu'].mean()
hesaplanan_guc = round(float(ort_guc), 0) if not pd.isna(ort_guc) else 110.0

# -------------------------------------------------------------------------
# 5. VERİ HAZIRLIĞI
# -------------------------------------------------------------------------
input_data = pd.DataFrame({
    'marka': [secilen_marka], 'seri': [secilen_seri], 'model': [secilen_model], 
    'yil': [secilen_uretim_yili],  
    'kilometre': [hesaplanan_km],  
    'vites_tipi': [secilen_vites], 'yakit_tipi': [secilen_yakit],    
    'kasa_tipi': ['Sedan'], 'renk': ['Beyaz'],                 
    'motor_hacmi': [hesaplanan_hacim], 'motor_gucu': [hesaplanan_guc],    
    'degisen_sayisi': [tahmini_degisen], 'boyali_sayisi': [tahmini_boyali],   
    'kimden': ['Sahibinden']
})

try:
    feature_order = joblib.load("feature_columns.pkl")
    for col in feature_order:
        if col not in input_data.columns: input_data[col] = 0
    input_data = input_data[feature_order]
except: pass

# -------------------------------------------------------------------------
# 6. EKRAN TASARIMI
# -------------------------------------------------------------------------

col_left, col_right = st.columns([1, 1])

# --- SOL TARAFA DETAYLI TABLO ---
with col_left:
    st.subheader("📋 Seçilen Araç Profili")
    
    profil_dict = {
        "Özellik": [
            "Marka / Model", 
            "Model Yılı", 
            "Araç Yaşı (Bugün)",
            "Tahmini Kilometre", 
            "Vites / Yakıt",
            "Motor Gücü",
            "Tahmini Boya/Değişen"
        ],
        "Değer": [
            f"{secilen_marka} {secilen_model}",
            secilen_uretim_yili,
            f"{arac_yasi} Yaşında",
            f"{hesaplanan_km:,.0f} km", 
            f"{secilen_vites} / {secilen_yakit}",
            f"{hesaplanan_guc} HP",
            f"{tahmini_boyali} Boya / {tahmini_degisen} Değişen"
        ]
    }
    st.table(pd.DataFrame(profil_dict))
    st.info(f"ℹ️ **Bilgi:** {secilen_uretim_yili} model bir aracın bugün ortalama **{hesaplanan_km:,.0f} km** yol yaptığı varsayılarak hesaplama yapılacaktır.")

# --- SAĞ TARAF: FİYAT ---
with col_right:
    st.subheader("💰 Fiyat Analizi")
    
    # 1. YAPAY ZEKA BUTONU
    if st.button("Fiyatı Hesapla (Yapay Zeka)", type="primary"):
        process_df = input_data.copy()
        for col in encoders:
            if col in process_df.columns:
                try: process_df[col] = encoders[col].transform(process_df[col].astype(str))
                except: process_df[col] = 0
        
        try:
            # A) HAM FİYAT (Modelin eski bildiği fiyat)
            ham_tahmin = model.predict(process_df)[0]
            
            # B) ENFLASYON DÜZELTMESİ (Güncel Piyasa İçin)
            # Senin dediğin %30 veya %100 farkı buraya ekliyoruz
            guncel_tahmin = ham_tahmin * (1 + enflasyon_orani / 100)

            st.session_state['ai_tahmin'] = guncel_tahmin
            
            st.markdown("### 📅 Güncel Piyasa Tahmini:")
            st.markdown(f"# ₺{guncel_tahmin:,.0f}")
            
            if enflasyon_orani > 0:
                st.caption(f"*Modelin ham tahmini ({ham_tahmin:,.0f} TL) üzerine %{enflasyon_orani} piyasa farkı eklenmiştir.*")
            
        except Exception as e:
            st.error(f"Hata: {e}")
            
    st.markdown("---")

    # 2. CANLI PİYASA BUTONU
    if st.button("Canlı Piyasayı Tara (Sahibinden vb.)"):
        with st.spinner(f"{secilen_uretim_yili} model {secilen_model} aranıyor..."):
            sonuc = ilanlari_tarat(secilen_marka, secilen_seri, secilen_uretim_yili)
            
        if sonuc["durum"] == "Başarılı":
            st.session_state['piyasa_ortalamasi'] = sonuc['ortalama_fiyat']
            st.success("İlanlar Bulundu!")
            st.metric(label="Gerçek Piyasa Ortalaması", 
                      value=f"{sonuc['ortalama_fiyat']:,.0f} TL",
                      delta=f"{sonuc['ilan_sayisi']} ilan")
        else:
            st.error(sonuc["mesaj"])

# --- SONUÇ KARŞILAŞTIRMASI ---
if st.session_state['ai_tahmin'] is not None and st.session_state['piyasa_ortalamasi'] is not None:
    st.markdown("---")
    st.header("📊 Sonuç Karşılaştırması")
    
    ai_fiyat = st.session_state['ai_tahmin']
    piyasa_fiyat = st.session_state['piyasa_ortalamasi']
    fark = ai_fiyat - piyasa_fiyat
    
    c1, c2, c3 = st.columns(3)
    c1.metric("AI Tahmini", f"{ai_fiyat:,.0f} TL")
    c2.metric("Piyasa Ortalaması", f"{piyasa_fiyat:,.0f} TL")
    c3.metric("Fark", f"{fark:,.0f} TL", delta_color="inverse")
    
    if fark < 0:
        st.success(f"✅ **Fırsat!** Yapay zeka, bu aracın piyasadan **{abs(fark):,.0f} TL daha ucuza** bulunması gerektiğini düşünüyor.")
    else:
        st.warning(f"⚠️ Yapay zeka tahmini piyasanın biraz üzerinde.")