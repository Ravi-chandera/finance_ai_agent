# import fitz

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text

# pdf_text = extract_text_from_pdf(r"C:\2025-stuff\finance_ai_agent\Transcript of the Q1 2024-25 Earnings Conference Call held on Jul 11, 2024.pdf")
# print(pdf_text)

import pdfplumber

def extract_text_from_meeting_transcriptions(pdf_path, output_txt_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    with open(output_txt_path, "a", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")  # Optionally add a newline after each extraction
    print(f"Text from {pdf_path} has been appended to {output_txt_path}")

# text = extract_text_pdfplumber(r"C:\2025-stuff\finance_ai_agent\Transcript of the Q1 2024-25 Earnings Conference Call held on Jul 11, 2024.pdf")
# print(text)
