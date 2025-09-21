# Construction Knowledge Graph QA System

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
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
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
