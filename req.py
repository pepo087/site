import os
import re
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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

# Feed RSS/Atom da cui attingere
RSS_SOURCES = {
    "Linux.com News":           "https://www.linux.com/feed/",
    "Planet Ubuntu":            "https://planet.ubuntu.com/rss20.xml",
    "Kernel.org Announcements": "https://www.kernel.org/feeds/kdist.xml",
}

# Namespace per Atom
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime  # sempre naive UTC

def normalize_dt(dt: datetime) -> datetime:
    """Se dt ha tzinfo, portalo a UTC e rendilo naive."""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def fetch_feed_xml(url: str, timeout: int = 10) -> Optional[bytes]:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content

def parse_feed(xml_bytes: bytes) -> List[Article]:
    root = ET.fromstring(xml_bytes)
    articles: List[Article] = []

    # RSS (<item>)
    for item in root.findall("./channel/item"):
        title = item.findtext("title", default="").strip()
        link  = item.findtext("link",  default="").strip()
        date  = item.findtext("pubDate", default="").strip()
        try:
            dt = parsedate_to_datetime(date)
            dt = normalize_dt(dt)
        except Exception:
            print(f"[WARN] Data RSS non parsabile: {date}")
            continue
        articles.append(Article(title=title, link=link, pub_date=dt))

    # Atom (<entry>)
    for entry in root.findall("atom:entry", ATOM_NS):
        title   = entry.findtext("atom:title", namespaces=ATOM_NS) or ""
        link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS)
        link    = link_el.get("href") if link_el is not None else ""
        date    = entry.findtext("atom:updated",   namespaces=ATOM_NS) \
               or entry.findtext("atom:published", namespaces=ATOM_NS) or ""
        try:
            dt = parsedate_to_datetime(date)
        except Exception:
            # fallback ISO
            try:
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            except Exception:
                print(f"[WARN] Data Atom non parsabile: {date}")
                continue
        dt = normalize_dt(dt)
        articles.append(Article(title=title.strip(), link=link.strip(), pub_date=dt))

    # Ordina in ordine decrescente di data
    return sorted(articles, key=lambda a: a.pub_date, reverse=True)

def safe_filename(title: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    return re.sub(r'\s+', '_', cleaned) + ".md"

def scrape_full_text(url: str) -> str:
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
    prompt = (
        "Extract the following information from the HTML and format in Markdown:\n"
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

def publish_gist(content: str, description: str, filename: str):
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
        print(f"[ERR] Fallita pubblicazione ({r.status_code}): {r.text}")

def main():
    all_articles: List[Article] = []
    for name, url in RSS_SOURCES.items():
        try:
            xml = fetch_feed_xml(url)
            all_articles.extend(parse_feed(xml))
        except Exception as e:
            print(f"[WARN] Feed '{name}' scartato per errore: {e}")

    if not all_articles:
        print("▶️ Nessun articolo valido trovato.")
        return

    top5 = all_articles[:5]  # già ordinati in parse_feed

    for idx, art in enumerate(top5, start=1):
        print(f"[{idx}/5] {art.title} ({art.pub_date.isoformat()})")
        html  = scrape_full_text(art.link)
        md    = extract_markdown(html)
        fname = safe_filename(art.title)
        publish_gist(md, art.title, fname)

if __name__ == "__main__":
    main()
