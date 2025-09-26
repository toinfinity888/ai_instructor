from pathlib import Path
from src.schemas.chunks_befor_embed import ChunksBeforeEmbed
from src.schemas.embedded_chunk import EmbeddedChunk
from src.services.ingestion.embedding.embedder_openai import EmbedderOpenai
from typing import Generator, List
from src.logging.logger import logger
import json
import hashlib
import asyncio
from asyncio import Queue
from tqdm.asyncio import tqdm as tqdm_asyncio
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams
from qdrant_client.http import models as rest_models
from qdrant_client.http.exceptions import ApiException
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
collection_name = "mvp_support"

qdrant_client = QdrantClient(
    url=QDRANT_URL, 
    api_key=QDRANT_API_KEY,
)

try:
    qdrant_client.get_collection(collection_name=collection_name)
except ApiException as e:
    if e.status_code == 404:

        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=3072,      # for text-embedding-3-large
                distance="Cosine"
            )
        )
    else:
        raise


embedder_openai = EmbedderOpenai()
output_path_to_json = Path("/Users/saraevsviatoslav/Documents/ai_instructor/data/embeddings_json/embeddings.json")

def generate_chunk_id() -> str:
    return str(uuid.uuid4())

class Embedder():
    def __init__(self, path: Path):
        self.path = path
                    
    def get_chunks_from_json(self) -> Generator[ChunksBeforeEmbed, None, None]:
        try:
            chunks = []
            for file in self.path.glob('*.json'):
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
                        id = generate_chunk_id()

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

                        yield chunk

        except (FileNotFoundError, IsADirectoryError) as e:
            logger.warning(f'❌ Error while reading JSONs: {e}')
        
    
    async def embedder(self, chunks: List[ChunksBeforeEmbed]) -> List[EmbeddedChunk]:
        embedded_chunks = await embedder_openai.embedder(chunks)
        return embedded_chunks


async def producer(queue: Queue, embedder_instance: Embedder, num_consumers: int) -> List[EmbeddedChunk]:
    for chunk in embedder_instance.get_chunks_from_json():
        await queue.put(chunk)
    for _ in range(num_consumers):
        await queue.put(None)


def to_point(chunk: EmbeddedChunk) -> PointStruct:
    return PointStruct(
        id=chunk.id,
        vector=chunk.embedding,
        payload={
            "section": chunk.section,
            "subsection": chunk.subsection,
            "question": chunk.question,
            "content": chunk.content,
            "url": chunk.url,
            "filename": chunk.filename,
            "page": chunk.page,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
            "file_type": chunk.file_type,
        }
    )


async def consumer(queue: Queue, collection_name: str, pbar):
    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        try:
            embedded = await embedder_openai.embedder([chunk])
            points = [to_point(c) for c in embedded]
            qdrant_client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            logger.error(f"Embedding failed for chunk {chunk.id}: {e}")
        finally:
            queue.task_done()
            pbar.update(1)



async def main():
    path_to_jsons = "/Users/saraevsviatoslav/Documents/ai_instructor/data/raw"
    queue = Queue(maxsize=10)
    embedder_instance = Embedder(Path(path_to_jsons))
    num_consumers = 5

    # Launch producer
    producer_task = asyncio.create_task(producer(queue, embedder_instance, num_consumers))

    # Launch a few cunsumers
    chunks_count = sum(1 for _ in embedder_instance.get_chunks_from_json())
    pbar = tqdm_asyncio(total=chunks_count, desc="Embedding chunks")

    consumer_tasks = [asyncio.create_task(consumer(queue, collection_name, pbar)) for _ in range(num_consumers)]

    await asyncio.gather(producer_task)
    await queue.join()

    for task in consumer_tasks:
        task.cancel()



if __name__ == "__main__":
    asyncio.run(main())


    