import fitz
from pathlib import Path
from src.logging.logger import logger
from src.path_config import SCRAPPED_PDF, SCRAPPED_DATA
from src.schemas.chunks_befor_embed import ChunksBeforeEmbed
from typing import List
import json
from collections import Counter

def define_zize_of_text_in_paragraph(file) -> int:
    doc = fitz.open(file)
    all_sizes = []
    for page_index, page in enumerate(doc):
        blocks = page.get_text('dict')['blocks']

        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        size = span['size']

                        all_sizes.append(size)

    counter = Counter(all_sizes)
    most_common_num, _ = counter.most_common(1)[0]
    return most_common_num
    

def extract_top_header(page, size_of_the_main_text):
    blocks = page.get_text('dict')['blocks']
    top_text = ''
    min_y = float('inf')
    for block in blocks:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                y = span['bbox'][1]
                size = span['size']
                text = span['text'].strip()
                if y < min_y and len(text) > 2 and size > size_of_the_main_text:
                    min_y = y
                    top_text = text
    return top_text

def is_toc_page(page):
    blocks = page.get_text('dict')['blocks']
    count_with_number = 0
    total_lines = 0

    for block in blocks:
        if block['type'] == 0:
            for line in block.get('lines', []):
                line_text = ''.join(span['text'] for span in line['spans']).strip()
                if len(line_text) < 4:
                    continue

                total_lines +=1
                if line_text[-1].isdigit():
                    count_with_number +=1

    if total_lines == 0:
        return False
    
    return count_with_number / total_lines > 0.7

def get_chunks_from_pdf(pdf_folder_path: Path) -> List[ChunksBeforeEmbed]:
    chunks = []

    try:
        for file in pdf_folder_path.glob('*.pdf'):
            size_of_the_main_text = define_zize_of_text_in_paragraph(file)

            doc = fitz.open(file)
            name = file.name
            url = str(file)
            file_type = 'PDF'
            current_section = 'Untitled'
            current_chunk = None
            

            for page_num in range(1, doc.page_count):
                page = doc.load_page(page_num)

                if is_toc_page(page):
                    continue

                current_section = extract_top_header(page, size_of_the_main_text)
                current_section = current_section.strip().replace('\t', '')

                blocks = page.get_text('dict')['blocks']
                page_height = page.rect.height

                title_lines = []
                for block in blocks:
                    for line in block.get('lines', []):
                        spans_filtered = [
                            span for span in line.get('spans', [])
                            if 50 < span['bbox'][1] < (page_height - 50)
                        ]
                        if not spans_filtered:
                            continue

                        text_line = " ".join(span['text'] for span in spans_filtered).strip()
                        text_line.replace('\t', '')
                        is_title = any(span['size'] > size_of_the_main_text for span in spans_filtered)
                        

                        if is_title:
                            title_lines.append(text_line)
                            continue

                        if title_lines:
                            full_title = ' '.join(title_lines).strip()
                            full_title = full_title.replace('\t', '')
                            if current_chunk and current_chunk.subsection and current_chunk.content.strip():
                                current_chunk.update_content_hash()
                                chunks.append(current_chunk)
                            

                            # Создаём новый чанк
                            current_chunk = ChunksBeforeEmbed(
                                id=f"{current_section}_{full_title}",
                                section=current_section,
                                subsection=full_title,
                                content='',
                                url=url,
                                filename=name,
                                page=page_num + 1,
                                file_type=file_type,
                            
                            )
                            title_lines.clear()

                        if not current_chunk:
                            logger.warning("⚠️ current_chunk is None while processing text_line")
                            continue
                        current_chunk.content += text_line + ' '

    except Exception as e:
        logger.info(f'Error: {e}')

    return chunks

# Save chunks to JSON to verify if data in chunks is correct
def save_chunks_to_json(chunks: List[ChunksBeforeEmbed], output_path: Path):
     with open(output_path, 'w', encoding = 'utf-8') as f:
          json.dump([chunk.model_dump() for chunk in chunks], f, ensure_ascii=False, indent=2, default=str)


def extract_and_save_chunks():
    #path: Path = SCRAPPED_PDF
    path = Path('/Users/saraevsviatoslav/Documents/ai_instructor/src/services/ingestion/faq_scrapper/data/pdf_for_knoledge_graph')
    chunks = get_chunks_from_pdf(path)
    output_path_json = SCRAPPED_DATA / 'pdf_chunks_bike.json'
    save_chunks_to_json(chunks, output_path_json)
    print(f"✅ Extracted {len(chunks)} chunks and saved to {output_path_json}")

# Cleaning JSON =================================================================

def json_cleaning(path: Path):
    for file in path.glob('*.json'):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cleaning_data = []
        for entry in data:
            if 'posts' in entry and 'answer' in entry['posts'] and not entry['posts']['answer']:
                continue

            if 'content' in entry:
                entry['content'] = entry['content'].replace('\t', '')

            cleaning_data.append(entry)

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(cleaning_data, f, ensure_ascii=False, indent=2)

def json_cleaning_run():
    path = SCRAPPED_DATA
    json_cleaning(path)



def size_test():
    path = Path('/Users/saraevsviatoslav/Documents/ai_instructor/src/services/ingestion/faq_scrapper/data/pdf_for_knoledge_graph')
    for file in path.glob('*.pdf'):
        define_zize_of_text_in_paragraph(file)
        break
           