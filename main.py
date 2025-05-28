from src.services.ingestion.faq_scrapper.pipeline.run import run_scraper_faq, run_pdf_download
from src.services.ingestion.processing.preprocess import extract_and_save_chunks

def main():
    #run_scraper()
    #run_pdf_download()
    extract_and_save_chunks()
if __name__ == '__main__':
    main()

