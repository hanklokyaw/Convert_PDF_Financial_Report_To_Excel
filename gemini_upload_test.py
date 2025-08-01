import os
from google import genai
from google.genai.types import Part  # ✅ Needed for file part
from datetime import datetime

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY environment variable must be set.")

client = genai.Client(api_key=api_key)

pdf_path = "input/sample_financial_report_COST-2024.pdf"
assert os.path.exists(pdf_path), f"❌ File not found: {pdf_path}"

print(f"📤 Uploading PDF: {pdf_path}")
uploaded_pdf = client.files.upload(
    path=pdf_path,
    config={"mime_type": "application/pdf"}
)
print(f"✅ Uploaded: name={uploaded_pdf.name}, uri={uploaded_pdf.uri}")

# ✅ Convert to Part for model input
pdf_part = Part.from_uri(
    file_uri=uploaded_pdf.uri,
    mime_type="application/pdf"
)

prompt = "Give me a summary of this PDF file."
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[prompt, pdf_part],
)

print("\n=== Summary Response ===")
print(response.text)


