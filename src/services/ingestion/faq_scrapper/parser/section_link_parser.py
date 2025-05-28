import requests
from bs4 import BeautifulSoup
from typing import Set

def get_section_links_from_page(url: str) -> Set[str]: 
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    links = set()
    for link in soup.find_all('a', class_='lia-link-navigation'):
        href = link.get('href')
        if href and '/bd-p/' in href:
            full_url = 'https://community.arlo.com' + href
            links.add(full_url)
    return links