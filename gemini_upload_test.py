import os
import time
import json
import re
import pandas as pd
from io import BytesIO
from typing import List, Optional
from google import genai
from google.genai.types import Part
from pydantic import BaseModel

# ---------- Models ----------
class Record(BaseModel):
    Field: str
    Value: Optional[str]

    def dict(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        d["Value"] = d["Value"] or ""  # Convert None to empty string for Excel
        return d

class DocumentOutput(BaseModel):
    income_statement: List[Record] = []
    balance_sheet: List[Record] = []
    cash_flow: List[Record] = []

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
You are a professional finance expert.
Help me to extract full financial statement from the report:
- Income Statement
- Balance Sheet (Field, Value)
- Cash Flow (Field, Value)

Return ONLY valid JSON in this format:
{
  "Income Statement": [{"Field":"...","Value":"..."}],
  "Balance Sheet": [{"Field":"...","Value":"..."}],
  "Cash Flow": [{"Field":"...","Value":"..."}]
}"""
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

def extract_json_from_markdown(text: str) -> str:
    """Extract JSON from code block if Gemini returns markdown"""
    if text.startswith("```json") or text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text.strip())
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

# ---------- Parse JSON ----------
if not result_text:
    raise RuntimeError("❌ No response from Gemini.")

try:
    # Clean markdown-style JSON formatting
    cleaned = extract_json_from_markdown(result_text)

    json_data = json.loads(cleaned)
    output_data = DocumentOutput(
        income_statement=[Record(**r) for r in json_data.get("Income Statement", [])],
        balance_sheet=[Record(**r) for r in json_data.get("Balance Sheet", [])],
        cash_flow=[Record(**r) for r in json_data.get("Cash Flow", [])]
    )
except json.JSONDecodeError as e:
    print("❌ JSON decode failed:", str(e))
    print("Raw cleaned response:\n", cleaned)
    raise
except Exception as e:
    print("❌ Parsing or validation error:", str(e))
    raise

# ---------- Write to Excel ----------
def create_excel(data: DocumentOutput, filename: str = "financial_data.xlsx") -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if data.income_statement:
            pd.DataFrame([r.dict() for r in data.income_statement]).to_excel(
                writer, sheet_name="Income Statement", index=False)
        if data.balance_sheet:
            pd.DataFrame([r.dict() for r in data.balance_sheet]).to_excel(
                writer, sheet_name="Balance Sheet", index=False)
        if data.cash_flow:
            pd.DataFrame([r.dict() for r in data.cash_flow]).to_excel(
                writer, sheet_name="Cash Flow", index=False)
    output.seek(0)
    with open(filename, "wb") as f:
        f.write(output.read())
    print(f"📁 Excel saved to: {filename}")
    return output

create_excel(output_data)
