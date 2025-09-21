#!/usr/bin/env python3
"""
Test script for the Construction Q&A Agent
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.knowledge_graph.neo4j_manager import ConstructionKnowledgeGraph
from src.llm.qa_agent import create_qa_agent

def test_qa_agent():
    """Test the Q&A agent with sample questions"""
    
    print("🤖 Testing Construction Q&A Agent")
    print("=" * 50)
    
    # Initialize knowledge graph and Q&A agent
    print("🔌 Connecting to knowledge graph...")
    kg = ConstructionKnowledgeGraph()
    
    if not kg.connected:
        print("❌ Neo4j not connected - some features may not work")
    else:
        print("✅ Connected to Neo4j")
    
    print("🧠 Creating Q&A agent...")
    qa_agent = create_qa_agent(kg)
    
    # Test questions
    test_questions = [
        "Who is the project manager?",
        "What's the status of the Microsoft project?", 
        "Show me all people in the system",
        "What companies are involved?",
        "Find all documents",
        "Are there any issues?",
        "What's the project budget?"
    ]
    
    print(f"\n🧪 Testing {len(test_questions)} questions...")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] ❓ Question: {question}")
        print("-" * 40)
        
        try:
            response = qa_agent.ask(question)
            
            print(f"💬 Answer: {response.answer[:200]}...")
            print(f"🎯 Confidence: {response.confidence:.1%}")
            print(f"📚 Sources: {len(response.sources)} entities found")
            
            if response.suggestions:
                print(f"💡 Suggestions: {len(response.suggestions)} available")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Q&A Agent test complete!")
    print("\n🚀 Ready to launch Streamlit interface:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    test_qa_agent()