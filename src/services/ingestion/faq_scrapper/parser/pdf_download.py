import requests
from bs4 import BeautifulSoup
from src.logging.logger import logger

def get_pdf_url_from_page(page_url: str) -> str:
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    section = soup.find('div', id='Usermanual')
    if not section:
        return None

    for item in section.find_all('div', class_='pdf-item'):
        img = item.find('img')
        link = item.find('a', href=True)

        if img and 'usa.png' or 'uk.png' in img['src'] and link:
            return link['href']
    return None
        

def download_pdf(pdf_url: str, filename: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.arlo.com/en-us/support/docs"
    }

    response = requests.get(pdf_url, headers=headers)

    if response.status_code != 200:
        logger.warning(f"Failed to download: {response.status_code} - {pdf_url}")
        return

    if 'application/pdf' not in response.headers.get('Content-Type', ''):
        logger.warning(f"Wrong content type for {pdf_url}")
        return

    if not response.content.startswith(b'%PDF'):
        logger.warning(f"Downloaded file is not a valid PDF: {pdf_url}")
        return

    with open(filename, 'wb') as f:
        f.write(response.content)
    logger.info(f"Downloaded: {filename}")
