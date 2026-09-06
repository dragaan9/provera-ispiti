from datetime import datetime
import os
import re
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL_VESTI = "https://ees.etf.bg.ac.rs/vesti.php?s=1"
GRANICNI_DATUM = datetime(2026, 9, 4)


def posalji_telegram_poruku(poruka):
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("Greška: TELEGRAM_BOT_TOKEN ili TELEGRAM_CHAT_ID nisu podešeni.")
    return False
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": poruka}
  try:
    res = requests.post(url, json=payload)
    return res.status_code == 200
  except Exception as e:
    print(f"Greška pri slanju Telegram poruke: {e}")
    return False


def parsiraj_datum(tekst_datuma):
  try:
    return datetime.strptime(tekst_datuma.strip(), "%d.%m.%Y")
  except ValueError:
    return None


def proveri():
  session = requests.Session()
  session.headers.update({
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  })

  try:
    print(f"Proveravam stranicu sa vestima: {URL_VESTI}")
    res = session.get(URL_VESTI, timeout=10)
    res.encoding = res.apparent_encoding or "utf-8"

    if res.status_code != 200:
      print(f"Status odgovora sa sajta: {res.status_code}")
      return

    soup = BeautifulSoup(res.text, "html.parser")
    tekst_stranice = soup.get_text(separator="\n")

    # 1. Ekstrakcija poslednje vesti za GitHub Workflow
    match = re.search(r"(\d{2}\.\d{2}\.\d{4})", tekst_stranice)
    if match:
      poslednji_datum = match.group(1)
      tekst_pre = tekst_stranice[: match.start()]
      linije = [
          line.strip() for line in tekst_pre.split("\n") if line.strip()
      ]
      poslednji_predmet = linije[-1] if linije else "Nepoznat predmet"

      print("=" * 40)
      print(f"POSLEDNJA VEST NA SAJTU: {poslednji_predmet}")
      print(f"DATUM OBJAVE: {poslednji_datum}")
      print("=" * 40)

      if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
          f.write(f"predmet={poslednji_predmet}\n")
          f.write(f"datum={poslednji_datum}\n")

    # 2. Provera da li postoji vest za Mehaniku posle 04.09.2026.
    blokovi = re.split(r"(\d{2}\.\d{2}\.\d{4})", tekst_stranice)
    pronadjena_mehanika = False

    for i in range(1, len(blokovi) - 1, 2):
      datum_str = blokovi[i]
      sadrzaj_vesti = (
          blokovi[i + 1].lower() + (blokovi[i - 1].lower() if i > 1 else "")
      )
      datum_obj = parsiraj_datum(datum_str)

      if datum_obj and datum_obj > GRANICNI_DATUM:
        if "механика" in sadrzaj_vesti or "mehanika" in sadrzaj_vesti:
          poruka = (
              f"🎉 Objavljena je NOVA vest za Mehaniku sa datumom"
              f" {datum_str}!\n\nPogledaj na linku: {URL_VESTI}"
          )
          print(
              f"Pronađena nova vest za Mehaniku ({datum_str})! Šaljem"
              " obaveštenje na Telegram..."
          )
          posalji_telegram_poruku(poruka)
          pronadjena_mehanika = True
          break

    if not pronadjena_mehanika:
      print("Nema novih vesti za Mehaniku objavljenih posle 04.09.2026.")

  except Exception as e:
    print(f"Došlo je do greške tokom provere: {e}")


if __name__ == "__main__":
  proveri()
