import os
from typing import Dict, Any, List
import json

# Example: OpenAI API (can be swapped for Anthropic, HuggingFace, etc.)
try:
    import openai
except ImportError:
    openai = None

LLM_PROMPT = '''
You are an expert construction project knowledge graph builder.
Given the following document text, extract all entities and relationships relevant to construction projects.

Return your answer as a JSON object with the following structure:
{{
    "projects": [ {{ ... }} ],
    "people": [ {{ ... }} ],
    "companies": [ {{ ... }} ],
    "documents": [ {{ ... }} ],
    "tasks": [ {{ ... }} ],
    "issues": [ {{ ... }} ],
    "relationships": [ {{ "source": ..., "target": ..., "type": ... }} ]
}}

Document text:
"""
{document_text}
"""
'''

def extract_entities_with_llm(document_text: str, model: str = "gpt-3.5-turbo", api_key: str = None) -> Dict[str, Any]:
    """
    Use an LLM to extract entities and relationships from document text.
    Returns a dict with keys: projects, people, companies, documents, tasks, issues, relationships
    """
    if not openai:
        raise ImportError("openai package not installed")
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not set")
    prompt = LLM_PROMPT.format(document_text=document_text[:4000])  # Truncate for token limit
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=2048
    )
    content = response.choices[0].message.content
    # Try to parse the first code block as JSON
    try:
        # Extract JSON from markdown/code block if present
        if '```' in content:
            content = content.split('```')[1]
        data = json.loads(content)
    except Exception:
        # Fallback: try to parse as is
        data = json.loads(content)
    return data
