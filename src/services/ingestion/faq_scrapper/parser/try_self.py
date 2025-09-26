import requests
from bs4 import BeautifulSoup

url = 'https://www.amazon.fr/gp/bestsellers/?ref_=nav_cs_bestsellers'
out_path = '/Users/saraevsviatoslav/Documents/ai_instructor/src/services/ingestion/faq_scrapper/parser/imgs'

def scrapper(url: str, out_path: str):
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    image_links = soup.find_all('div', class_='a-section a-spacing-mini _cDEzb_noop_3Xbw5')
    links = []
    for link in image_links:
        img = link.find('img')
        lnk = img['src']
        links.append(lnk)
        name = '/Image'
        num_im = 1
    for link in links:
        im_name = name + str(num_im) + '.jpg'

        response = requests.get(link)
        if response.status_code == 200:
            with open((out_path+im_name), 'wb') as f:
                f.write(response.content)
        else:
            print('Error of request')
        num_im += 1



scrapper(url, out_path)