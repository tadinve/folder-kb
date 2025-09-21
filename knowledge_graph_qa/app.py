"""
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
