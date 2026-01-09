import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_voice_transcription(file_tuple):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=file_tuple
    )
    return transcription.text

def analyze_sentiment(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir çağrı merkezi asistanısın. Analiz et. Çıktı formatı: DUYGU - ÖZET"},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content