import os
import time
from langchain.chat_models import init_chat_model
from agent import kredi_taksiti, hesap_bilgisi, bilgi_ara

SYSTEM = ("Bir banka destek asistanısın. Sadece araçlardan gelen bilgiye dayan. "
          "Araçlarda bilgi yoksa bilmediğini söyle. "
    "Para transferi, kart iptali gibi işlemleri yapamazsın; bunu kullanıcıya açıkça söyle.")
llm = init_chat_model("google_genai:" + os.environ.get("MODEL", "gemini-3.5-flash-lite")).bind_tools(
    [kredi_taksiti, hesap_bilgisi, bilgi_ara])

TEST = [
    ("Kredi kartı yıllık aidatı ne kadar?", {"bilgi_ara"}),
    ("Kartım kaybolursa ne yapmalıyım?", {"bilgi_ara"}),
    ("Erken kredi kapatmada ücret alınıyor mu?", {"bilgi_ara"}),
    ("Konut kredisi en fazla kaç ay vadeli olur?", {"bilgi_ara"}),
    ("EFT işlemleri hangi saatlerde anında gerçekleşir?", {"bilgi_ara"}),
    ("1001 numaralı müşterinin bakiyesi nedir?", {"hesap_bilgisi"}),
    ("1001 numaralı müşterinin son işlemleri nelerdir?", {"hesap_bilgisi"}),
    ("200000 TL'yi 36 ayda aylık %2 faizle çeksem taksit ne olur?", {"kredi_taksiti"}),
    ("9999 numaralı müşterinin bakiyesi nedir?", {"hesap_bilgisi"}),
    ("Kredi kartı limit artışı nasıl yapılır, ne kadar sürer?", {"bilgi_ara"}),
    ("1001 numaralı müşterinin bakiyesi nedir ve kart aidatı ne kadar?", {"hesap_bilgisi", "bilgi_ara"}),
    ("75000 TL'yi 18 ayda aylık %2,5 faizle çeksem taksit ne olur, erken kapatma ücreti var mı?", {"kredi_taksiti", "bilgi_ara"}),
    ("1001 numaralı müşterinin bakiyesi nedir, 30000 TL'yi 10 ayda aylık %3 faizle çeksem taksit ne olur?", {"hesap_bilgisi", "kredi_taksiti"}),
    ("Taşıt kredisi vadesi en fazla kaç ay olabilir?", {"bilgi_ara"}),
    ("Bugün İstanbul'da hava nasıl?", set()),
]

dogru = 0
for i, (soru, beklenen) in enumerate(TEST, 1):
    kullanilan = None
    for deneme in range(4):
        try:
            resp = llm.invoke([("system", SYSTEM), ("human", soru)])
            kullanilan = {tc["name"] for tc in resp.tool_calls}
            break
        except Exception as e:
            mesaj = str(e)
            if "PerDay" in mesaj:
                print("GÜNLÜK KOTA DOLU:", mesaj[:200])
                break
            if "RateLimit" in type(e).__name__ and deneme < 3:
                print(f"    dakikalık limit, 65 sn bekleniyor... ({mesaj[:150]})")
                time.sleep(65)
            else:
                print("HATA:", type(e).__name__, mesaj[:200])
                break
    if kullanilan is None:
        print(f"{i:2d}. test durduruldu")
        break
    ok = kullanilan == beklenen
    dogru += ok
    print(f"{i:2d}. {'DOĞRU' if ok else 'YANLIŞ'} | beklenen={sorted(beklenen)} | kullanılan={sorted(kullanilan)}")
    if not ok:
        print(f"    soru: {soru}")
    time.sleep(6)

print(f"\nSonuç: {dogru}/{len(TEST)}")
