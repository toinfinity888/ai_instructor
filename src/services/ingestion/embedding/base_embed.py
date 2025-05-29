from abc import ABC, abstractmethod
from pathlib import Path
from src.schemas.chunks_befor_embed import ChunksBeforeEmbed
from src.schemas.embedded_chunk import EmbeddedChunk
from typing import List
from src.logging.logger import logger
import json
import hashlib

def generate_chunk_id(title_from_json: str) -> str:
    return hashlib.sha256(title_from_json.encode('utf-8')).hexdigest()

class BaseEmbedder(ABC):
    def get_chunks_from_json(self, path: Path) -> List[ChunksBeforeEmbed]:
        try:
            chunks = []
            for file in path.glob('*.json'):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for entry in data:
                    if entry.get('id') and entry.get('content'):
                        chunk = ChunksBeforeEmbed(**entry) # If there are ID is mean that entry in ChunksBeforeEmbed structure and we can save direct
                        chunks.append(chunk)
                        continue
                    
                    # If structure of FAQ
                    if 'posts' in entry:
                        section = entry['posts'].get('title', 'Unknown')
                        question = entry['posts'].get('question', '')
                        content = '\n'.join(entry['posts'].get('answer', []))
                        url = entry.get('section_url', '')
                        id = generate_chunk_id(section + question + content)

                        chunk = ChunksBeforeEmbed(
                            id=id,
                            section=section,
                            subsection=question,
                            content=content,
                            url=url,
                            filename=None,
                            page=None,
                            file_type='Forum',
                        )
                        chunks.append(chunk)

        except (FileNotFoundError, IsADirectoryError) as e:
            logger.warning(f'❌ Error while reading JSONs: {e}')
        
        return chunks

    
    @abstractmethod
    def embedder(self, chunks: List[ChunksBeforeEmbed]) -> List[EmbeddedChunk]:
        ...