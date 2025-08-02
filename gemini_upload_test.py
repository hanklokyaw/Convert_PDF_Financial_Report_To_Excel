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

Please extract the full Income Statement from the document.

Instructions:
1. Detect and return the unit of measurement (e.g., "USD", "USD in thousands", or "USD in millions") in a top-level field called `unit`. This is for informational purposes only.
2. Regardless of unit, return **fully scaled numeric values** (e.g., 249625000).
3. Return the Income Statement as a list of dictionaries, one row per metric, under the key `"Income Statement"`.
4. Sort the years in descending order (e.g., "2024", "2023", "2022").
5. If any additional line items not included in the template appear in the financial statement, insert them into the appropriate logical position.
6. Output must be **strictly valid JSON**, with no markdown or explanation.

Example format:

{
  "Income Statement": [
    { "Metric": "Revenue", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Cost of Goods Sold (COGS)", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Gross Profit", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Operating Expenses", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Selling, General & Admin (SG&A)", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Research & Development (R&D)", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Operating Income", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Interest Income", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Interest Expense", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Other Income (Expense), net", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Income Before Tax", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Income Tax Expense", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Net Income", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Net Income Attributable to Non-Controlling Interest", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Net Income Attributable to Parent", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Earnings Per Share (EPS) - Basic", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Earnings Per Share (EPS) - Diluted", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Weighted Average Shares Outstanding - Basic", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Weighted Average Shares Outstanding - Diluted", "2022": "", "2023": "", "2024": "" }
  ]
}

⚠️ Do not explain anything. Return only valid JSON.

Return **only valid JSON** and **do not add explanations**.

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
            if isinstance(section_data, list):
                try:
                    df = pd.DataFrame(section_data)
                    if not df.empty:
                        # Insert unit as header
                        unit = json_data.get("unit", "")
                        unit_row = pd.DataFrame([[unit] + [""] * (df.shape[1] - 1)], columns=df.columns)
                        df = pd.concat([unit_row, df], ignore_index=True)

                    df.to_excel(writer, sheet_name=section_name[:31], index=False)
                except Exception as e:
                    print(f"⚠️ Could not write sheet '{section_name}': {e}")
            else:
                print(f"ℹ️ Skipping non-table key: '{section_name}'")
    output.seek(0)
    with open(filename, "wb") as f:
        f.write(output.read())
    print(f"📁 Excel saved to: {filename}")
    return output


# ---------- Extract and display unit ----------
unit = json_data.get("unit", "USD")  # Default fallback
print(f"\n📐 Unit of Measurement: {unit}")


create_excel_dynamic(json_data)
