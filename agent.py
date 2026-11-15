import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

emb = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
db = Chroma(persist_directory="chroma_db", embedding_function=emb)
retriever = db.as_retriever(search_kwargs={"k": 2})

VERI = {
    "1001": {"bakiye": 15400.50,
             "islemler": ["Market -320 TL", "Maaş +25000 TL", "Fatura -410 TL"]},
}

@tool
def kredi_taksiti(tutar: float, vade_ay: int, aylik_faiz_yuzde: float) -> str:
    """Kredi için aylık taksit tutarını hesaplar."""
    r = aylik_faiz_yuzde / 100
    taksit = tutar * r / (1 - (1 + r) ** -vade_ay)
    return f"Aylık taksit: {taksit:.2f} TL"

@tool
def hesap_bilgisi(musteri_no: str) -> str:
    """Müşteri numarasına göre bakiyeyi ve son işlemleri getirir."""
    k = VERI.get(musteri_no)
    return str(k) if k else "Müşteri bulunamadı."

@tool
def bilgi_ara(soru: str) -> str:
    """Kart aidatı, limit, erken kapatma, vade, EFT/havale gibi genel banka kuralları için bilgi arar."""
    docs = retriever.invoke(soru)
    return "\n\n".join(d.page_content for d in docs)

agent = create_agent(
    model="google_genai:" + os.environ.get("MODEL", "gemini-3.5-flash-lite"),
    tools=[kredi_taksiti, hesap_bilgisi, bilgi_ara],
    system_prompt="Bir banka destek asistanısın. Sadece araçlardan gelen bilgiye dayan. "
                  "Araçlarda bilgi yoksa bilmediğini söyle. "
    "Para transferi, kart iptali gibi işlemleri yapamazsın; bunu kullanıcıya açıkça söyle.",
)

def metin(m):
    c = m.content
    if isinstance(c, str):
        return c
    return "".join(b.get("text", "") for b in c if isinstance(b, dict))

def sor(soru):
    res = agent.invoke({"messages": [{"role": "user", "content": soru}]})
    araclar = [tc["name"] for m in res["messages"] for tc in (getattr(m, "tool_calls", None) or [])]
    print("Soru:", soru)
    print("Kullanılan araçlar:", araclar)
    print("Cevap:", metin(res["messages"][-1]))
    print()

if __name__ == "__main__":
    sor("Kredi kartı aidatı ne kadar, 1001 numaralı müşterinin bakiyesi nedir "
        "ve 100000 TL'yi 24 ayda aylık %3 faizle çeksem taksit ne olur?")
