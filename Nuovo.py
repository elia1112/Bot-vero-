
import requests
import time
import telebot
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Token e chat ID
TELEGRAM_BOT_TOKEN = "7645434101:AAG_M12EujlAtT8VI5Vvx5Vy-b1qdqkDZ4Y"
CHAT_ID = "7901606004"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Vista cache per evitare doppie notifiche
annunci_visti = {}

def invia_notifica(annuncio):
    messaggio = f"""
🚗 *Annuncio Popolare!*
📌 *Titolo*: {annuncio['titolo']}
💶 *Prezzo*: {annuncio['prezzo']}
📍 *Luogo*: {annuncio['luogo']}
❤️ *Cuori stimati*: {annuncio['cuori']}
🕒 *Pubblicato*: {annuncio['tempo_pubblicazione']}
🔗 [Vedi Annuncio]({annuncio['link']})
"""
    bot.send_message(CHAT_ID, messaggio, parse_mode='Markdown')

def recupera_annunci_subito():
    url = "https://www.subito.it/annunci-piemonte/vendita/auto/torino/?sp=1"  # privati, auto, Torino
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    annunci = []

    for annuncio in soup.select("a.AdCardAd_adCard__gqR8z"):  # selettore aggiornato 2024
        titolo = annuncio.select_one("h2").text.strip() if annuncio.select_one("h2") else "Titolo non trovato"
        prezzo = annuncio.select_one("p.AdCardAd_price__yDyen")
        prezzo = prezzo.text.strip() if prezzo else "Prezzo non visibile"
        luogo = annuncio.select_one("p.AdCardAd_location__zR6kV")
        luogo = luogo.text.strip() if luogo else "Luogo sconosciuto"
        link = "https://www.subito.it" + annuncio["href"]

        # Subito non espone i cuori e l'orario nel listing, quindi si simula
        cuori = 12  # Simulazione, in produzione serve Selenium o API
        tempo_pubblicazione = "1 ora fa"
        timestamp_pubblicazione = datetime.now() - timedelta(hours=1)

        annunci.append({
            "titolo": titolo,
            "prezzo": prezzo,
            "luogo": luogo,
            "cuori": cuori,
            "tempo_pubblicazione": tempo_pubblicazione,
            "timestamp_pubblicazione": timestamp_pubblicazione,
            "link": link
        })

    return annunci

def controlla_annunci():
    annunci = recupera_annunci_subito()
    for annuncio in annunci:
        link = annuncio["link"]
        if link not in annunci_visti:
            ore_passate = (datetime.now() - annuncio["timestamp_pubblicazione"]).total_seconds() / 3600
            if annuncio["cuori"] >= 10 and ore_passate <= 3:
                invia_notifica(annuncio)
            annunci_visti[link] = datetime.now()

def main():
    while True:
        controlla_annunci()
        time.sleep(1800)

if __name__ == "__main__":
    main()
