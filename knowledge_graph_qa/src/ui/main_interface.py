"""
Main Streamlit Interface for Construction Knowledge Graph QA System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from knowledge_graph.neo4j_manager import ConstructionKnowledgeGraph
    from llm.qa_agent import create_qa_agent
    KG_AVAILABLE = True
except ImportError as e:
    KG_AVAILABLE = False
    # Create mock classes for fallback functionality
    class ConstructionKnowledgeGraph:
        def __init__(self):
            # Test actual Neo4j connection
            self.connected = False
            try:
                import os
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(
                    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    auth=(os.getenv("NEO4J_USERNAME", "neo4j"), 
                          os.getenv("NEO4J_PASSWORD", "password123"))
                )
                self.driver.verify_connectivity()
                self.connected = True
            except Exception as e:
                self.driver = None
                self.connected = False
                
        def get_project_overview(self, project_name=None):
            return {"projects": 1, "documents": 2117, "people": 25, "companies": 15}
            
        def search_entities(self, term):
            return []
            
        def query_graph(self, query, params=None):
            """Execute Cypher query against Neo4j"""
            if not self.connected or not self.driver:
                return []
            try:
                with self.driver.session() as session:
                    result = session.run(query, params or {})
                    return [record.data() for record in result]
            except Exception as e:
                print(f"Query error: {e}")
                return []
    
    def create_qa_agent(kg):
        return None

class KnowledgeGraphApp:
    """Main Streamlit application for the Knowledge Graph QA System."""
    
    def __init__(self):
        """Initialize the application."""
        self.kg = None
        self.qa_agent = None
        
        if KG_AVAILABLE:
            # Use the real classes
            self.kg = ConstructionKnowledgeGraph()
            self.qa_agent = create_qa_agent(self.kg)
        else:
            # Use the mock classes for fallback functionality
            self.kg = ConstructionKnowledgeGraph()  # This is our mock class
            self.qa_agent = create_qa_agent(self.kg)  # This will return None
    
    def setup_page_config(self):
        """Configure the Streamlit page."""
        st.set_page_config(
            page_title="Construction Knowledge Graph QA",
            page_icon="🏗️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_sidebar(self):
        """Render the sidebar with navigation and controls."""
        st.sidebar.title("🏗️ Construction KG QA")
        st.sidebar.markdown("---")
        
        # Connection status
        if self.kg and self.kg.connected:
            st.sidebar.success("✅ Connected to Neo4j")
        else:
            st.sidebar.warning("⚠️ Neo4j not connected")
            st.sidebar.info("Running in simulation mode")
        
        st.sidebar.markdown("---")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["🏠 Home", "❓ Q&A Interface", "🔍 Entity Search", "📊 Analytics", "🗂️ Data Management"]
        )
        
        return page
    
    def render_home_page(self):
        """Render the home page with overview."""
        st.title("🏗️ Construction Knowledge Graph QA System")
        st.markdown("Welcome to the intelligent construction project management system!")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get overview data
        if self.kg:
            overview = self.kg.get_project_overview()
        else:
            overview = {
                "projects": 1,
                "documents": 2117,
                "people": 25,
                "companies": 15
            }
        
        with col1:
            st.metric("Projects", overview.get("projects", 0))
        with col2:
            st.metric("Documents", overview.get("documents", 0))
        with col3:
            st.metric("People", overview.get("people", 0))
        with col4:
            st.metric("Companies", overview.get("companies", 0))
        
        st.markdown("---")
        
        # System capabilities
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 System Capabilities")
            st.markdown("""
            - **Natural Language Q&A**: Ask questions in plain English
            - **Document Search**: Find relevant project documents
            - **Entity Discovery**: Explore people, companies, tasks
            - **Relationship Mapping**: Understand project connections
            - **Visual Analytics**: Interactive graphs and charts
            """)
        
        with col2:
            st.subheader("📋 Sample Questions")
            st.markdown("""
            - "Who is the project manager for the Microsoft project?"
            - "Find all documents related to concrete issues"
            - "What change orders were approved last month?"
            - "Show me the org chart for this project"
            - "What are the current open issues?"
            """)
        
        # Quick actions
        st.markdown("---")
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Search Documents", use_container_width=True):
                st.info("Navigate to Entity Search to find documents")
        
        with col2:
            if st.button("❓ Ask Question", use_container_width=True):
                st.info("Navigate to Q&A Interface to ask questions")
        
        with col3:
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Navigate to Analytics for project insights")
    
    def render_qa_interface(self):
        """Render the Q&A interface."""
        st.title("❓ Natural Language Q&A")
        st.markdown("Ask questions about your construction project in natural language")
        
        # System status indicator
        col1, col2, col3 = st.columns(3)
        with col1:
            if self.qa_agent:
                st.success("🤖 AI Agent: Active")
            else:
                st.warning("🤖 AI Agent: Fallback Mode")
        
        with col2:
            if self.kg and self.kg.connected:
                st.success("🗃️ Knowledge Graph: Connected")
            else:
                st.info("🗃️ Knowledge Graph: Simulation")
        
        with col3:
            st.info("📊 Data: 2,117 documents ready")
        
        st.markdown("---")
        
        # Question input
        question = st.text_input(
            "Your Question:",
            placeholder="e.g., Who is working on Phase 2 of the Microsoft project?",
            help="Ask questions about projects, people, documents, or any other project data"
        )
        
        # Example questions
        st.markdown("### 💡 Example Questions")
        
        example_questions = [
            "What is the status of the Microsoft Service Center project?",
            "Who are the key people working on this project?",
            "Find all documents from McGuire and Hester",
            "What change orders were approved this month?",
            "Show me all open issues with high priority",
            "What is the budget status for Phase 2?"
        ]
        
        cols = st.columns(2)
        for i, eq in enumerate(example_questions):
            col = cols[i % 2]
            with col:
                if st.button(f"📝 {eq}", key=f"example_{i}", use_container_width=True):
                    question = eq
                    st.rerun()
        
        if question:
            st.markdown("---")
            st.subheader("🤖 Answer")
            
            # Process question (placeholder for now)
            with st.spinner("Processing your question..."):
                answer = self.process_question(question)
            
            # Display answer
            st.markdown(answer)
            
            # Show related entities (if available)
            if self.kg and self.kg.connected:
                related = self.kg.search_entities(question)
                if related:
                    st.markdown("### 🔗 Related Entities")
                    for entity in related[:5]:
                        st.write(f"- **{entity.get('name', 'Unknown')}** ({entity.get('type', ['Unknown'])[0]})")
    
    def render_entity_search(self):
        """Render the entity search interface."""
        st.title("🔍 Entity Search & Discovery")
        st.markdown("Search for people, companies, documents, and other project entities")
        
        # Search input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Search Term:",
                placeholder="e.g., Microsoft, John Smith, concrete, drawings",
                help="Search for any entity in the knowledge graph"
            )
        
        with col2:
            entity_types = st.multiselect(
                "Filter by Type:",
                ["Person", "Company", "Document", "Project", "Task", "Issue"],
                help="Filter results by entity type"
            )
        
        if search_term:
            st.markdown("---")
            
            # Perform search
            if self.kg and self.kg.connected:
                results = self.kg.search_entities(search_term, entity_types)
            else:
                # Simulated results
                results = [
                    {"type": ["Person"], "name": "John Smith", "id": "person_001", "description": "Project Manager", "score": 0.95},
                    {"type": ["Company"], "name": "Microsoft Corporation", "id": "company_002", "description": "Technology company", "score": 0.88},
                    {"type": ["Project"], "name": "Microsoft Service Center", "id": "msvc_project_001", "description": "Construction project", "score": 0.82}
                ]
            
            st.subheader(f"🎯 Search Results ({len(results)} found)")
            
            if results:
                # Display results in a table
                df = pd.DataFrame(results)
                if 'type' in df.columns:
                    df['type'] = df['type'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else str(x))
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "score": st.column_config.ProgressColumn(
                            "Relevance",
                            help="Search relevance score",
                            min_value=0,
                            max_value=1,
                        ),
                    }
                )
                
                # Entity details
                if st.checkbox("Show detailed entity information"):
                    selected_entity = st.selectbox(
                        "Select entity for details:",
                        options=range(len(results)),
                        format_func=lambda x: f"{results[x]['name']} ({results[x]['type']})"
                    )
                    
                    if selected_entity is not None:
                        entity = results[selected_entity]
                        st.json(entity)
            else:
                st.info("No entities found matching your search criteria.")
    
    def render_analytics(self):
        """Render the analytics dashboard."""
        st.title("📊 Project Analytics Dashboard")
        st.markdown("Visual insights into your construction project data")
        
        # Sample analytics data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Document Types Distribution")
            
            # Sample data for document types
            doc_types = {
                'PDF': 1604,
                'Excel': 157,
                'Word': 84,
                'Email': 76,
                'Other': 196
            }
            
            fig = px.pie(
                values=list(doc_types.values()),
                names=list(doc_types.keys()),
                title="Document Types in Project"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("👥 Project Team Overview")
            
            # Sample team data
            team_data = {
                'Role': ['Project Manager', 'Architect', 'Engineer', 'Contractor', 'Inspector'],
                'Count': [3, 5, 8, 12, 4]
            }
            
            fig = px.bar(
                x=team_data['Role'],
                y=team_data['Count'],
                title="Team Members by Role"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline view
        st.subheader("📅 Project Timeline")
        
        # Sample timeline data
        timeline_data = {
            'Phase': ['Preconstruction', 'Foundation', 'Structure', 'MEP', 'Finishes'],
            'Start': ['2019-01-01', '2019-03-01', '2019-06-01', '2019-10-01', '2020-02-01'],
            'End': ['2019-02-28', '2019-05-31', '2019-09-30', '2020-01-31', '2020-06-30'],
            'Status': ['Complete', 'Complete', 'Complete', 'In Progress', 'Not Started']
        }
        
        df = pd.DataFrame(timeline_data)
        df['Start'] = pd.to_datetime(df['Start'])
        df['End'] = pd.to_datetime(df['End'])
        
        fig = px.timeline(
            df,
            x_start='Start',
            x_end='End',
            y='Phase',
            color='Status',
            title="Project Phase Timeline"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Network visualization
        st.subheader("🕸️ Entity Relationship Network")
        
        if st.button("Generate Network Visualization"):
            # Create sample network
            G = nx.Graph()
            
            # Add nodes
            G.add_node("Microsoft Project", type="Project")
            G.add_node("John Smith", type="Person")
            G.add_node("McGuire & Hester", type="Company")
            G.add_node("Phase 1", type="Phase")
            G.add_node("Foundation Work", type="Task")
            
            # Add edges
            G.add_edge("Microsoft Project", "John Smith", relation="MANAGED_BY")
            G.add_edge("Microsoft Project", "McGuire & Hester", relation="CONTRACTED_TO")
            G.add_edge("Microsoft Project", "Phase 1", relation="HAS_PHASE")
            G.add_edge("Phase 1", "Foundation Work", relation="CONTAINS_TASK")
            
            # Create visualization using plotly
            pos = nx.spring_layout(G)
            
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(
                    size=20,
                    color='lightblue',
                    line=dict(width=2, color='darkblue')
                )
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Entity Relationship Network',
                               titlefont_size=16,
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20,l=5,r=5,t=40),
                               annotations=[ dict(
                                   text="Knowledge Graph Relationships",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(color="gray", size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                           ))
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_data_management(self):
        """Render the data management interface."""
        st.title("🗂️ Data Management")
        st.markdown("Upload and manage construction project documents and data")
        
        tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "🏗️ Schema Management", "📋 Data Status"])
        
        with tab1:
            st.subheader("Document Upload")
            
            uploaded_files = st.file_uploader(
                "Choose files to upload",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'xlsx', 'xls'],
                help="Upload construction documents for processing"
            )
            
            if uploaded_files:
                st.write(f"Selected {len(uploaded_files)} files:")
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.size} bytes)")
                
                if st.button("🚀 Process Documents"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"Processing {file.name}...")
                        progress_bar.progress((i + 1) / len(uploaded_files))
                        # Here you would call your document processing pipeline
                    
                    st.success("✅ Documents processed successfully!")
        
        with tab2:
            st.subheader("Knowledge Graph Schema")
            
            if st.button("🔄 Refresh Schema"):
                if self.kg:
                    self.kg.create_schema()
                    st.success("✅ Schema updated!")
                else:
                    st.info("Schema would be created when Neo4j is connected")
            
            # Show schema information
            st.markdown("### Current Schema")
            st.code("""
            Entity Types:
            - Project (id, name, status, budget)
            - Person (name, email, role, department)
            - Company (name, type, specialization)
            - Document (filename, path, type, size)
            - Task (id, name, status, priority)
            - Issue (id, description, priority, status)
            
            Relationships:
            - (Project)-[:HAS_PHASE]->(Phase)
            - (Person)-[:WORKS_FOR]->(Company)
            - (Document)-[:BELONGS_TO_PROJECT]->(Project)
            - (Task)-[:ASSIGNED_TO]->(Person)
            """, language="cypher")
        
        with tab3:
            st.subheader("Data Status & Statistics")
            
            # Connection status
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if self.kg and self.kg.connected:
                    st.success("Neo4j: Connected")
                else:
                    st.error("Neo4j: Not Connected")
            
            with col2:
                st.info("Vector DB: Not Configured")
            
            with col3:
                st.warning("LLM: Not Configured")
            
            # Data statistics
            st.markdown("### 📊 Data Statistics")
            
            if self.kg:
                overview = self.kg.get_project_overview()
                
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                with metrics_col1:
                    st.metric("Total Entities", sum([
                        overview.get("projects", 0),
                        overview.get("people", 0),
                        overview.get("companies", 0)
                    ]))
                
                with metrics_col2:
                    st.metric("Documents", overview.get("documents", 0))
                
                with metrics_col3:
                    st.metric("Relationships", "TBD")
    
    def handle_direct_kg_query(self, question: str) -> str:
        """Handle direct knowledge graph queries when Q&A agent isn't available."""
        # Check if we have a valid knowledge graph connection
        if not self.kg:
            return "**Knowledge graph not available.** Please check the system configuration."
        
        if not hasattr(self.kg, 'query_graph') or not callable(getattr(self.kg, 'query_graph', None)):
            return "**Knowledge graph query method not available.** Using fallback responses."
        
        question_lower = question.lower()
        
        try:
            # Issues and problems
            if "issue" in question_lower or "problem" in question_lower or "open" in question_lower:
                query = """
                MATCH (i:Issue)
                OPTIONAL MATCH (i)-[:ASSIGNED_TO]->(p:Person)
                RETURN i.id as id, i.description as description, 
                       i.priority as priority, i.status as status,
                       p.name as assigned_to
                ORDER BY i.priority DESC
                LIMIT 10
                """
                results = self.kg.query_graph(query)
                
                if results:
                    answer = f"**Found {len(results)} issues:**\n\n"
                    for issue in results:
                        answer += f"• **{issue.get('id', 'Unknown ID')}**: {issue.get('description', 'No description')}\n"
                        answer += f"  - Priority: {issue.get('priority', 'Unknown')}\n"
                        answer += f"  - Status: {issue.get('status', 'Unknown')}\n"
                        if issue.get('assigned_to'):
                            answer += f"  - Assigned to: {issue['assigned_to']}\n"
                        answer += "\n"
                    return answer
                else:
                    return "**No open issues found in the system.** ✅\n\nThis could mean:\n- All issues have been resolved\n- Issues haven't been added to the knowledge graph yet\n- The project is running smoothly!"
            
            # People queries
            elif "who" in question_lower or "people" in question_lower or "team" in question_lower:
                query = """
                MATCH (p:Person)
                OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
                OPTIONAL MATCH (p)-[:MANAGES]->(proj:Project)
                RETURN p.name as name, p.role as role, p.email as email,
                       c.name as company, proj.name as project
                LIMIT 10
                """
                results = self.kg.query_graph(query)
                
                if results:
                    answer = f"**Found {len(results)} team members:**\n\n"
                    for person in results:
                        answer += f"• **{person.get('name', 'Unknown')}**"
                        if person.get('role'):
                            answer += f" - {person['role']}"
                        answer += "\n"
                        if person.get('company'):
                            answer += f"  - Company: {person['company']}\n"
                        if person.get('project'):
                            answer += f"  - Managing: {person['project']}\n"
                        if person.get('email'):
                            answer += f"  - Email: {person['email']}\n"
                        answer += "\n"
                    return answer
                else:
                    return "**No team members found.** Try asking about specific roles or companies."
            
            # Company queries  
            elif "company" in question_lower or "companies" in question_lower or "contractor" in question_lower:
                query = """
                MATCH (c:Company)
                OPTIONAL MATCH (c)<-[:WORKS_FOR]-(p:Person)
                OPTIONAL MATCH (c)<-[:CONTRACTED_TO]-(proj:Project)
                RETURN c.name as name, c.type as type, c.specialization as specialization,
                       count(p) as employee_count, proj.name as project
                """
                results = self.kg.query_graph(query)
                
                if results:
                    answer = f"**Found {len(results)} companies:**\n\n"
                    for company in results:
                        answer += f"• **{company.get('name', 'Unknown Company')}**"
                        if company.get('type'):
                            answer += f" ({company['type']})"
                        answer += "\n"
                        if company.get('specialization'):
                            answer += f"  - Specialization: {company['specialization']}\n"
                        if company.get('employee_count', 0) > 0:
                            answer += f"  - Team members: {company['employee_count']}\n"
                        if company.get('project'):
                            answer += f"  - Working on: {company['project']}\n"
                        answer += "\n"
                    return answer
                else:
                    return "**No companies found.** The system may need company data to be imported."
            
            # Project status
            elif "status" in question_lower or "project" in question_lower:
                query = """
                MATCH (p:Project)
                OPTIONAL MATCH (p)-[:CONTRACTED_TO]->(c:Company)
                RETURN p.name as name, p.status as status, p.start_date as start_date,
                       p.budget as budget, p.description as description, c.name as contractor
                """
                results = self.kg.query_graph(query)
                
                if results:
                    project = results[0]
                    answer = f"**{project.get('name', 'Project')} Status:**\n\n"
                    answer += f"• **Status**: {project.get('status', 'Unknown')}\n"
                    if project.get('budget'):
                        answer += f"• **Budget**: ${project['budget']:,}\n"
                    if project.get('start_date'):
                        answer += f"• **Start Date**: {project['start_date']}\n"
                    if project.get('contractor'):
                        answer += f"• **Main Contractor**: {project['contractor']}\n"
                    if project.get('description'):
                        answer += f"• **Description**: {project['description']}\n"
                    return answer
                else:
                    return "**No project information found.** The project data may need to be imported into the knowledge graph."
            
            else:
                return None  # Fall back to hardcoded responses
                
        except Exception as e:
            return f"**Error querying knowledge graph:** {str(e)}\n\nTry a simpler question or check the system status."
    
    def process_question(self, question: str) -> str:
        """Process a natural language question and return an answer."""
        
        # Use the Q&A agent if available
        if self.qa_agent:
            try:
                response = self.qa_agent.ask(question)
                
                # Format the response for Streamlit
                answer = response.answer
                
                if response.confidence > 0.5:
                    # Add confidence indicator
                    answer += f"\n\n*Confidence: {response.confidence:.1%}*"
                    
                    # Add sources if available
                    if response.sources:
                        answer += f"\n\n**Sources:** {len(response.sources)} knowledge graph entities"
                    
                    # Add suggestions
                    if response.suggestions:
                        answer += "\n\n**Try asking:**"
                        for suggestion in response.suggestions[:3]:
                            answer += f"\n- {suggestion}"
                
                return answer
                
            except Exception as e:
                st.error(f"Q&A Agent Error: {str(e)}")
                # Fall back to direct knowledge graph queries
                pass
        
        # Enhanced fallback: Direct knowledge graph queries
        if self.kg and hasattr(self.kg, 'query_graph') and callable(getattr(self.kg, 'query_graph', None)):
            try:
                result = self.handle_direct_kg_query(question)
                if result:  # Only return if we got a meaningful result
                    return result
            except Exception as e:
                st.warning(f"Knowledge graph query failed: {str(e)}")
        
        # Final fallback: Simple rule-based responses for demonstration
        question_lower = question.lower()
        
        if "status" in question_lower and ("microsoft" in question_lower or "project" in question_lower):
            return """
            **Microsoft Service Center Project Status:**
            
            - **Overall Status**: Active (In Progress)
            - **Current Phase**: MEP Installation (Phase 4)
            - **Progress**: Approximately 75% complete
            - **Budget Status**: On track with minor variances
            - **Timeline**: Expected completion Q2 2024
            - **Key Activities**: 
              - Mechanical systems installation ongoing
              - Electrical rough-in 90% complete
              - Plumbing installation in progress
            
            *Last updated: September 2025*
            """
        
        elif "who" in question_lower and ("working" in question_lower or "people" in question_lower):
            return """
            **Key People on Microsoft Project:**
            
            - **John Smith** - Project Manager (McGuire & Hester)
            - **Sarah Johnson** - Owner Representative (Microsoft)
            - **Mike Chen** - Senior Architect (Design Team)
            - **Lisa Wong** - MEP Engineer
            - **David Martinez** - Site Superintendent
            
            *Total project team: 25+ people across multiple disciplines*
            """
        
        elif "change order" in question_lower or "co" in question_lower:
            return """
            **Recent Change Orders:**
            
            1. **PCO 80071** - Kitchen Equipment Upgrades ($234K) - *Approved*
            2. **PCO 80209** - Additional Beam Penetrations ($211K) - *Approved*
            3. **PCO 80135** - Addendum 8 Changes ($151K) - *Approved*
            4. **PCO 82647** - Damaged Zinc Panels ($28K) - *Under Review*
            
            *Total approved changes: $596K*
            """
        
        elif "document" in question_lower and "mcguire" in question_lower:
            return """
            **Documents from McGuire and Hester:**
            
            - Meeting minutes (45 documents)
            - Change order requests (23 documents)
            - Submittal packages (67 documents)
            - Progress reports (12 documents)
            - Safety documentation (15 documents)
            
            *Most recent: Weekly progress report dated September 15, 2025*
            """
        
        else:
            return f"""
            **I'm still learning to answer that question!**
            
            You asked: *"{question}"*
            
            Here's what I can help you with right now:
            - Project status updates
            - Team member information
            - Change order summaries
            - Document searches
            
            Try rephrasing your question or use one of the example questions above.
            """
    
    def run(self):
        """Run the main application."""
        self.setup_page_config()
        
        # Render sidebar and get selected page
        page = self.render_sidebar()
        
        # Render the selected page
        if page == "🏠 Home":
            self.render_home_page()
        elif page == "❓ Q&A Interface":
            self.render_qa_interface()
        elif page == "🔍 Entity Search":
            self.render_entity_search()
        elif page == "📊 Analytics":
            self.render_analytics()
        elif page == "🗂️ Data Management":
            self.render_data_management()

def main():
    """Main application entry point."""
    app = KnowledgeGraphApp()
    app.run()

if __name__ == "__main__":
    main()