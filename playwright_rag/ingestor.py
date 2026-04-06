# ingestor.py
# LangChain document loaders + text splitter → VectorStore.

import os
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class Ingestor:
    """
    Loads .txt, .md, and .pdf files using LangChain loaders,
    splits them with RecursiveCharacterTextSplitter, and feeds into VectorStore.

    Usage:
        ingestor = Ingestor(vector_store, chunk_size=500, overlap=50)
        ingestor.ingest_file("docs/my_spec.md")
        ingestor.ingest_folder("docs/")
    """

    def __init__(self, vector_store, chunk_size=500, overlap=50):
        self.store = vector_store
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def ingest_file(self, path):
        """Load a single file, split, and add to the vector store."""
        ext = os.path.splitext(path)[1].lower()
        print(f"Ingesting: {path}")

        if ext == ".pdf":
            docs = self._load_pdf(path)
        elif ext == ".md":
            docs = self._load_md(path)
        else:
            docs = TextLoader(path, encoding="utf-8").load()

        chunks = self.splitter.split_documents(docs)
        # Ensure source metadata is set
        for chunk in chunks:
            chunk.metadata.setdefault("source", os.path.basename(path))

        texts = [c.page_content for c in chunks]
        meta = [c.metadata for c in chunks]
        self.store.add_documents(texts, metadata=meta)

    def ingest_folder(self, folder):
        """Recursively ingest all .txt, .md, .pdf files in a folder."""
        supported = {".txt", ".md", ".pdf"}
        for root, _, files in os.walk(folder):
            for fname in sorted(files):
                if os.path.splitext(fname)[1].lower() in supported:
                    self.ingest_file(os.path.join(root, fname))

    def ingest_text(self, text, source="inline"):
        """Directly ingest a raw string."""
        from langchain_core.documents import Document
        docs = [Document(page_content=text, metadata={"source": source})]
        chunks = self.splitter.split_documents(docs)
        texts = [c.page_content for c in chunks]
        meta = [c.metadata for c in chunks]
        self.store.add_documents(texts, metadata=meta)

    def _load_md(self, path):
        """Load markdown — fall back to TextLoader if unstructured not installed."""
        try:
            return UnstructuredMarkdownLoader(path).load()
        except Exception:
            return TextLoader(path, encoding="utf-8").load()

    def _load_pdf(self, path):
        """Load PDF using LangChain's PyPDFLoader."""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            return PyPDFLoader(path).load()
        except ImportError:
            raise ImportError("Install pypdf to read PDFs: pip install pypdf")
