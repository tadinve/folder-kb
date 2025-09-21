#!/usr/bin/env python3
"""
Knowledge Graph QA System - Project Setup Script

This script creates the initial project structure and installs dependencies
for the construction knowledge graph question-answering system.
"""

import os
import subprocess
import sys
from pathlib import Path

def create_project_structure():
    """Create the project directory structure."""
    
    project_dirs = [
        "knowledge_graph_qa",
        "knowledge_graph_qa/data",
        "knowledge_graph_qa/data/raw",
        "knowledge_graph_qa/data/processed", 
        "knowledge_graph_qa/data/embeddings",
        "knowledge_graph_qa/src",
        "knowledge_graph_qa/src/ingestion",
        "knowledge_graph_qa/src/knowledge_graph",
        "knowledge_graph_qa/src/vector_store",
        "knowledge_graph_qa/src/llm",
        "knowledge_graph_qa/src/api",
        "knowledge_graph_qa/src/ui",
        "knowledge_graph_qa/config",
        "knowledge_graph_qa/logs",
        "knowledge_graph_qa/tests",
        "knowledge_graph_qa/docs",
        "knowledge_graph_qa/notebooks"
    ]
    
    print("🏗️  Creating project structure...")
    for dir_path in project_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")
    
    return "knowledge_graph_qa"

def create_requirements_file(project_dir):
    """Create requirements.txt with all necessary dependencies."""
    
    requirements = """# Knowledge Graph QA System Dependencies

# Core Framework
streamlit>=1.28.0
langchain>=0.0.350
python-dotenv>=1.0.0

# Document Processing
pypdf2>=3.0.1
python-docx>=0.8.11
openpyxl>=3.1.2
python-magic>=0.4.27
textract>=1.6.5

# NLP & ML
spacy>=3.7.0
transformers>=4.35.0
sentence-transformers>=2.2.2
torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0

# Knowledge Graph
neo4j>=5.13.0
py2neo>=2021.2.4

# Vector Database
lancedb>=0.3.0
faiss-cpu>=1.7.4

# LLM Integration
openai>=1.0.0
anthropic>=0.3.0
huggingface-hub>=0.17.0

# Web Interface & Visualization
plotly>=5.17.0
networkx>=3.2.0
pyvis>=0.3.2
streamlit-agraph>=0.0.45

# Utilities
requests>=2.31.0
pydantic>=2.5.0
rich>=13.7.0
tqdm>=4.66.0
schedule>=1.2.0

# Development & Testing
pytest>=7.4.0
black>=23.9.0
flake8>=6.1.0
mypy>=1.7.0
jupyter>=1.0.0

# Database & Storage
sqlalchemy>=2.0.0
redis>=5.0.0
"""
    
    requirements_path = Path(project_dir) / "requirements.txt"
    with open(requirements_path, 'w') as f:
        f.write(requirements)
    
    print(f"📋 Created requirements.txt")
    return requirements_path

def create_config_files(project_dir):
    """Create configuration files."""
    
    # Environment configuration
    env_content = """# Knowledge Graph QA System Configuration

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# LanceDB Configuration
LANCEDB_PATH=./data/vector_store

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_hf_key_here

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4000
EMBEDDING_MODEL=all-MiniLM-L6-v2
"""
    
    env_path = Path(project_dir) / ".env.example"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    # Docker Compose for Neo4j
    docker_compose = """version: '3.8'

services:
  neo4j:
    image: neo4j:5.13
    container_name: kg_neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/password123
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    networks:
      - kg_network

  redis:
    image: redis:7-alpine
    container_name: kg_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - kg_network

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  redis_data:

networks:
  kg_network:
    driver: bridge
"""
    
    docker_path = Path(project_dir) / "docker-compose.yml"
    with open(docker_path, 'w') as f:
        f.write(docker_compose)
    
    print(f"🐳 Created Docker Compose configuration")
    print(f"🔧 Created environment configuration")

def create_main_modules(project_dir):
    """Create main Python modules with basic structure."""
    
    # Main application entry point
    main_app = '''"""
Knowledge Graph QA System - Main Application
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from ui.main_interface import KnowledgeGraphApp

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Construction Knowledge Graph QA",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    app = KnowledgeGraphApp()
    app.run()

if __name__ == "__main__":
    main()
'''
    
    app_path = Path(project_dir) / "app.py"
    with open(app_path, 'w') as f:
        f.write(main_app)
    
    # Configuration module
    config_module = '''"""
Configuration management for Knowledge Graph QA System
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Neo4j Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password123")
    
    # LanceDB Configuration
    lancedb_path: str = os.getenv("LANCEDB_PATH", "./data/vector_store")
    
    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Processing Configuration
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Paths
    data_dir: Path = Path("./data")
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    embeddings_dir: Path = data_dir / "embeddings"
    logs_dir: Path = Path("./logs")
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
'''
    
    config_path = Path(project_dir) / "src" / "config.py"
    with open(config_path, 'w') as f:
        f.write(config_module)
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/ingestion/__init__.py", 
        "src/knowledge_graph/__init__.py",
        "src/vector_store/__init__.py",
        "src/llm/__init__.py",
        "src/api/__init__.py",
        "src/ui/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(project_dir) / init_file
        init_path.touch()
    
    print(f"🐍 Created main Python modules")

def create_readme(project_dir):
    """Create comprehensive README."""
    
    readme_content = '''# Construction Knowledge Graph QA System

A comprehensive question-answering system built on knowledge graphs for construction project management.

## 🏗️ Architecture

- **Neo4j**: Knowledge graph database for structured relationships
- **LanceDB**: Vector database for semantic search
- **LangChain**: LLM orchestration and processing
- **Streamlit**: Web interface
- **Open-source LLMs**: Local/cloud language models

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and setup
cd knowledge_graph_qa
python -m venv venv
source venv/bin/activate  # or `venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
```

### 2. Start Databases

```bash
# Start Neo4j and Redis
docker-compose up -d

# Verify Neo4j is running
# Open http://localhost:7474 in browser
# Login with neo4j/password123
```

### 3. Configure Environment

```bash
# Copy and edit configuration
cp .env.example .env
# Edit .env with your API keys and settings
```

### 4. Run Application

```bash
# Start Streamlit app
streamlit run app.py

# Or run individual components
python -m src.ingestion.document_processor
python -m src.api.main
```

## 📊 Features

### Document Processing
- PDF, Word, Excel document parsing
- Entity extraction and relationship detection
- Automatic knowledge graph population

### Knowledge Graph
- Construction project schema
- Relationship mapping
- Graph-based queries

### Vector Search
- Semantic document search
- Similarity matching
- Embedding-based retrieval

### Question Answering
- Natural language queries
- Context-aware responses
- Source attribution

### Web Interface
- Interactive Q&A
- Graph visualization
- Analytics dashboard
- Admin controls

## 🗂️ Project Structure

```
knowledge_graph_qa/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Database services
├── .env.example          # Configuration template
├── src/
│   ├── config.py         # Settings management
│   ├── ingestion/        # Document processing
│   ├── knowledge_graph/  # Neo4j operations
│   ├── vector_store/     # LanceDB operations
│   ├── llm/             # Language model integration
│   ├── api/             # REST API
│   └── ui/              # Streamlit components
├── data/
│   ├── raw/             # Original documents
│   ├── processed/       # Processed data
│   └── embeddings/      # Vector embeddings
├── tests/               # Test suite
├── docs/               # Documentation
└── notebooks/          # Jupyter notebooks
```

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing](docs/contributing.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
'''
    
    readme_path = Path(project_dir) / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"📚 Created README.md")

def main():
    """Main setup function."""
    print("🚀 Setting up Knowledge Graph QA System Project")
    print("=" * 50)
    
    # Create project structure
    project_dir = create_project_structure()
    
    # Create configuration files
    create_requirements_file(project_dir)
    create_config_files(project_dir)
    create_main_modules(project_dir)
    create_readme(project_dir)
    
    print("\n✅ Project setup complete!")
    print("\n📋 Next Steps:")
    print("1. cd knowledge_graph_qa")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate")
    print("4. pip install -r requirements.txt")
    print("5. cp .env.example .env")
    print("6. docker-compose up -d")
    print("7. streamlit run app.py")
    
    print("\n🌐 Access points:")
    print("• Streamlit App: http://localhost:8501")
    print("• Neo4j Browser: http://localhost:7474")
    print("• Neo4j Bolt: bolt://localhost:7687")

if __name__ == "__main__":
    main()