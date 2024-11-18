import time
import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import re
import litellm  # Importa la libreria litellm
from datetime import datetime

# Carica le variabili d'ambiente dal file .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Aggiungi la chiave API per Gemini

# Configura il servizio per ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Funzione per pubblicare un Gist su GitHub
def publish_gist(content, description, filename="offerta_mini_pc.md", public=True):
    """Pubblica il contenuto come Gist su GitHub."""
    url = "https://api.github.com/gists"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "description": description,
        "public": public,
        "files": {
            filename: {
                "content": content
            }
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("Gist pubblicato con successo:", response.json()["html_url"])
    else:
        print("Errore nella pubblicazione del Gist:", response.json())

# Funzione per sostituire il tag di affiliazione Amazon con quello corretto
def update_amazon_affiliate_links(content, affiliate_tag="pepo087site-21"):
    # Trova i link Amazon e sostituisci i tag di affiliazione con quello corretto
    content = re.sub(
        r'(https://www\.amazon\.[\w\.\/-]+?)(\?.*?tag=[^&\s]+|)(?=&|\s|$)',
        rf'\1?tag={affiliate_tag}',
        content
    )
    return content

try:
    # Link RSS feed di Google News
    rss_url = "https://news.google.com/rss/search?q=%7BMINI+PC+OFFERTA+AMAZON%7D&hl=it&gl=IT&ceid=IT:it"
   
    # Scarica l'RSS feed
    response = requests.get(rss_url)
    xml_content = response.content

    # Parsing dell'XML per estrarre il link con la data di pubblicazione più recente
    root = ET.fromstring(xml_content)
    latest_link = None
    latest_date = None

    for item in root.findall("./channel/item"):
        # Estrai la data di pubblicazione
        pub_date = item.find("pubDate").text
        link = item.find("link").text

        # Converte la data di pubblicazione in un oggetto datetime
        try:
            pub_date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            print("Formato data non valido per:", pub_date)
            continue

        # Aggiorna il link se è la data più recente
        if latest_date is None or pub_date_obj > latest_date:
            latest_date = pub_date_obj
            latest_link = link

    print("Ultimo link trovato:", latest_link)

    if latest_link:
        # Apri l'ultimo link
        driver.get(latest_link)

        # Gestione del consenso
        try:
            reject_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Rifiuta tutto']"))
            )
            reject_button.click()
            time.sleep(5)
            WebDriverWait(driver, 20).until(EC.url_changes(latest_link))

            final_url = driver.current_url
            print("Final URL:", final_url)
        except Exception as e:
            print("Errore nella gestione del consenso:", e)

        # Scarica il contenuto della pagina
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Estrai il contenuto della pagina come stringa
        webpage_content = str(soup)

        # Prompt per estrarre informazioni in Markdown
        prompt = (
            "Extract the following information from the article and format it in Markdown:\n"
            "1. **Title**: Extract the title of the article and format it as an H1 header (e.g., # Article Title).\n"
            "2. **Content**: Include all main content from the article in Markdown format.\n"
            "3. **Images**: Extract links to images and format each image like this: ![Alt text](URL).\n"
            "4. **Links**: If available, clearly include any relevant links.\n"
            "5. **Amazon Affiliate Links**: Replace any Amazon links by adding the correct affiliate tag '?tag=pepo087site-21' to the URL.\n"
            "\nHere is the page content:\n\n" + webpage_content
        )

        # Crea il payload per la richiesta a Gemini usando litellm
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Esegui la chiamata API al modello Gemini utilizzando litellm
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=messages
        )

        # Estrai il contenuto Markdown dalla risposta
        markdown_content = response["choices"][0]["message"]["content"]
        # Visualizza il contenuto Markdown
        print(markdown_content)

        # Aggiorna i link Amazon con il tag corretto
        markdown_content = update_amazon_affiliate_links(markdown_content)

        # Estrai il titolo dall'intestazione H1
        title = markdown_content.split("\n")[0][2:]  # Estrae il titolo dall'intestazione H1
        # Rimuovi caratteri speciali e sostituisci gli spazi con underscore
        filename = re.sub(r'[<>:"/\\|?*]', '', title)  # Rimuovi caratteri non validi
        filename = re.sub(r'\s+', '_', filename) + '.md'  # Sostituisci spazi con underscore e aggiungi l'estensione .md

        # Pubblica il contenuto in Markdown su GitHub come Gist
        publish_gist(markdown_content, description=title, filename=filename)

finally:
    driver.quit()
