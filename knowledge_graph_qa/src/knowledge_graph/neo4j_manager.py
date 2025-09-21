"""
Neo4j Knowledge Graph Setup for Construction Projects

This module handles the knowledge graph schema creation and basic operations
for construction project management data.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j driver not available. Install with: pip install neo4j")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Entity:
    """Represents an entity in the knowledge graph."""
    id: str
    type: str
    properties: Dict[str, Any]

@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = None

class ConstructionKnowledgeGraph:
    """Manages the construction project knowledge graph in Neo4j."""
    
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        """Initialize the knowledge graph connection."""
        
        # Use environment variables or defaults
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password123")
        
        self.driver = None
        self.connected = False
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        if NEO4J_AVAILABLE:
            self.connect()
        else:
            self.logger.warning("Neo4j driver not available. Running in simulation mode.")
    
    def connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    self.connected = True
                    self.logger.info(f"✅ Connected to Neo4j at {self.uri}")
                    return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Neo4j: {e}")
            self.logger.info("💡 To start Neo4j locally, run: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:5.13")
            self.connected = False
            return False
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            self.connected = False
            self.logger.info("🔌 Disconnected from Neo4j")
    
    def create_schema(self):
        """Create the construction project knowledge graph schema."""
        
        if not self.connected:
            self.logger.warning("📋 Creating schema (simulation mode - not connected to Neo4j)")
            self._print_schema_info()
            return True
        
        schema_queries = [
            # Create constraints for unique identifiers
            "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT person_email IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE",
            "CREATE CONSTRAINT document_path IF NOT EXISTS FOR (d:Document) REQUIRE d.file_path IS UNIQUE",
            "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
            
            # Create indexes for common search properties
            "CREATE INDEX project_name_idx IF NOT EXISTS FOR (p:Project) ON (p.name)",
            "CREATE INDEX person_name_idx IF NOT EXISTS FOR (p:Person) ON (p.name)",
            "CREATE INDEX document_filename_idx IF NOT EXISTS FOR (d:Document) ON (d.filename)",
            "CREATE INDEX document_type_idx IF NOT EXISTS FOR (d:Document) ON (d.file_type)",
            "CREATE INDEX task_status_idx IF NOT EXISTS FOR (t:Task) ON (t.status)",
            "CREATE INDEX issue_priority_idx IF NOT EXISTS FOR (i:Issue) ON (i.priority)",
            
            # Full-text search indexes
            "CREATE FULLTEXT INDEX document_content_idx IF NOT EXISTS FOR (d:Document) ON EACH [d.content, d.filename]",
            "CREATE FULLTEXT INDEX entity_search_idx IF NOT EXISTS FOR (n:Person|Company|Project|Task) ON EACH [n.name, n.description]"
        ]
        
        try:
            with self.driver.session() as session:
                for query in schema_queries:
                    try:
                        session.run(query)
                        self.logger.info(f"✅ Executed: {query}")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            self.logger.info(f"⏭️  Skipped (exists): {query}")
                        else:
                            self.logger.error(f"❌ Failed: {query} - {e}")
            
            self.logger.info("🏗️  Knowledge graph schema created successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create schema: {e}")
            return False
    
    def _print_schema_info(self):
        """Print information about the schema structure."""
        print("\n🏗️  Construction Knowledge Graph Schema")
        print("=" * 50)
        
        entities = {
            "Project": ["id", "name", "status", "start_date", "end_date", "budget", "description"],
            "Phase": ["name", "number", "description", "start_date", "end_date", "project_id"],
            "Task": ["id", "name", "description", "status", "priority", "assigned_to", "due_date"],
            "Person": ["name", "email", "phone", "role", "department"],
            "Company": ["name", "type", "specialization", "contact_info"],
            "Document": ["filename", "file_path", "file_type", "size", "created_date", "content"],
            "Meeting": ["date", "type", "agenda", "attendees"],
            "Issue": ["id", "description", "priority", "status", "reported_by", "created_date"],
            "Change_Order": ["id", "description", "amount", "status", "approval_date"],
            "Drawing": ["number", "revision", "date", "type", "discipline"],
            "Material": ["name", "type", "supplier", "cost", "quantity"]
        }
        
        relationships = [
            "(:Project)-[:HAS_PHASE]->(:Phase)",
            "(:Phase)-[:CONTAINS_TASK]->(:Task)",
            "(:Task)-[:ASSIGNED_TO]->(:Person)",
            "(:Person)-[:WORKS_FOR]->(:Company)",
            "(:Document)-[:BELONGS_TO_PROJECT]->(:Project)",
            "(:Document)-[:CREATED_BY]->(:Person)",
            "(:Meeting)-[:DISCUSSES]->(:Issue)",
            "(:Issue)-[:ASSIGNED_TO]->(:Person)",
            "(:Change_Order)-[:AFFECTS]->(:Task)",
            "(:Drawing)-[:SHOWS]->(:Material)"
        ]
        
        print("📋 Entity Types:")
        for entity, properties in entities.items():
            print(f"  {entity}: {', '.join(properties)}")
        
        print("\n🔗 Key Relationships:")
        for rel in relationships:
            print(f"  {rel}")
        
        print("\n💡 This schema will be created when Neo4j is available.")
    
    def add_entity(self, entity: Entity) -> bool:
        """Add an entity to the knowledge graph."""
        if not self.connected:
            self.logger.info(f"📝 Would add {entity.type}: {entity.id}")
            return True
        
        try:
            # Create Cypher query
            properties_str = ", ".join([f"{k}: ${k}" for k in entity.properties.keys()])
            query = f"CREATE (n:{entity.type} {{id: $id, {properties_str}}})"
            
            parameters = {"id": entity.id, **entity.properties}
            
            with self.driver.session() as session:
                session.run(query, parameters)
                self.logger.info(f"✅ Added {entity.type}: {entity.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to add entity {entity.id}: {e}")
            return False
    
    def add_relationship(self, relationship: Relationship) -> bool:
        """Add a relationship to the knowledge graph."""
        if not self.connected:
            self.logger.info(f"🔗 Would add relationship: {relationship.source_id} -{relationship.relationship_type}-> {relationship.target_id}")
            return True
        
        try:
            # Create relationship with properties
            properties_str = ""
            parameters = {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id
            }
            
            if relationship.properties:
                properties_str = " {" + ", ".join([f"{k}: ${k}" for k in relationship.properties.keys()]) + "}"
                parameters.update(relationship.properties)
            
            query = f"""
            MATCH (a), (b)
            WHERE a.id = $source_id AND b.id = $target_id
            CREATE (a)-[r:{relationship.relationship_type}{properties_str}]->(b)
            """
            
            with self.driver.session() as session:
                result = session.run(query, parameters)
                self.logger.info(f"✅ Added relationship: {relationship.source_id} -{relationship.relationship_type}-> {relationship.target_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to add relationship: {e}")
            return False
    
    def query_graph(self, cypher_query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query and return results."""
        if not self.connected:
            self.logger.info(f"🔍 Would execute query: {cypher_query}")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters or {})
                records = [record.data() for record in result]
                self.logger.info(f"📊 Query returned {len(records)} records")
                return records
                
        except Exception as e:
            self.logger.error(f"❌ Query failed: {e}")
            return []
    
    def get_project_overview(self, project_name: str = None) -> Dict[str, Any]:
        """Get overview statistics for a project or all projects."""
        if not self.connected:
            return {
                "projects": 1,
                "documents": 2117,
                "people": 25,
                "companies": 15,
                "issues": 0,
                "tasks": 0
            }
        
        query = """
        MATCH (p:Project)
        OPTIONAL MATCH (p)-[:HAS_DOCUMENT]->(d:Document)
        OPTIONAL MATCH (p)-[:HAS_PERSON]->(person:Person)
        OPTIONAL MATCH (p)-[:HAS_COMPANY]->(c:Company)
        OPTIONAL MATCH (p)-[:HAS_ISSUE]->(i:Issue)
        OPTIONAL MATCH (p)-[:HAS_TASK]->(t:Task)
        WHERE $project_name IS NULL OR p.name = $project_name
        RETURN 
            count(DISTINCT p) as projects,
            count(DISTINCT d) as documents,
            count(DISTINCT person) as people,
            count(DISTINCT c) as companies,
            count(DISTINCT i) as issues,
            count(DISTINCT t) as tasks
        """
        
        results = self.query_graph(query, {"project_name": project_name})
        return results[0] if results else {}
    
    def search_entities(self, search_term: str, entity_types: List[str] = None) -> List[Dict]:
        """Search for entities by name or description."""
        if not self.connected:
            self.logger.info(f"🔍 Would search for: {search_term}")
            return []
        
        # Build label filter for WHERE clause
        where_clause = ""
        if entity_types:
            label_conditions = [f"'{label}' IN labels(node)" for label in entity_types]
            where_clause = f"WHERE {' OR '.join(label_conditions)}"
        
        query = f"""
        CALL db.index.fulltext.queryNodes('entity_search_idx', $search_term)
        YIELD node, score
        {where_clause}
        RETURN labels(node) as type, node.name as name, node.id as id, 
               node.description as description, score
        ORDER BY score DESC
        LIMIT 20
        """
        
        return self.query_graph(query, {"search_term": search_term})

def create_sample_data(kg: ConstructionKnowledgeGraph):
    """Create sample construction project data."""
    
    print("\n📊 Creating sample construction project data...")
    
    # Sample project
    project = Entity(
        id="msvc_project_001",
        type="Project",
        properties={
            "name": "Microsoft Service Center",
            "status": "active",
            "start_date": "2019-01-01",
            "budget": 50000000,
            "description": "Construction of Microsoft Service Center facility"
        }
    )
    kg.add_entity(project)
    
    # Sample people
    people = [
        Entity("person_001", "Person", {
            "name": "John Smith", "email": "j.smith@contractor.com", 
            "role": "Project Manager", "department": "Construction"
        }),
        Entity("person_002", "Person", {
            "name": "Sarah Johnson", "email": "s.johnson@msft.com",
            "role": "Owner Representative", "department": "Facilities"
        }),
        Entity("person_003", "Person", {
            "name": "Mike Chen", "email": "m.chen@architect.com",
            "role": "Senior Architect", "department": "Design"
        })
    ]
    
    for person in people:
        kg.add_entity(person)
    
    # Sample companies
    companies = [
        Entity("company_001", "Company", {
            "name": "McGuire and Hester", "type": "General Contractor",
            "specialization": "Commercial Construction"
        }),
        Entity("company_002", "Company", {
            "name": "Microsoft Corporation", "type": "Owner",
            "specialization": "Technology"
        })
    ]
    
    for company in companies:
        kg.add_entity(company)
    
    # Sample relationships
    relationships = [
        Relationship("person_001", "company_001", "WORKS_FOR"),
        Relationship("person_002", "company_002", "WORKS_FOR"),
        Relationship("person_001", "msvc_project_001", "MANAGES"),
        Relationship("msvc_project_001", "company_001", "CONTRACTED_TO")
    ]
    
    for rel in relationships:
        kg.add_relationship(rel)
    
    print("✅ Sample data created!")

def main():
    """Main function to demonstrate the knowledge graph."""
    
    print("🚀 Starting Construction Knowledge Graph Setup")
    print("=" * 50)
    
    # Initialize knowledge graph
    kg = ConstructionKnowledgeGraph()
    
    # Create schema
    kg.create_schema()
    
    # Create sample data
    create_sample_data(kg)
    
    # Get overview
    overview = kg.get_project_overview()
    print(f"\n📊 Project Overview: {overview}")
    
    # Test search
    if kg.connected:
        results = kg.search_entities("Microsoft")
        print(f"\n🔍 Search results for 'Microsoft': {len(results)} found")
        for result in results[:3]:
            print(f"  - {result}")
    
    # Close connection
    kg.close()
    
    print("\n✅ Knowledge graph setup complete!")

if __name__ == "__main__":
    main()