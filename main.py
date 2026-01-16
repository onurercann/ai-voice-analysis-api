from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from contextlib import asynccontextmanager
import csv
import os
from datetime import datetime

# Servislerimizi import ediyoruz
from services.openai_service import get_voice_transcription, analyze_sentiment
from services.rag_service import initialize_rag_system, ask_pdf, get_rag_readiness

# --- LIFESPAN (YAŞAM DÖNGÜSÜ) ---
# FastAPI açılırken veritabanını kur, kapanırken temizle mantığı.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlarken çalışır
    initialize_rag_system("bilgi.pdf") 
    yield
    # Uygulama kapanırken çalışır (Şu an boş)

app = FastAPI(lifespan=lifespan)

# Soru için veri modeli
class SoruIstegi(BaseModel):
    soru: str

@app.post("/pdf-ile-sohbet")
def pdf_sohbet(istek: SoruIstegi):
    # RAG servisine soruyu gönder
    cevap = ask_pdf(istek.soru)
    return {
        "soru": istek.soru,
        "cevap": cevap
    }

# --- ESKİ ENDPOINTLERİN DURUYOR ---

@app.post("/ses-ile-analiz")
async def ses_analiz(dosya: UploadFile = File(...)):
    print(f"İşlem başladı: {dosya.filename}")
    ses_icerigi = await dosya.read()
    cevrilen_metin = get_voice_transcription((dosya.filename, ses_icerigi))
    analiz_sonucu = analyze_sentiment(cevrilen_metin)
    csv_dosyasi = "cagri_gecmisi.csv"
    dosya_var_mi = os.path.exists(csv_dosyasi)
    zaman_damgasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(csv_dosyasi, mode="a", newline="", encoding="utf-8") as file:
        yazici = csv.writer(file)
        if not dosya_var_mi:
            yazici.writerow(["Tarih", "Dosya Adı", "Duygu Durumu", "Metin"])
            yazici.writerow([zaman_damgasi, dosya.filename, analiz_sonucu, cevrilen_metin])
    
    return {
        "dosya": dosya.filename,
        "metin": cevrilen_metin,
        "analiz": analiz_sonucu
    }

@app.get("/")
def home():
    return {"message": "AI Call Center API Çalışıyor 🚀"}

@app.get("/saglik-kontrolu")
def saglik_kontrolu_endpoint():  # Fonksiyon ismini değiştirdik!
    
    # Servis katmanındaki fonksiyonu çağırıyoruz
    durum = get_rag_readiness()
    
    if durum == True:
        return {"durum": "aktif", "mesaj": "RAG sistemi bomba gibi çalışıyor 🚀"}
    else:
        return {"durum": "pasif", "mesaj": "Sistem henüz yüklenemedi ⚠️"}
