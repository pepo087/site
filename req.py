import os
import re
import time
import tempfile
import shutil
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
    pub_date: datetime  # sempre UTC naive


def normalize_dt(dt: datetime) -> datetime:
    """Converti in UTC naive ogni datetime offset-aware."""
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
            try:
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            except Exception:
                continue
        dt = normalize_dt(dt)
        articles.append(Article(title=title.strip(), link=link.strip(), pub_date=dt))

    # Ordina per data decrescente
    return sorted(articles, key=lambda a: a.pub_date, reverse=True)


def safe_filename(title: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    return re.sub(r'\s+', '_', cleaned) + ".md"


def has_enough_text(html: str, min_chars: int = 300) -> bool:
    """
    Verifica che l'HTML contenga almeno min_chars caratteri di testo visibile,
    escludendo link e URL.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Rimuovi tag non testuali
    for tag in soup(["script", "style", "noscript", "header", "footer", "aside"]):
        tag.extract()
    # Rimuovi link <a>
    for a in soup.find_all('a'):
        a.extract()
    text = soup.get_text(separator=" ", strip=True)
    # Rimuovi URL espliciti da testo
    text = re.sub(r'https?://\S+', '', text)
    return len(text) >= min_chars


def scrape_full_text(url: str) -> str:
    user_data_dir = tempfile.mkdtemp(prefix="chrome-profile-")
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_opts.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=chrome_opts)

    try:
        driver.get(url)
        for text in ("Rifiuta tutto", "Accetta tutti", "Reject all", "Accept all"):
            try:
                btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{text}')]))")
                )
                btn.click()
                time.sleep(2)
                break
            except Exception:
                pass
        return driver.page_source

    finally:
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)


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
        messages=[{"role":"user","content":prompt}]
    )
    return resp["choices"][0]["message"]["content"]


def publish_gist(content: str, description: str, filename: str):
    url     = "https://api.github.com/gists"
    headers = {"Authorization": f"token {PEPOGIT_TOKEN}"}
    payload = {
        "description": description,
        "public": True,
        "files": {filename: {"content": content}}
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 201:
        print(f"[OK] Gist: {r.json()['html_url']}")
    else:
        print(f"[ERR] Gist fallito ({r.status_code}): {r.text}")


def main():
    all_articles: List[Article] = []
    for name, url in RSS_SOURCES.items():
        try:
            xml = fetch_feed_xml(url)
            all_articles.extend(parse_feed(xml))
        except Exception:
            pass

    candidates = all_articles[:10]
    published = 0

    for art in candidates:
        if published >= 5:
            break

        html = scrape_full_text(art.link)
        if not has_enough_text(html, min_chars=300):
            continue

        md    = extract_markdown(html)
        fname = safe_filename(art.title)
        publish_gist(md, art.title, fname)
        published += 1

if __name__ == "__main__":
    main()
