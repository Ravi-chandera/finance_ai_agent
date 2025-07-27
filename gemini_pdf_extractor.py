from google import genai
from google.genai import types
import pathlib
import httpx
import pathlib

client = genai.Client(api_key="AIzaSyCAaYSZdgeGrhEYK9ycITfR6VPNK56ykDc")

# Retrieve and encode the PDF byte
def extract_pdf_to_text_using_gemini(pdf_path, output_file):
    filepath = pathlib.Path(pdf_path)
    prompt = "Extract all the details from pdf for LLM readable format. Return only the text and nothing else. for tables you can decide better choice of what will best suit the LLM"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ]
    )
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(response.text)
        f.write("\n")  # Optionally add a newline after each extraction
    print("Text from finance pdf is extracted successfully")

# Example usage:
# extract_pdf_to_text(r"C:\2025-stuff\finance_ai_agent\Consolidated and Standalone tcs.pdf", "extracted_text.txt")