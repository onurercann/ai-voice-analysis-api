import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# 1. Ortam Değişkenlerini Yükle (.env içindeki API Key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print("--- RAG Sistemi Başlatılıyor ---")

# 2. PDF Dosyasını Yükle
# (Senin dosya adın farklıysa burayı değiştir)
pdf_path = "bilgi.pdf" 

if not os.path.exists(pdf_path):
    print(f"HATA: {pdf_path} dosyası bulunamadı! Lütfen klasöre bir PDF at.")
    exit()

print(f"1. PDF Yükleniyor: {pdf_path}")
loader = PyPDFLoader(pdf_path)
docs = loader.load()

# 3. Metni Parçala (Chunking)
# Yapay zekaya 100 sayfalık kitabı tek seferde veremeyiz.
# Küçük parçalara (Chunk) bölmemiz lazım.
print("2. Metin parçalanıyor...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, # Her parça 1000 karakter olsun
    chunk_overlap=100 # Parçalar birbirinin ucundan 100 karakter tekrar etsin (bağlam kopmasın)
)
splits = text_splitter.split_documents(docs)

# 4. Vektör Veritabanı Oluştur (Embedding)
# Metinleri sayısal vektörlere çevirip FAISS içine gömüyoruz.
print("3. Vektör veritabanı oluşturuluyor (Bu biraz sürebilir)...")
embeddings = OpenAIEmbeddings(api_key=api_key)
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

# 5. Arama Motorunu Hazırla (Retriever)
retriever = vectorstore.as_retriever()

# 6. Beyni Hazırla (LLM)
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, api_key=api_key)

# 7. Zinciri Kur (Chain)
# Soru Gelir -> Vektörde Ara -> Parçaları Bul -> LLM'e Gönder -> Cevap Ver
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

print("\n✅ SİSTEM HAZIR! PDF Hakkında soru sorabilirsin.")
print("(Çıkmak için 'q' bas)")

while True:
    soru = input("\nSoru: ")
    if soru.lower() == 'q':
        break
    
    # Soruyu zincire gönder
    sonuc = qa_chain.invoke({"query": soru})
    
    print(f"Cevap: {sonuc['result']}")