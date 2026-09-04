import os
import time
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL_1 = "https://oet.etf.bg.ac.rs/"
URL_2 = "https://oet.etf.bg.ac.rs/OET-preliminarne_ocene.htm"
URL_3 = "https://oet.etf.bg.ac.rs/19E071OE2-2.html"


def posalji_telegram_poruku(poruka):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": poruka}
  try:
    res = requests.post(url, json=payload)
    return res.status_code == 200
  except Exception as e:
    print(f"Greška pri slanju poruke: {e}")
    return False


def proveri():
  session = requests.Session()
  session.headers.update({
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  })

  try:
    session.get(URL_1, timeout=10)
    time.sleep(2)

    session.get(URL_2, timeout=10)
    time.sleep(2)

    res = session.get(URL_3, timeout=10)
    if res.status_code == 200:
      sadrzaj = res.text.lower()
      if "not found" not in sadrzaj and "404" not in sadrzaj:
        posalji_telegram_poruku(
            f"🎉 Rezultati iz OE2 su objavljeni!\n{URL_3}"
        )
        print("Rezultati pronađeni i obaveštenje je poslato!")
      else:
        print("Stranica još uvek vraća Not Found.")
    else:
      print(f"Status odgovora: {res.status_code}")
  except Exception as e:
    print(f"Došlo je do greške: {e}")


if __name__ == "__main__":
  proveri()
