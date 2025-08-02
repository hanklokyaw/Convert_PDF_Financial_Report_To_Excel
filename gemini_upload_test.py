import os
import time
import json
import re
import pandas as pd
from io import BytesIO
from typing import Dict, Any
from google import genai
from google.genai.types import Part

# ---------- Config ----------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY environment variable must be set.")

client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash"

# ---------- Upload PDF ----------
pdf_path = "input/sample_financial_report_COST-2024.pdf"
assert os.path.exists(pdf_path), f"❌ File not found: {pdf_path}"

print(f"📤 Uploading PDF: {pdf_path}")
uploaded_pdf = client.files.upload(
    path=pdf_path,
    config={"mime_type": "application/pdf"}
)
print(f"✅ Uploaded: name={uploaded_pdf.name}, uri={uploaded_pdf.uri}")

# ---------- Wait for processing ----------
while uploaded_pdf.state == "PROCESSING":
    print("⏳ Waiting for file to finish processing...")
    time.sleep(2)
    uploaded_pdf = client.files.get(name=uploaded_pdf.name)

print(f"✅ File state: {uploaded_pdf.state}")

# ---------- Send Prompt to Gemini ----------
def extract_financial_data(pdf_part):
    prompt = """
You are a professional financial analyst.
Extract the full Income Statement from the financial report.

Return it in **valid JSON** as a list of dictionaries like this:

{
  "Income Statement": [
    {"Metric": "Revenue", "2022": "10000", "2023": "11000"},
    {"Metric": "COGS", "2022": "4000", "2023": "4500"},
    {"Metric": "Gross Profit", "2022": "6000", "2023": "6500"},
    ...
  ]
}

⚠️ Return only valid JSON. Do not explain anything.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pdf_part],
        )
        return response.text
    except Exception as e:
        print(f"❌ API error: {e}")
        return None

# Convert to Part
pdf_part = Part.from_uri(
    file_uri=uploaded_pdf.uri,
    mime_type="application/pdf"
)

result_text = extract_financial_data(pdf_part)

# ---------- Clean and Parse JSON ----------
def extract_json_from_markdown(text: str) -> str:
    if text.startswith("```json") or text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text.strip())
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

if not result_text:
    raise RuntimeError("❌ No response from Gemini.")

try:
    cleaned = extract_json_from_markdown(result_text)
    json_data: Dict[str, Any] = json.loads(cleaned)
except json.JSONDecodeError as e:
    print("❌ JSON decode failed:", str(e))
    print("Raw cleaned response:\n", cleaned)
    raise

# ---------- Convert to DataFrame ----------
df_income = pd.DataFrame(json_data.get("Income Statement", []))
print("\n📊 Income Statement Preview:")
print(df_income.head())

# ---------- Write to Excel ----------
def create_excel_dynamic(json_data: Dict[str, Any], filename: str = "financial_data_dynamic.xlsx") -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for section_name, section_data in json_data.items():
            try:
                df = pd.DataFrame(section_data)
                df.to_excel(writer, sheet_name=section_name[:31], index=False)  # Max 31 chars
            except Exception as e:
                print(f"⚠️ Could not write sheet '{section_name}': {e}")
    output.seek(0)
    with open(filename, "wb") as f:
        f.write(output.read())
    print(f"📁 Excel saved to: {filename}")
    return output

create_excel_dynamic(json_data)
