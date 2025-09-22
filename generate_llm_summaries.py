import csv
import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract

# Use custom pdf_to_md.py logic for Markdown extraction
try:
    from pdf_to_md import convert_pdf_to_md
    PDF2MD_AVAILABLE = True
except ImportError:
    PDF2MD_AVAILABLE = False

# Dummy stubs for missing functions/classes (replace with real implementations as needed)
import openai
import time

def generate_summary(row):
    """
    Calls OpenAI API to generate a 300-500 word summary for the given file/page content.
    Returns the summary or an error message.
    """
    prompt = (
        "You are an expert construction project analyst. "
        "Summarize the following document page for a project knowledge graph. "
        "Write a clear, detailed, 300-500 word summary in professional English. "
        "Focus on key topics, entities, and any important context.\n\n"
        "Also, based on the content, classify the business type of this page as one of: 'drawing-or-map', 'financial-plan', 'schedule', 'correspondence', 'contract', 'administration', 'testing-inspection', 'closeout', or 'other'. "
        "At the end of your summary, add a line in the format: BUSINESS_TYPE: <type>\n"
        f"Document/Page Content:\n{row.get('file_content', '')}\n"
    )
    try:
        # For openai>=1.0.0
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        time.sleep(2)
        return f"LLM ERROR: {e}"

class DescribeConfig:
    def __init__(self, provider, max_pages, pdf_dpi):
        pass
def describe_visual_file(full_path, cfg, page_number=None):
    return [("Visual", "[Visual summary placeholder]")]

# Path and filter constants (set these to your actual values)
CSV_PATH = "DocLabs_Sample_Project_Template/file_inventory_Project_Information_only.csv"
OUTPUT_CSV_PATH = "file_inventory_with_llm_summaries.csv"
FOLDER_FILTER = "01. Project Information"
def write_project_info_csv(input_csv, output_csv, folder_filter):
    with open(input_csv, newline='') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if folder_filter in row["directory"]:
                writer.writerow(row)


import os
# ...existing code...
import csv
def main():
    print("Started execution of PDF page-level summarization...")
    with open(CSV_PATH, newline='') as infile, open(OUTPUT_CSV_PATH, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        original_fieldnames = reader.fieldnames
        fieldnames = original_fieldnames + ["page_number", "llm_summary", "exceptions", "business_type", "page_text", "page_text_md"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        pdf_count = 0
        for row in reader:
            exceptions = ""
            business_type = ""
            fname = row["filename"].lower()
            fdir = row["directory"].lower()
            ftype = row["file_type"].lower()
            if ftype != "pdf":
                continue
            if pdf_count >= 8:
                break
            # Heuristic for business type
            if any(x in fname for x in ["drawing", "plan", "map", "sketch"]) or "drawings" in fdir:
                business_type = "drawing-or-map"
            elif any(x in fname for x in ["estimate", "budget", "cost", "pricing", "financial", "audit"]) or "financial" in fdir or "billing" in fdir:
                business_type = "financial-plan"
            elif any(x in fname for x in ["schedule", "timeline", "gantt"]) or "schedule" in fdir:
                business_type = "schedule"
            # PDF processing block (for all business types)
            pdf_count += 1
            print(f"Processing PDF {pdf_count}: {row['filename']}")
            dir_part = row["directory"].lstrip("/")
            if dir_part.startswith("/Users/"):
                full_path = os.path.join(dir_part, row["filename"])
            elif dir_part.startswith("Users/"):
                full_path = os.path.join("/" + dir_part, row["filename"])
            elif dir_part.startswith("DocLabs_Sample_Project_Template/"):
                full_path = os.path.join(dir_part, row["filename"])
            else:
                full_path = os.path.join("DocLabs_Sample_Project_Template", dir_part, row["filename"])
            try:
                with open(full_path, 'rb') as f:
                    reader_pdf = PyPDF2.PdfReader(f)
                    num_pages = len(reader_pdf.pages)
                    max_pages = min(num_pages, 5)
                    # Always split into single-page PDFs and analyze each page
                    for page_idx in range(max_pages):
                        page_number = page_idx + 1
                        page = reader_pdf.pages[page_idx]
                        # Extract text
                        page_text = (page.extract_text() or "").replace('\n', ' ').replace('\r', ' ')
                        # Extract Markdown
                        if PDF2MD_AVAILABLE:
                            try:
                                import tempfile
                                pdf_writer = PyPDF2.PdfWriter()
                                pdf_writer.add_page(page)
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                                    pdf_writer.write(tmp_pdf)
                                    tmp_pdf_path = tmp_pdf.name
                                with open(tmp_pdf_path, "rb") as pdf_f:
                                    pdf_bytes = pdf_f.read()
                                os.remove(tmp_pdf_path)
                                md_bytes, md_filename = convert_pdf_to_md(pdf_bytes, f"{os.path.splitext(full_path)[0]}_page{page_number}.pdf")
                                page_text_md = md_bytes.decode("utf-8")[:8000]
                            except Exception as e:
                                page_text_md = f"[Markdown extraction error: {e}]"
                                print(f"pdf_to_md error: {e}")
                        else:
                            page_text_md = "[pdf_to_md not installed]"
                        summary = ""
                        exceptions = ""
                        business_type_out = business_type
                        # Summarize or OCR/visual fallback
                        if page_text and len(page_text.strip()) > 30:
                            row_for_prompt = dict(row)
                            row_for_prompt["file_content"] = page_text[:8000]
                            row_for_prompt["full_path"] = full_path
                            row_for_prompt["page_number"] = page_number
                            row_for_prompt.pop("created_date", None)
                            row_for_prompt.pop("modified_date", None)
                            print(f"Summarizing (text): {row['filename']} page {page_number}")
                            try:
                                summary = generate_summary(row_for_prompt)
                                # Extract business type from summary if present
                                business_type_out = ""
                                for line in summary.splitlines()[::-1]:
                                    if line.strip().upper().startswith("BUSINESS_TYPE:"):
                                        business_type_out = line.split(":",1)[-1].strip().lower()
                                        summary = summary.replace(line, "").strip()
                                        break
                                if not business_type_out:
                                    business_type_out = "other"
                            except Exception as e:
                                summary = f"LLM ERROR: {e}"
                                business_type_out = "other"
                            if page_text and len(page_text) == 8000:
                                exceptions = "Page content truncated due to LLM context length limit. Not all content analyzed."
                            print(f"\n--- LLM Summary for {row['filename']} page {page_number} ---\n{summary}\n")
                        else:
                            # Fallback: OCR or visual analysis
                            images = convert_from_path(full_path, dpi=300, first_page=page_number, last_page=page_number)
                            ocr_text = []
                            for img in images:
                                ocr_text.append(pytesseract.image_to_string(img))
                            ocr_result = " ".join(ocr_text).replace('\n', ' ').replace('\r', ' ').strip()
                            if ocr_result and len(ocr_result) > 30:
                                row_for_prompt = dict(row)
                                row_for_prompt["file_content"] = ocr_result[:8000]
                                row_for_prompt["full_path"] = full_path
                                row_for_prompt["page_number"] = page_number
                                row_for_prompt.pop("created_date", None)
                                row_for_prompt.pop("modified_date", None)
                                print(f"Summarizing (OCR): {row['filename']} page {page_number}")
                                try:
                                    summary = generate_summary(row_for_prompt)
                                except Exception as e:
                                    summary = f"LLM ERROR: {e}"
                                if len(ocr_result) == 8000:
                                    exceptions = "OCR page content truncated due to LLM context length limit. Not all content analyzed."
                                print(f"\n--- LLM OCR Summary for {row['filename']} page {page_number} ---\n{summary}\n")
                            else:
                                # Fallback: visual LLM
                                try:
                                    cfg = DescribeConfig(provider="openai", max_pages=1, pdf_dpi=200)
                                    visual_summaries = describe_visual_file(full_path, cfg, page_number=page_number)
                                    summary = "\n".join([f"[{label}] {desc}" for label, desc in visual_summaries])
                                    exceptions = "Page analyzed visually, not all content may be captured."
                                    print(f"\n--- Visual LLM Summary for {row['filename']} page {page_number} ---\n{summary}\n")
                                except Exception as e:
                                    summary = f"ERROR: Could not generate image summary for {row['filename']} page {page_number}: {e}"
                                    exceptions = f"Extraction error: {e}"
                                    print(f"\n--- Extraction Error for {row['filename']} page {page_number} ---\n{summary}\n")
                        row_out = dict(row)
                        row_out["page_number"] = page_number
                        row_out["llm_summary"] = summary
                        row_out["exceptions"] = exceptions
                        row_out["business_type"] = business_type_out
                        row_out["page_text"] = page_text[:1000]
                        row_out["page_text_md"] = page_text_md
                        writer.writerow(row_out)
            except Exception as e:
                print(f"[PDF Split Error] {row['filename']}: {e}")
        print(f"Finished execution. Processed {pdf_count} PDF files. Output written to {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    # Run the summary pipeline for the first 8 PDFs
    main()
    # If you want to create a CSV with only files from /01. Project Information, use the function below:
    # write_project_info_csv(
    #     CSV_PATH,
    #     "DocLabs_Sample_Project_Template/file_inventory_Project_Information_only.csv",
    #     FOLDER_FILTER
    # )
