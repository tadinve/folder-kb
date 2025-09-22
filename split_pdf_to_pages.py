import csv

def split_pdfs_and_write_csv(csv_path, output_csv, output_dir, max_pdfs=8):
    """
    For each PDF in the input CSV (up to max_pdfs), split into single-page PDFs and write one row per page to output_csv.
    Adds columns: page_number, page_pdf_path
    """
    with open(csv_path, newline='') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["page_number", "page_pdf_path", "exceptions"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        pdf_count = 0
        for row in reader:
            if row.get("file_type", "").lower() == "pdf":
                # Determine full path to PDF
                dir_part = row["directory"].lstrip("/")
                if dir_part.startswith("/Users/"):
                    full_path = os.path.join(dir_part, row["filename"])
                elif dir_part.startswith("Users/"):
                    full_path = os.path.join("/" + dir_part, row["filename"])
                elif dir_part.startswith("DocLabs_Sample_Project_Template/"):
                    full_path = os.path.join(dir_part, row["filename"])
                else:
                    full_path = os.path.join("DocLabs_Sample_Project_Template", dir_part, row["filename"])
                # Split PDF into pages
                page_paths = split_pdf_to_pages(full_path, output_dir)
                max_pages = 5
                total_pages = len(page_paths)
                for i, page_path in enumerate(page_paths[:max_pages]):
                    row_out = dict(row)
                    row_out["page_number"] = i + 1
                    row_out["page_pdf_path"] = page_path
                    if total_pages > max_pages:
                        row_out["exceptions"] = f"Only processed 5 out of {total_pages} pages."
                    else:
                        row_out["exceptions"] = ""
                    writer.writerow(row_out)
                pdf_count += 1
                if pdf_count >= max_pdfs:
                    break
import os
import PyPDF2

def split_pdf_to_pages(pdf_path, output_dir):
    """
    Splits a PDF into single-page PDFs and saves them in output_dir.
    Each page is saved as <original_filename>_page<N>.pdf
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    page_paths = []
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(page)
                out_path = os.path.join(output_dir, f"{base_name}_page{i+1}.pdf")
                with open(out_path, 'wb') as out_f:
                    pdf_writer.write(out_f)
                page_paths.append(out_path)
    except Exception as e:
        print(f"[split_pdf_to_pages ERROR] {pdf_path}: {e}")
    return page_paths

if __name__ == "__main__":
    # Example usage
    pdf_path = "DocLabs_Sample_Project_Template/01. Project Information/BW Tank Fencing and Disconnect/Transmittal_SupplementalInstruction - SI-186 (Sent and Closed).pdf"
    output_dir = "ProcessedFolder/PDF_Pages"
    split_pdf_to_pages(pdf_path, output_dir)
