import tempfile
import os
from pdf2markdown4llm import PDF2Markdown4LLM

def convert_pdf_to_md(pdf_bytes: bytes, original_filename: str) -> (bytes, str):
    """
    Converts PDF bytes to Markdown using docling and returns the markdown content and filename.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name
        tmp_pdf.write(pdf_bytes)

    try:
        converter = PDF2Markdown4LLM(remove_headers=False, skip_empty_tables=True, table_header="### Table")
        md_content = converter.convert(pdf_path)
        md_dir = "ProcessedFolder/md_files"
        if not os.path.exists(md_dir):
            os.makedirs(md_dir)
        md_filename = os.path.splitext(os.path.basename(original_filename))[0] + ".md"
        md_file_path = os.path.join(md_dir, md_filename)
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
        return md_content.encode("utf-8"), md_file_path
    except Exception as e:
        raise RuntimeError(f"Error converting PDF to Markdown: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)