# --- Imports ---
import csv
import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
try:
    from pdf_to_md import convert_pdf_to_md
    PDF2MD_AVAILABLE = True
except ImportError:
    PDF2MD_AVAILABLE = False
from llm_summary_utils import generate_summary
from visual_utils import DescribeConfig, describe_visual_file

# --- Constants ---
CSV_PATH = "DocLabs_Sample_Project_Template/file_inventory_Project_Information_only.csv"
OUTPUT_CSV_PATH = "file_inventory_with_llm_summaries.csv"
FOLDER_FILTER = "01. Project Information"


# --- Main logic ---
def main():
    from split_pdf_to_pages import split_pdfs_and_write_csv
    output_csv = OUTPUT_CSV_PATH
    output_dir = "ProcessedFolder/PDF_Pages"
    split_pdfs_and_write_csv(CSV_PATH, output_csv, output_dir, max_pdfs=8)


    # Read, process, and update CSV with Markdown columns
    updated_rows = []
    with open(output_csv, newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["md_text", "md_filename"] if "md_text" not in reader.fieldnames else reader.fieldnames
        for row in reader:
            page_pdf_path = row.get("page_pdf_path")
            print(f"Processing: {page_pdf_path}")
            if not page_pdf_path or not os.path.exists(page_pdf_path):
                print(f"PDF page not found: {page_pdf_path}")
                row["md_text"] = ""
                row["md_filename"] = ""
                updated_rows.append(row)
                continue
            try:
                with open(page_pdf_path, "rb") as pdf_f:
                    pdf_bytes = pdf_f.read()
                md_bytes, md_filename = convert_pdf_to_md(pdf_bytes, os.path.basename(page_pdf_path))
                md_text = md_bytes.decode("utf-8")
                # Save markdown file
                md_dir = "ProcessedFolder/md_files"
                if not os.path.exists(md_dir):
                    os.makedirs(md_dir)
                md_file_path = os.path.join(md_dir, os.path.splitext(os.path.basename(page_pdf_path))[0] + ".md")
                with open(md_file_path, "w", encoding="utf-8") as md_f:
                    md_f.write(md_text)
                row["md_text"] = md_text[:8000]
                row["md_filename"] = md_file_path
            except Exception as e:
                row["md_text"] = f"[Markdown extraction error: {e}]"
                row["md_filename"] = ""
            updated_rows.append(row)

    # Write updated rows back to CSV
    with open(output_csv, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in updated_rows:
            writer.writerow(row)

if __name__ == "__main__":
    main()



