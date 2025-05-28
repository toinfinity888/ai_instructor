from src.services.ingestion.faq_scrapper.parser.link_parser import get_post_links_from_page
from src.services.ingestion.faq_scrapper.parser.post_parser import parser_post_page
from src.services.ingestion.faq_scrapper.parser.section_link_parser import get_section_links_from_page
from src.services.ingestion.faq_scrapper.utils.save import save_to_json 
from src.services.ingestion.faq_scrapper.parser.pdf_download import get_pdf_url_from_page, download_pdf
from src.services.ingestion.faq_scrapper.parser.docs_link_parcer import get_docs_link
from src.logging.logger import logger
from tqdm import tqdm
import time
from random import uniform
import typer

app = typer.Typer()
@app.command(help='Scrapper FAQ')
def run_scraper_faq():
    base_url = 'https://community.arlo.com/t5/Services/ct-p/en-services'
    all_data = []
    logger.info('Get section links...')
    section_urls = get_section_links_from_page(base_url)
    for url in tqdm(section_urls, desc='Sections'):
        logger.info("Get all post's links...")
        post_links = get_post_links_from_page(url)
        time.sleep(uniform(1, 2))
        logger.info(f'Number of posts found: {len(post_links)}')

        logger.info('Parsing of posts...')
        for link in tqdm(post_links, desc=f"Parsing posts from {url}"):
            data = parser_post_page(link)
            section_data = {
                'section_url': url,
                'posts': data
            }
            all_data.append(section_data)
            time.sleep(uniform(1, 3))
    save_to_json(all_data, '/Users/saraevsviatoslav/Documents/ai_instructor/src/services/ingestion/faq_scrapper/data/posts.json')

@app.command(help='PDF downloader')
def run_pdf_download():
    base_url = 'https://www.arlo.com/en-us/support/docs'
    logger.info('Get all links...')
    all_items_link = get_docs_link(base_url)
    if not all_items_link:
        logger.info('Links of items not found')
        raise ValueError
    
    for url in tqdm(all_items_link, desc='PDF downloading...'):
        pdf_link = get_pdf_url_from_page(url)
        if not pdf_link:
            logger.warning(f'No PDF found on page: {url}')
            continue
        filename = pdf_link.split('/')[-1].split('?')[0]
        pdfs_path = '/Users/saraevsviatoslav/Documents/ai_instructor/src/services/ingestion/faq_scrapper/data/pdfs'
        download_pdf(pdf_link, f'{pdfs_path}/{filename}')
        logger.info(f"Downloaed: {filename}")
        time.sleep(uniform(1, 3))
