from openai import AsyncOpenAI
from src.path_config import SCRAPPED_DATA
from src.config import OPENAI_API_KEY
from src.logging.logger import logger
from pathlib import Path
from src.schemas.chunks_befor_embed import ChunksBeforeEmbed
from src.schemas.embedded_chunk import EmbeddedChunk
from typing import List
from tqdm.asyncio import tqdm as tqdm_asyncio
import asyncio
import hashlib

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)

class EmbedderOpenai():
    def convert_to_embed(self, chunk: ChunksBeforeEmbed, embedding: list[float]) -> EmbeddedChunk:
        return EmbeddedChunk(
            id=chunk.id,
            section=chunk.section,
            subsection=chunk.subsection,
            question=chunk.question,
            content=chunk.content or "",
            embedding=embedding,
            url=chunk.url,
            filename=chunk.filename,
            page=chunk.page,
            created_at=chunk.created_at,
            content_hash=chunk.content_hash or hashlib.sha256((chunk.content or "").encode()).hexdigest(),
            file_type=chunk.file_type,
        )
    
    async def embed_one_chunk(self, chunk: ChunksBeforeEmbed) -> EmbeddedChunk:
        try:
            response = await client.embeddings.create(
                input=chunk.content,
                model='text-embedding-3-large'
            )
            embedding = response.data[0].embedding

            return self.convert_to_embed(chunk, embedding)
        except Exception as e:
            logger.error(f'Embedding failed for chunk: {chunk.id}: {e}')
            raise
    
    async def embedder(self, chunks: List[ChunksBeforeEmbed]) -> List[EmbeddedChunk]:
        embed_tasks = [asyncio.create_task(self.embed_one_chunk(chunk)) for chunk in chunks]
        all_embed_chunks = []

        for future in asyncio.as_completed(embed_tasks):
            try:
                embed_chunk = await future
                all_embed_chunks.append(embed_chunk)
            except Exception:
                continue

        return all_embed_chunks