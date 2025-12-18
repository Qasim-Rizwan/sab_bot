"""
Sentence Transformer and ChromaDB service for embeddings
"""
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self):
        """Initialize Sentence Transformer and ChromaDB"""
        # All configuration hardcoded (no .env required)
        # Using all-MiniLM-L6-v2 for faster embedding generation (384 dims vs 768)
        self.embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.chroma_persist_dir = './scripts/scripts/chroma_db'
        
        print(f"Loading Sentence Transformer model: {self.embedding_model_name}")
        self.model = SentenceTransformer(self.embedding_model_name)
        
        print(f"Initializing ChromaDB at: {self.chroma_persist_dir}")
        self.client = chromadb.PersistentClient(path=self.chroma_persist_dir)
        
        # Create or get collection
        self.collection = None
    
    def get_or_create_collection(self, name="products"):
        """Get or create a ChromaDB collection"""
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        return self.collection
    
    def encode_text(self, text):
        """Generate embedding for text"""
        return self.model.encode(text, convert_to_tensor=False)
    
    def encode_batch(self, texts):
        """Generate embeddings for batch of texts"""
        return self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
    
    def add_to_collection(self, ids, embeddings, documents, metadatas):
        """Add embeddings to ChromaDB collection"""
        if self.collection is None:
            raise ValueError("Collection not initialized. Call get_or_create_collection() first")
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def query_collection(self, query_embedding, n_results=5):
        """Query collection with embedding"""
        if self.collection is None:
            raise ValueError("Collection not initialized. Call get_or_create_collection() first")
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        return results
    
    def get_collection_count(self):
        """Get number of items in collection"""
        if self.collection is None:
            return 0
        return self.collection.count()

# Global instance
embedding_service = None

def get_embedding_service():
    """Get or create embedding service singleton"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service

