import csv
from neo4j import GraphDatabase
import os

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"  # Change as needed

CSV_PATH = "DocLabs_Sample_Project_Template/file_inventory_DocLabs_Sample_Project_Template_20250920_220124.csv"

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def clear_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_indexes(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.full_path IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Folder) REQUIRE f.path IS UNIQUE")

def load_documents(tx, rows):
    for row in rows:
        folder = row['directory']
        filename = row['filename']
        ext = row.get('file_type', '').upper()
        full_path = row['full_path']
        size = row['size_human']
        modified = row['modified_date']
        created = row['created_date']
        # Create Folder node
        tx.run("MERGE (f:Folder {path: $folder})", folder=folder)
        # Create Document node
        tx.run("MERGE (d:Document {full_path: $full_path}) SET d.filename=$filename, d.ext=$ext, d.size=$size, d.modified=$modified, d.created=$created",
               full_path=full_path, filename=filename, ext=ext, size=size, modified=modified, created=created)
        # Link Folder -> Document
        tx.run("MATCH (f:Folder {path: $folder}), (d:Document {full_path: $full_path}) MERGE (f)-[:CONTAINS]->(d)",
               folder=folder, full_path=full_path)

def main():
    with driver.session() as session:
        print("Clearing database...")
        session.write_transaction(clear_database)
        print("Creating indexes...")
        session.write_transaction(create_indexes)
        print("Loading documents from CSV...")
        with open(CSV_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            session.write_transaction(load_documents, rows)
        print(f"Loaded {len(rows)} documents.")

if __name__ == "__main__":
    main()
    driver.close()
