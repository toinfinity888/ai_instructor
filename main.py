from src.services.ingestion.faq_scrapper.pipeline.run import run_scraper_faq, run_pdf_download
from src.services.ingestion.processing.preprocess import extract_and_save_chunks
from src.services.ingestion.processing.preprocess import json_cleaning_run

def main():
    #run_scraper()
    #run_pdf_download()
    #extract_and_save_chunks()
    json_cleaning_run()
if __name__ == '__main__':
    main()

