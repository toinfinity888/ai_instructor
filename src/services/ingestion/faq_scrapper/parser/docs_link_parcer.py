from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from time import time
from typing import List
from src.logging.logger import logger

def get_docs_link(url: str) -> List[str]:
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
    response = requests.get(url, headers=headers)
    logger.info(response.status_code)
    soup = BeautifulSoup(response.text, 'lxml')

    links = set()
    ul = soup.find('ul', class_='panel-list')
    if not ul:
        logger.info('No panel-list found')
        return []
    
    for li in ul.find_all('li'):
        link = li.get('id')
        logger.info(f"{link}")
        if link and link.startswith('http'):
            links.add(link)

    return list(links)