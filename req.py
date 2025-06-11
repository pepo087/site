import os
import re
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List

import requests
import feedparser
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import litellm

# Caricamento variabili d’ambiente
load_dotenv()
PEPOGIT_TOKEN  = os.getenv("PEPOGIT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lista feed: rimuovi quelli non funzionanti o sostituiscili con alternative valide
RSS_SOURCES = {
    "Linux.com News":           "https://www.linux.com/feed/",
    "Planet Ubuntu":            "https://planet.ubuntu.com/rss20.xml",
    "Kernel.org Announcements": "https://www.kernel.org/feeds/kdist.xml",
    # se vuoi aggiungerne altri, verifica prima che rispondano 200 OK
}

@dataclass
class Article:
    title: str
    link: str
    published: datetime

def fetch_articles_from_feed(name: str, url: str) -> List[Article]:
    """Scarica e parse di un feed; ritorna lista di Article o vuoto se errore."""
    try:
        # Controllo preliminare HTTP per escludere i 403/404
        resp = requests.head(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARN] Feed '{name}' non raggiungibile ({e}); skip.")
        return []

    parsed = feedparser.parse(url)
    articles = []
    for entry in parsed.entries:
        # Alcuni feed usano 'published', altri 'updated'
        date_str = getattr(entry, "published", getattr(entry, "updated", None))
        try:
            pub_dt = datetime(*entry.published_parsed[:6])
        except Exception:
            continue
        articles.append(Article(
            title     = entry.title,
            link      = entry.link,
            published = pub_dt
        ))
    return articles

def safe_filename(title: str) -> str:
    """Pulisce il titolo per usarlo come nome file."""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    return re.sub(r'\s+', '_', cleaned) + ".md"

def scrape_full_text(url: str) -> str:
    """Con Selenium aggira i cookie e restituisce l’HTML completo."""
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service)
    try:
        driver.get(url)
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Rifiuta tutto']"))
            )
            btn.click()
            time.sleep(2)
        except Exception:
            pass
        html = driver.page_source
    finally:
        driver.quit()
    return html

def extract_markdown(html: str) -> str:
    """Invoca Gemini via litellm per estrarre i contenuti in Markdown."""
    prompt = (
        "Extract the following information and format in Markdown:\n"
        "1. **Title** as H1\n"
        "2. **Main content**\n"
        "3. **Images** as ![alt](url)\n"
        "4. **Links**\n\n"
        + html
    )
    resp = litellm.completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role":"user","content":prompt}]
    )
    return resp["choices"][0]["message"]["content"]

def publish_gist(content: str, description: str, filename: str):
    """Pubblica un Gist GitHub."""
    url = "https://api.github.com/gists"
    headers = {"Authorization": f"token {PEPOGIT_TOKEN}"}
    payload = {
        "description": description,
        "public": True,
        "files": {filename: {"content": content}}
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 201:
        print(f"[OK] Gist pubblicato: {r.json()['html_url']}")
    else:
        print(f"[ERR] Gist fallito ({r.status_code}): {r.text}")

def main():
    # 1. Raccogli da tutti i feed
    all_articles: List[Article] = []
    for name, url in RSS_SOURCES.items():
        arts = fetch_articles_from_feed(name, url)
        all_articles.extend(arts)

    if not all_articles:
        print("Nessun articolo valido trovato; termina.")
        return

    # 2. Ordina e prendi i primi 5
    sorted_articles = sorted(all_articles, key=lambda a: a.published, reverse=True)
    top5 = sorted_articles[:5]

    # 3. Per ciascuno: scrape → AI → Gist
    for i, art in enumerate(top5, start=1):
        print(f"[{i}/5] {art.title} ({art.published.isoformat()})")
        html = scrape_full_text(art.link)
        md   = extract_markdown(html)
        fname = safe_filename(art.title)
        publish_gist(md, art.title, fname)

if __name__ == "__main__":
    main()
