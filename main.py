# import requires libraries
import os
import time
import json
import re
import pandas as pd
from typing import Dict, Any
from google import genai
from google.genai.types import Part
from datetime import datetime
# import from functions.py
from functions import extract_income_statement, extract_balance_sheet, extract_cash_flow_statement

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY environment variable must be set.")

client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash"
log_file = "convert_pdf_log.txt"


def extract_json_from_markdown(text: str) -> str:
    if text.startswith("```json") or text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text.strip())
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalize_unit(unit_str: str) -> str:
    unit_str = unit_str.lower()
    if "million" in unit_str:
        return "millions"
    elif "thousand" in unit_str:
        return "thousands"
    elif "billion" in unit_str:
        return "billions"
    else:
        return unit_str


def create_excel_dynamic(json_data: Dict[str, Any], input_path: str) -> str:
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"{base_name}.xlsx")

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for section_name, section_data in json_data.items():
            if isinstance(section_data, list):
                try:
                    df = pd.DataFrame(section_data)
                    if not df.empty:
                        unit = normalize_unit(json_data.get("unit", "USD"))
                        df.columns = [
                            col if col == "Metric" else f"{col} ({unit})" for col in df.columns
                        ]
                    df.to_excel(writer, sheet_name=section_name[:31], index=False)
                except Exception as e:
                    print(f"⚠️ Could not write sheet '{section_name}': {e}")

    print(f"📁 Excel saved to: {filename}")
    return filename


def process_pdf_to_excel(pdf_path: str) -> str:
    status = "succeed"
    dest_path = None

    assert os.path.exists(pdf_path), f"❌ File not found: {pdf_path}"
    print(f"📤 Uploading PDF: {pdf_path}")
    uploaded_pdf = client.files.upload(
        path=pdf_path,
        config={"mime_type": "application/pdf"}
    )
    print(f"✅ Uploaded: name={uploaded_pdf.name}, uri={uploaded_pdf.uri}")

    while uploaded_pdf.state == "PROCESSING":
        print("⏳ Waiting for file to finish processing...")
        time.sleep(2)
        uploaded_pdf = client.files.get(name=uploaded_pdf.name)

    pdf_part = Part.from_uri(file_uri=uploaded_pdf.uri, mime_type="application/pdf")

    # Extract statements
    income_statement_response = extract_income_statement(pdf_part)
    balance_sheet_response = extract_balance_sheet(pdf_part)
    cash_flow_statement_response = extract_cash_flow_statement(pdf_part)

    if not income_statement_response:
        raise RuntimeError("❌ No response for Income Statement.")
    if not balance_sheet_response:
        raise RuntimeError("❌ No response for Balance Sheet.")
    if not cash_flow_statement_response:
        raise RuntimeError("❌ No response for Cash Flow Statement.")

    # Parse
    json_data = json.loads(extract_json_from_markdown(income_statement_response))
    balance_json = json.loads(extract_json_from_markdown(balance_sheet_response))
    json_data["Balance Sheet"] = balance_json.get("Balance Sheet", [])
    cash_flow_json = json.loads(extract_json_from_markdown(cash_flow_statement_response))
    json_data["Cash Flow Statement"] = cash_flow_json.get("Cash Flow Statement", [])

    try:
        dest_path = create_excel_dynamic(json_data, pdf_path)
    except Exception as e:
        status = "failed"
        print(f"❌ Conversion failed: {e}")
        raise
    finally:
        try:
            src_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
            dest_size = os.path.getsize(dest_path) if dest_path and os.path.exists(dest_path) else 0
            log_entry = f"{os.path.basename(pdf_path)}\t{src_size}\t{status}\t" \
                        f"{os.path.basename(dest_path) if dest_path else ''}\t{dest_size}\t" \
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(log_entry)
            print(f"📝 Log updated: {log_file}")
        except Exception as log_err:
            print(f"⚠️ Failed to write log: {log_err}")

    return dest_path
