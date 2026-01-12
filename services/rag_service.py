import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --- GLOBAL DEĞİŞKENLER ---
# Veritabanını uygulama açılırken bir kere oluşturacağız, hafızada tutacağız.
qa_chain = None

def initialize_rag_system(pdf_path="bilgi.pdf"):
    """
    Sistemi başlatır: PDF'i okur, vektör veritabanını kurar ve zinciri hazırlar.
    """
    global qa_chain
    
    if not os.path.exists(pdf_path):
        print(f"UYARI: {pdf_path} bulunamadı! RAG servisi çalışmayacak.")
        return

    print("--- RAG Sistemi Yükleniyor (Bu işlem bir kez yapılır) ---")
    
    # 1. PDF Yükle
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Parçala
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # 3. Vektör DB Oluştur
    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = FAISS.from_documents(splits, embeddings)

    # 4. Zinciri Kur
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    print("✅ RAG Sistemi Hazır!")

def ask_pdf(question):
    """
    Kullanıcının sorusunu alır, PDF'ten cevaplar.
    """
    if qa_chain is None:
        return "Sistem henüz hazır değil veya PDF dosyası yok."
    
    # Soruyu sor ve cevabı al
    response = qa_chain.invoke({"query": question})
    return response['result']

def get_rag_readiness():
    """
    RAG sisteminin (qa_chain) dolu olup olmadığını kontrol eder.
    """
    if qa_chain is not None:
        return True
    else:
        return False