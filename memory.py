from mem.vectordb import search_memories, insert_memories, EmbeddedMemory, client
from mem.generate_embeddings import generate_embeddings
from datetime import datetime

class MemoryStore:
    def __init__(self):
        self.client = client 

    async def add(self, text: str, user_id: int):
        embeddings = await generate_embeddings([text])
        memory = EmbeddedMemory(
            user_id=user_id,
            memory_text=text,
            categories=["general"],
            date=datetime.now().strftime("%Y-%m-%d"),
            embedding=embeddings[0]
        )
        await insert_memories([memory])
        return "Memory stored."

    async def search(self, query: str, user_id: int):
        query_vector = await generate_embeddings([query])
        results = await search_memories(query_vector[0], user_id=user_id)
        return [m.memory_text for m in results]