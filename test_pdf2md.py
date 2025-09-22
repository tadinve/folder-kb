import sys
from pdf_to_md import convert_pdf_to_md

if __name__ == "__main__":
    pdf_path = "DocLabs_Sample_Project_Template/01. Project Information/BW Tank Fencing and Disconnect/Transmittal_SupplementalInstruction - SI-186 (Sent and Closed).pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    md_bytes, md_filename = convert_pdf_to_md(pdf_bytes, pdf_path)
    print(f"Markdown output written to: {md_filename}")
    print("\n--- Markdown Preview (first 500 chars) ---\n")
    print(md_bytes.decode("utf-8")[:500])
