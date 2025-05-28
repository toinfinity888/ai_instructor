import requests
from bs4 import BeautifulSoup
from typing import List
from src.logging.logger import logger

def get_max_page_num(soup):
    page_links = soup.find_all('a', class_='lia-link-navigation')
    page_numbers = []

    for link in page_links:
        if link.text.strip().isdigit():
            page_numbers.append(int(link.text.strip()))
    return max(page_numbers) if page_numbers else 1

def get_post_links_from_page(url: str) -> List[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    all_links = set()

    logger.info('Get last page number...')
    last_page = get_max_page_num(soup)
    logger.info(f'Total pages: {last_page}')

    try:
        for page_num in range(1, last_page + 1):
            if page_num == 1:
                page_soup = soup
            else:
                page_url = f'{url}/page/{page_num}'
                response = requests.get(page_url)
                page_soup = BeautifulSoup(response.text, 'lxml')
                
            for link in page_soup.find_all('a', class_='page-link'):
                href = link.get('href')
                if href and '/td-p/' in href:
                    full_url = 'https://community.arlo.com' + href
                    all_links.add(full_url)

    except Exception as e:
        logger.info(f'Error: {e}')

    return list(all_links)
