from fastapi import FastAPI, UploadFile, File
from services.openai_service import get_voice_transcription, analyze_sentiment

app = FastAPI()

@app.post("/ses-ile-analiz")
async def ses_analiz(dosya: UploadFile = File(...)):
    
    print(f"İşlem başladı: {dosya.filename}")

    ses_icerigi = await dosya.read()

    cevrilen_metin = get_voice_transcription(dosya.filename, ses_icerigi)

    print(f"Metin: {cevrilen_metin}")

    analiz_sonucu = analyze_sentiment(cevrilen_metin)

    return {
        "dosya": dosya.filename,
        "metin": cevrilen_metin,
        "analiz": analiz_sonucu
    }
        
@app.get("/")
def home():
    return {"message": "AI Call Center API Çalışıyor."}