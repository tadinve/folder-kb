"""
Construction Q&A Agent - TrunkText-inspired intelligent assistant
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..knowledge_graph.neo4j_manager import ConstructionKnowledgeGraph
from ..config import load_config

@dataclass
class QueryContext:
    """Context for a user query"""
    question: str
    user_id: Optional[str] = None
    project_context: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class QAResponse:
    """Response from Q&A agent"""
    answer: str
    confidence: float
    sources: List[Dict]
    reasoning: str
    suggestions: List[str]

class ConstructionQAAgent:
    """
    TrunkText-inspired Q&A Agent for Construction Projects
    
    Features:
    - Natural language queries about project data
    - Construction-specific context understanding
    - Knowledge graph integration
    - Document source attribution
    - Smart suggestions for follow-up questions
    """
    
    def __init__(self, knowledge_graph: ConstructionKnowledgeGraph):
        self.kg = knowledge_graph
        self.logger = logging.getLogger(__name__)
        self.config = load_config()
        
        # Construction-specific query patterns
        self.query_patterns = {
            'project_info': [
                'project', 'budget', 'timeline', 'status', 'schedule',
                'start date', 'end date', 'completion', 'progress'
            ],
            'people': [
                'manager', 'contractor', 'team', 'contact', 'responsible',
                'assigned', 'who is', 'who does', 'person', 'employee'
            ],
            'documents': [
                'document', 'file', 'drawing', 'specification', 'contract',
                'submittal', 'rfi', 'plan', 'blueprint', 'report'
            ],
            'issues': [
                'problem', 'issue', 'delay', 'conflict', 'risk',
                'discrepancy', 'change order', 'concern'
            ],
            'materials': [
                'material', 'equipment', 'supply', 'vendor', 'cost',
                'procurement', 'delivery', 'installation'
            ],
            'schedule': [
                'when', 'deadline', 'milestone', 'phase', 'task',
                'due date', 'completion date', 'schedule'
            ]
        }
        
        # Common construction questions and responses
        self.sample_questions = [
            "Who is the project manager for the Microsoft project?",
            "What documents are related to the elevator system?",
            "What's the current status of the project?",
            "Show me all pending tasks",
            "What companies are involved in this project?",
            "Find all files related to electrical work",
            "When is the project scheduled to complete?",
            "What issues need immediate attention?"
        ]
    
    def classify_query_type(self, question: str) -> str:
        """Classify the type of construction query"""
        question_lower = question.lower()
        
        scores = {}
        for category, keywords in self.query_patterns.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return 'general'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def extract_entities_from_query(self, question: str) -> Dict[str, List[str]]:
        """Extract potential entity references from the question"""
        entities = {
            'projects': [],
            'people': [],
            'companies': [],
            'documents': [],
            'tasks': []
        }
        
        # Simple keyword extraction (in production, use NER)
        question_lower = question.lower()
        
        # Look for project names
        if 'microsoft' in question_lower:
            entities['projects'].append('Microsoft Service Center')
        
        # Look for file types
        file_types = ['drawing', 'spec', 'contract', 'rfi', 'submittal', 'plan']
        for file_type in file_types:
            if file_type in question_lower:
                entities['documents'].append(file_type)
        
        # Look for roles
        roles = ['manager', 'contractor', 'superintendent', 'engineer']
        for role in roles:
            if role in question_lower:
                entities['people'].append(role)
        
        return entities
    
    def generate_cypher_query(self, question: str, query_type: str, entities: Dict) -> str:
        """Generate Cypher query based on the natural language question"""
        
        if query_type == 'people':
            if 'manager' in question.lower():
                return """
                MATCH (p:Person)-[r:MANAGES]->(proj:Project)
                RETURN p.name as name, p.role as role, p.email as email, 
                       proj.name as project_name
                """
            else:
                return """
                MATCH (p:Person)
                OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
                RETURN p.name as name, p.role as role, p.email as email,
                       c.name as company_name
                LIMIT 10
                """
        
        elif query_type == 'project_info':
            return """
            MATCH (p:Project)
            OPTIONAL MATCH (p)-[:CONTRACTED_TO]->(c:Company)
            RETURN p.id as id, p.name as name, p.status as status,
                   p.start_date as start_date, p.budget as budget,
                   p.description as description, c.name as contractor
            """
        
        elif query_type == 'documents':
            return """
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:BELONGS_TO_PROJECT]->(p:Project)
            RETURN d.filename as filename, d.file_type as type,
                   d.size as size, d.created_date as created,
                   p.name as project_name
            LIMIT 20
            """
        
        elif query_type == 'issues':
            return """
            MATCH (i:Issue)
            OPTIONAL MATCH (i)-[:ASSIGNED_TO]->(p:Person)
            OPTIONAL MATCH (i)-[:BELONGS_TO_PROJECT]->(proj:Project)
            RETURN i.id as id, i.description as description,
                   i.priority as priority, i.status as status,
                   p.name as assigned_to, proj.name as project_name
            """
        
        else:  # general query
            return """
            MATCH (n)
            WHERE n.name IS NOT NULL
            RETURN labels(n) as type, n.name as name,
                   CASE 
                     WHEN n.description IS NOT NULL THEN n.description
                     WHEN n.status IS NOT NULL THEN n.status
                     ELSE 'No description'
                   END as description
            LIMIT 10
            """
    
    def format_response(self, results: List[Dict], query_type: str, question: str) -> QAResponse:
        """Format the database results into a natural language response"""
        
        if not results:
            return QAResponse(
                answer="I couldn't find any information related to your question. Could you try rephrasing it or asking about a specific project, person, or document?",
                confidence=0.1,
                sources=[],
                reasoning="No matching data found in the knowledge graph",
                suggestions=self.sample_questions[:3]
            )
        
        # Format response based on query type
        if query_type == 'people':
            if len(results) == 1:
                person = results[0]
                answer = f"**{person.get('name', 'Unknown')}** is the {person.get('role', 'team member')}"
                if person.get('project_name'):
                    answer += f" for the {person['project_name']} project"
                if person.get('email'):
                    answer += f". You can reach them at {person['email']}"
                if person.get('company_name'):
                    answer += f". They work for {person['company_name']}"
            else:
                answer = f"I found {len(results)} people:\n\n"
                for person in results[:5]:
                    answer += f"• **{person.get('name', 'Unknown')}** - {person.get('role', 'Team member')}"
                    if person.get('company_name'):
                        answer += f" at {person['company_name']}"
                    answer += "\n"
        
        elif query_type == 'project_info':
            if results:
                project = results[0]
                answer = f"**{project.get('name', 'Project')}**\n\n"
                answer += f"• **Status**: {project.get('status', 'Unknown')}\n"
                answer += f"• **Budget**: ${project.get('budget', 'Unknown'):,}\n" if project.get('budget') else ""
                answer += f"• **Start Date**: {project.get('start_date', 'Unknown')}\n"
                if project.get('contractor'):
                    answer += f"• **Contractor**: {project['contractor']}\n"
                if project.get('description'):
                    answer += f"• **Description**: {project['description']}\n"
        
        elif query_type == 'documents':
            answer = f"I found {len(results)} documents:\n\n"
            for doc in results[:10]:
                answer += f"• **{doc.get('filename', 'Unknown file')}**"
                if doc.get('type'):
                    answer += f" ({doc['type']})"
                if doc.get('project_name'):
                    answer += f" - {doc['project_name']}"
                answer += "\n"
        
        else:  # general
            answer = f"Here's what I found:\n\n"
            for item in results[:5]:
                answer += f"• **{item.get('name', 'Unknown')}** ({', '.join(item.get('type', ['Unknown']))})"
                if item.get('description') and item['description'] != 'No description':
                    answer += f" - {item['description']}"
                answer += "\n"
        
        # Generate suggestions
        suggestions = [
            "Show me more details about this project",
            "Who else is involved in this project?",
            "What documents are related to this?",
            "Are there any issues or concerns?"
        ]
        
        return QAResponse(
            answer=answer,
            confidence=0.8 if results else 0.1,
            sources=results,
            reasoning=f"Found {len(results)} matches using {query_type} query pattern",
            suggestions=suggestions
        )
    
    def ask(self, question: str, context: Optional[QueryContext] = None) -> QAResponse:
        """
        Main Q&A interface - ask a natural language question
        """
        try:
            self.logger.info(f"🤖 Processing question: {question}")
            
            # Create context if not provided
            if context is None:
                context = QueryContext(question=question)
            
            # Step 1: Classify the query type
            query_type = self.classify_query_type(question)
            self.logger.info(f"📊 Query classified as: {query_type}")
            
            # Step 2: Extract entities from the question
            entities = self.extract_entities_from_query(question)
            self.logger.info(f"🔍 Extracted entities: {entities}")
            
            # Step 3: Generate appropriate Cypher query
            cypher_query = self.generate_cypher_query(question, query_type, entities)
            self.logger.info(f"🔍 Generated Cypher: {cypher_query[:100]}...")
            
            # Step 4: Execute query against knowledge graph
            results = self.kg.query_graph(cypher_query)
            self.logger.info(f"📊 Found {len(results)} results")
            
            # Step 5: Format response
            response = self.format_response(results, query_type, question)
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error processing question: {str(e)}")
            return QAResponse(
                answer=f"I encountered an error while processing your question: {str(e)}. Please try again.",
                confidence=0.0,
                sources=[],
                reasoning=f"Error: {str(e)}",
                suggestions=self.sample_questions[:3]
            )
    
    def get_sample_questions(self) -> List[str]:
        """Get sample questions users can ask"""
        return self.sample_questions

def create_qa_agent(knowledge_graph: ConstructionKnowledgeGraph) -> ConstructionQAAgent:
    """Factory function to create a Q&A agent"""
    return ConstructionQAAgent(knowledge_graph)

# Example usage for testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create knowledge graph connection
    kg = ConstructionKnowledgeGraph()
    
    # Create Q&A agent
    qa_agent = create_qa_agent(kg)
    
    # Test questions
    test_questions = [
        "Who is the project manager?",
        "What's the status of the Microsoft project?",
        "Show me all people in the system",
        "What companies are involved?"
    ]
    
    print("🤖 Construction Q&A Agent Test")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = qa_agent.ask(question)
        print(f"💬 Answer: {response.answer}")
        print(f"🎯 Confidence: {response.confidence:.2f}")
        print(f"📚 Sources: {len(response.sources)} found")