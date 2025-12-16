import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

print("🚀 Model eğitimi başlatılıyor...")

# 1. Veriyi Yükle
df = pd.read_csv("araba_verileri.csv")

# --- DÜZELTME BURADA: Eğer veride 'id' sütunu varsa, onu atıyoruz ---
if 'id' in df.columns:
    df = df.drop('id', axis=1)
    print("ℹ️ 'id' sütunu eğitimden çıkarıldı.")

df = df.dropna()

# 2. Yazıları Sayıya Çevir (Encoding)
encoders = {}
kategorik_sutunlar = ['marka', 'seri', 'model', 'vites_tipi', 'yakit_tipi', 'kasa_tipi', 'renk', 'kimden']

for col in kategorik_sutunlar:
    le = LabelEncoder()
    # Tüm veriyi görerek eğit
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le 

# 3. Eğitime Başla
X = df.drop("fiyat", axis=1) # Fiyat hariç her şey girdi
y = df["fiyat"]              # Fiyat hedef

# Sütun sırasını kaydedelim (app.py'da aynı sırada göndermek önemli)
feature_columns = list(X.columns)
joblib.dump(feature_columns, "feature_columns.pkl")

# Modeli oluştur
model = RandomForestRegressor(n_estimators=50, random_state=42) # Ağaç sayısını biraz artırdım
model.fit(X, y)

# 4. Modeli Kaydet
joblib.dump(model, "araba_fiyat_modeli.pkl")
joblib.dump(encoders, "label_encoders.pkl")

print(f"✅ Model başarıyla eğitildi ve kaydedildi!")
print(f"Eğitilen Sütunlar: {feature_columns}")