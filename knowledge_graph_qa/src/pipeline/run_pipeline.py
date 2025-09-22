import sys
from pathlib import Path
from pipeline.file_parser import parse_file
from pipeline.llm_entity_extractor import extract_entities_with_llm
from knowledge_graph.neo4j_manager import ConstructionKnowledgeGraph, Entity, Relationship
import os

def main(filename: str, neo4j: bool = True, llm_model: str = "gpt-3.5-turbo"):
    print(f"\n📄 Processing file: {filename}")
    text = parse_file(filename)
    print(f"Extracted {len(text)} characters of text.")

    print("\n🤖 Extracting entities and relationships with LLM...")
    llm_api_key = os.getenv("OPENAI_API_KEY")
    data = extract_entities_with_llm(text, model=llm_model, api_key=llm_api_key)
    print(f"LLM Extraction Result:\n{data}\n")

    if neo4j:
        print("\n🔗 Populating Neo4j knowledge graph...")
        kg = ConstructionKnowledgeGraph()
        # Correct singularization mapping
        entity_type_map = {
            "projects": "Project",
            "people": "Person",
            "companies": "Company",
            "documents": "Document",
            "tasks": "Task",
            "issues": "Issue"
        }
        for entity_type in entity_type_map:
            for ent in data.get(entity_type, []):
                kg.add_entity(Entity(id=ent.get("id", ent.get("name", "")), type=entity_type_map[entity_type], properties=ent))
        for rel in data.get("relationships", []):
            kg.add_relationship(Relationship(
                source_id=rel["source"],
                target_id=rel["target"],
                relationship_type=rel["type"],
                properties=rel.get("properties", {})
            ))
        print("✅ Neo4j population complete!")
    else:
        print("(Neo4j population skipped)")

    print("\n📊 Pipeline complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <filename> [--no-neo4j]")
        sys.exit(1)
    filename = sys.argv[1]
    neo4j = "--no-neo4j" not in sys.argv
    main(filename, neo4j=neo4j)
