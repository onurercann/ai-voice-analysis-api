import streamlit as st
import requests
import pandas as pd
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Call Center", page_icon="🤖")
st.title("AI Call Center Asistanı 🤖")

# --- SIDEBAR (YAN MENÜ) ---
st.sidebar.header("Sistem Durumu")

# 1. Yöntem Seçimi (Dosya mı Mikrofon mu?)
st.sidebar.header("Ses Analizi")
yontem = st.sidebar.radio("Yöntem Seçiniz:", ["Dosya Yükle", "Mikrofonla Kaydet"])

uploaded_file = None

if yontem == "Dosya Yükle":
    # Dosya yükleme aracı
    uploaded_file = st.sidebar.file_uploader("Ses Dosyasını Yükleyin", type=["m4a", "mp3", "wav"])
else:
    # Mikrofon kayıt aracı (Streamlit 1.40+ özelliği)
    uploaded_file = st.sidebar.audio_input("Sesinizi Kaydedin")

# 2. Ortak Analiz Butonu
if uploaded_file is not None:
    st.sidebar.success("Ses Verisi Hazır!")
    
    if st.sidebar.button("Analiz Et"):
        st.sidebar.info("Analiz Başlıyor...")
        
        try:
            # Backend'e gönder (Hem mikrofon hem dosya aynı formatta gider)
            response = requests.post("http://localhost:8000/ses-ile-analiz", files={"dosya": uploaded_file})
            
            if response.status_code == 200:
                data = response.json()
                st.sidebar.success("Analiz Tamamlandı!")
                st.sidebar.write("**Metin:**", data["metin"])
                st.sidebar.write("**Duygu:**", data["analiz"])
            else:
                st.sidebar.error("Backend hata verdi!")
                
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Bir hata oluştu: {e}")

# 3. Rapor Geçmişi (CSV)
st.sidebar.markdown("---")
if st.sidebar.checkbox("Rapor Geçmişini Göster"):
    csv_yolu = "cagri_gecmisi.csv"
    
    if os.path.exists(csv_yolu):
        df = pd.read_csv(csv_yolu)
        st.write("### 📊 Çağrı Analiz Raporu")
        st.dataframe(df)
        
        st.write("### 📈 Duygu İstatistikleri")
        duygu_dagilimi = df["Duygu Durumu"].value_counts()
        st.bar_chart(duygu_dagilimi)
    else:
        st.warning("Henüz hiç kayıt bulunamadı!")

# 4. Sağlık Kontrolü (Backend Ayakta mı?)
st.sidebar.markdown("---")
try:
    requests.get("http://localhost:8000/saglik-kontrolu")
    st.sidebar.success("Sistem Aktif!")
except:
    st.sidebar.error("Bağlantı Hatası! Backend çalışıyor mu?")


# --- ANA EKRAN (CHAT) ---

# Hafızayı Başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Yeni Mesaj Girişi
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # Kullanıcı mesajını göster ve kaydet
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Backend'e sor
    try:
        response = requests.post("http://localhost:8000/pdf-ile-sohbet", json={"soru": prompt})

        if response.status_code == 200:
            bot_cevabi = response.json().get("cevap")
            
            # Botun cevabını göster ve kaydet
            with st.chat_message("assistant"):
                st.markdown(bot_cevabi)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_cevabi})

        else:
            st.error("Backend hata verdi!")

    except requests.exceptions.RequestException as e:
        st.error(f"Bir hata oluştu: {e}")