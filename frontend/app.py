import requests
import streamlit as st

st.write(f"Şu anki Sürüm: {st.__version__}")

st.title("AI Call Center Asistanı 🤖")

st.sidebar.header("Sistem Durumu")

uploaded_file = st.sidebar.file_uploader("Ses Dosyasını Yükleyin", type="m4a")

if uploaded_file is not None:
    st.sidebar.success("Dosya Yüklendi!")
    
    if st.sidebar.button("Analiz Et"):
        st.sidebar.info("Analiz Başlıyor...")
        
        try:
            response = requests.post("http://localhost:8000/ses-ile-analiz", files={"dosya": uploaded_file})
            
            if response.status_code == 200:
                data = response.json()
                st.sidebar.success("Analiz Tamamlandı!")
                st.sidebar.write("Metin: ", data["metin"])
                st.sidebar.write("Duygu: ", data["analiz"])
            else:
                st.sidebar.error("Backend hata verdi!")
                
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Bir hata oluştu: {e}")

try:
    requests.get("http://localhost:8000/saglik-kontrolu")
    st.sidebar.success("Sistem Aktif!")
except:
    st.sidebar.error("Bağlantı Hatası! Backend çalışıyor mu?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post("http://localhost:8000/pdf-ile-sohbet", json={"soru": prompt})

        if response.status_code == 200:
            bot_cevabi = response.json().get("cevap")
            with st.chat_message("assistant"):
                st.markdown(bot_cevabi)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_cevabi})

        else:
            st.error("Backend hata verdi!")

    except requests.exceptions.RequestException as e:
        st.error(f"Bir hata oluştu: {e}")
