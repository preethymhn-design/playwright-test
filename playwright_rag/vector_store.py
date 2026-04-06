# vector_store.py
# LangChain-backed vector store using FAISS + HuggingFace embeddings.

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStore:
    """
    FAISS vector store powered by LangChain.

    Usage:
        store = VectorStore()
        store.add_documents(["chunk1", "chunk2"], metadata=[{"source": "file.md"}])
        results = store.search("my query", top_k=5)
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self._db = None  # FAISS index, built on first add

    def add_documents(self, chunks, metadata=None):
        """Embed and store a list of text chunks."""
        if not chunks:
            return
        docs = [
            Document(
                page_content=chunk,
                metadata=metadata[i] if metadata else {}
            )
            for i, chunk in enumerate(chunks)
        ]
        if self._db is None:
            self._db = FAISS.from_documents(docs, self.embeddings)
        else:
            self._db.add_documents(docs)
        print(f"  Stored {len(chunks)} chunks (total: {len(self)})")

    def search(self, query, top_k=5):
        """
        Return top_k most similar chunks to the query.
        Returns list of dicts: [{text, score, metadata}]
        """
        if self._db is None:
            return []
        results = self._db.similarity_search_with_score(query, k=top_k)
        return [
            {
                "text": doc.page_content,
                "score": float(score),
                "metadata": doc.metadata,
            }
            for doc, score in results
        ]

    def as_retriever(self, top_k=5):
        """Return a LangChain retriever for use in chains."""
        if self._db is None:
            raise ValueError("Vector store is empty. Ingest documents first.")
        return self._db.as_retriever(search_kwargs={"k": top_k})

    def __len__(self):
        if self._db is None:
            return 0
        return self._db.index.ntotal
