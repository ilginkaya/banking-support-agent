from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

metin = open("sss.txt", encoding="utf-8").read()
parcalar = [p.strip() for p in metin.split("\n\n") if p.strip()]

emb = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
db = Chroma.from_texts(parcalar, emb, persist_directory="chroma_db")
print("Yüklenen parça sayısı:", len(parcalar))

for s in db.similarity_search("Kart aidatı ne kadar?", k=2):
    print("-", s.page_content)
