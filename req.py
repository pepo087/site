import os
import re
import time                                # <— import time per le pause dopo il click
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import litellm

# Carica le variabili d’ambiente
load_dotenv()
PEPOGIT_TOKEN   = os.getenv("PEPOGIT_TOKEN")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")

# Definisci qui le sorgenti RSS di progetti/doc/guide Linux open-source
RSS_SOURCES = {
    "Linux.com News":           "https://www.linux.com/feed/",
    "DistroWatch News":         "https://distrowatch.com/news/dwd.xml",
    "LWN.net Headlines":        "https://lwn.net/headlines/xml/",
    "Planet Ubuntu":            "https://planet.ubuntu.com/rss20.xml",
    "Kernel.org Announcements": "https://www.kernel.org/feeds/kdist.xml",
}

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime

def fetch_feed(url: str, timeout: int = 10) -> Optional[bytes]:
    """Scarica il contenuto raw dell’RSS feed."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content

def parse_feed(xml_bytes: bytes) -> List[Article]:
    """Estrae tutti gli <item> da un feed RSS, li ordina per data di pubblicazione."""
    root = ET.fromstring(xml_bytes)
    articles = []
    for item in root.findall("./channel/item"):
        title = item.findtext("title", default="").strip()
        link  = item.findtext("link",  default="").strip()
        date  = item.findtext("pubDate", default="").strip()
        try:
            dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            continue
        articles.append(Article(title=title, link=link, pub_date=dt))
    # Ordina in ordine decrescente di data
    return sorted(articles, key=lambda a: a.pub_date, reverse=True)

def scrape_full_text(url: str) -> str:
    """Usa Selenium + BeautifulSoup per aggirare cookie banner e ottenere HTML pulito."""
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service)
    try:
        driver.get(url)
        # Attendi e clicca “Rifiuta tutto” se presente
        try:
            btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Rifiuta tutto']"))
            )
            btn.click()
            time.sleep(3)
        except Exception:
            pass
        html = driver.page_source
    finally:
        driver.quit()
    return html

def extract_markdown(html: str) -> str:
    """Invoca Gemini via litellm per estrarre titolo, contenuti e immagini in Markdown."""
    prompt = (
        "Extract the following information from the HTML page and format in Markdown:\n"
        "1. **Title** as H1\n"
        "2. **Main content**\n"
        "3. **Images** as ![alt](url)\n"
        "4. **Links**\n\n"
        + html
    )
    resp = litellm.completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp["choices"][0]["message"]["content"]

def publish_gist(content: str, description: str, filename: str) -> None:
    """Pubblica un Gist GitHub contenente il Markdown estratto."""
    url = "https://api.github.com/gists"
    hdr = {"Authorization": f"token {PEPOGIT_TOKEN}"}
    data = {
        "description": description,
        "public": True,
        "files": { filename: {"content": content} }
    }
    r = requests.post(url, json=data, headers=hdr)
    if r.status_code == 201:
        print("Gist creato:", r.json()["html_url"])
    else:
        print("Errore Gist:", r.status_code, r.json())

def safe_filename(title: str) -> str:
    """Rimuove caratteri non validi e sostituisce spazi con underscore."""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    return re.sub(r'\s+', '_', cleaned)

def main():
    # 1. Scarica e parsifica tutti i feed
    all_articles: List[Article] = []
    for name, rss in RSS_SOURCES.items():
        try:
            xml = fetch_feed(rss)
            all_articles.extend(parse_feed(xml))
        except Exception as e:
            print(f"Errore fetch/parse per {name}: {e}")
    if not all_articles:
        print("Nessun articolo trovato.")
        return

    # 2. Prendi i 5 articoli più recenti
    latest_five = all_articles[:5]

    # 3. Processa ciascun articolo e pubblica un Gist
    for idx, article in enumerate(latest_five, start=1):
        print(f"[{idx}/5] Processing: {article.title} ({article.pub_date.isoformat()})")
        html = scrape_full_text(article.link)
        md   = extract_markdown(html)
        fname = safe_filename(article.title) + ".md"
        publish_gist(content=md, description=article.title, filename=fname)

if __name__ == "__main__":
    main()
