import os
import re
import time
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
PEPOGIT_TOKEN  = os.getenv("PEPOGIT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# I feed funzionanti
RSS_SOURCES = {
    "Linux.com News":           "https://www.linux.com/feed/",
    "Planet Ubuntu":            "https://planet.ubuntu.com/rss20.xml",
    "Kernel.org Announcements": "https://www.kernel.org/feeds/kdist.xml",
}

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime

def fetch_feed_xml(url: str, timeout: int = 10) -> Optional[bytes]:
    """Scarica il feed (RSS o Atom) come XML raw."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content

def parse_feed(xml_bytes: bytes) -> List[Article]:
    """Estrae articoli sia da RSS (<item>) che da Atom (<entry>)."""
    root = ET.fromstring(xml_bytes)
    articles: List[Article] = []

    # 1) RSS standard
    for item in root.findall("./channel/item"):
        t = item.findtext("title", default="").strip()
        l = item.findtext("link",  default="").strip()
        d = item.findtext("pubDate", default="").strip()
        try:
            dt = datetime.strptime(d, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            continue
        articles.append(Article(title=t, link=l, pub_date=dt))

    # 2) Atom
    for entry in root.findall("atom:entry", ATOM_NS):
        t = entry.findtext("atom:title",   namespaces=ATOM_NS) or ""
        # cerchiamo il link alternativo
        link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        l = link_el.get("href") if link_el is not None else ""
        d = entry.findtext("atom:updated",   namespaces=ATOM_NS) \
            or entry.findtext("atom:published", namespaces=ATOM_NS) or ""
        try:
            dt = datetime.fromisoformat(d.rstrip("Z"))
        except Exception:
            continue
        articles.append(Article(title=t.strip(), link=l.strip(), pub_date=dt))

    # Ordina per data decrescente
    return sorted(articles, key=lambda a: a.pub_date, reverse=True)

def safe_filename(title: str) -> str:
    """Pulisce il titolo per usarlo come filename."""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    return re.sub(r'\s+', '_', cleaned) + ".md"

def scrape_full_text(url: str) -> str:
    """Con Selenium aggira i cookie banner e restituisce l’HTML."""
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
        return driver.page_source
    finally:
        driver.quit()

def extract_markdown(html: str) -> str:
    """Invoca Gemini via litellm per estrarre i contenuti in Markdown."""
    prompt = (
        "Extract the following information from the HTML and format in Markdown:\n"
        "1. **Title** as H1\n"
        "2. **Main content**\n"
        "3. **Images** as ![alt](url)\n"
        "4. **Links**\n\n" + html
    )
    resp = litellm.completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role":"user","content":prompt}]
    )
    return resp["choices"][0]["message"]["content"]

def publish_gist(content: str, description: str, filename: str):
    """Pubblica un Gist su GitHub."""
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
        print(f"[ERR] Fallita pubblicazione (status {r.status_code}): {r.text}")

def main():
    all_articles: List[Article] = []
    for name, url in RSS_SOURCES.items():
        try:
            xml = fetch_feed_xml(url)
            all_articles.extend(parse_feed(xml))
        except Exception as e:
            print(f"[WARN] Feed '{name}' salto per errore: {e}")

    if not all_articles:
        print("▶️ Nessun articolo valido trovato.")
        return

    # Prendi i 5 più recenti
    top5 = sorted(all_articles, key=lambda a: a.pub_date, reverse=True)[:5]

    for idx, art in enumerate(top5, start=1):
        print(f"[{idx}/5] {art.title} ({art.pub_date.isoformat()})")
        html = scrape_full_text(art.link)
        md   = extract_markdown(html)
        fname = safe_filename(art.title)
        publish_gist(md, art.title, fname)

if __name__ == "__main__":
    main()
