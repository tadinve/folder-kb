"""
Configuration management for Knowledge Graph QA System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    def __init__(self):
        # Neo4j Configuration
        self.neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password123")
        
        # LanceDB Configuration
        self.lancedb_path: str = os.getenv("LANCEDB_PATH", "./data/vector_store")
        
        # LLM Configuration
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
        
        # Processing Configuration
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Paths
        self.data_dir: Path = Path("./data")
        self.raw_data_dir: Path = self.data_dir / "raw"
        self.processed_data_dir: Path = self.data_dir / "processed"
        self.embeddings_dir: Path = self.data_dir / "embeddings"
        self.logs_dir: Path = Path("./logs")

# Factory function to create settings
def load_config() -> Settings:
    """Load application configuration."""
    return Settings()

# Global settings instance
settings = Settings()
