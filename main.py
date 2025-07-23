import streamlit as st
from google import genai
import os
from io import BytesIO
import pandas as pd
import json
from pdf2image import convert_from_bytes

# Configure the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set.")
    st.stop()

client = genai.Client(api_key=api_key)

EXTRACTION_PROMPT = """
You are a financial expert. Extract all the tables from the image or PDF. 
Only return valid JSON in this format:

{
  "Income Statement": [
    {"Field": "Revenue", "Value": "100000"},
    {"Field": "COGS", "Value": "40000"},
    ...
  ],
  "Balance Sheet": [
    {"Field": "Assets", "Value": "150000"},
    ...
  ],
  "Cash Flow Statement": [
    {"Field": "Operating Cash Flow", "Value": "25000"},
    ...
  ]
}

Do not return any text explanation. Only the JSON object. If a section is missing, skip it.
"""

def send_pdf_to_gemini(uploaded_file):
    pages = convert_from_bytes(uploaded_file.getvalue())
    accumulated_text = ""

    for i, page in enumerate(pages):
        img_byte_arr = BytesIO()
        page.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        content = genai.Image(data=img_bytes)
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[EXTRACTION_PROMPT, content]
            )
            accumulated_text += response.text + "\n"
        except Exception as e:
            st.error(f"Gemini API Error on page {i+1}: {e}")
            return None

    return accumulated_text.strip()

def send_image_to_gemini(uploaded_file):
    content = genai.Image(data=uploaded_file.getvalue())
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[EXTRACTION_PROMPT, content]
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

def send_to_gemini(uploaded_file):
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        return send_pdf_to_gemini(uploaded_file)
    elif file_type.startswith("image/"):
        return send_image_to_gemini(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload PDF or image files.")
        return None

def parse_json_to_dfs(response_text):
    # Gemini might return multiple JSON objects separated by newlines (one per page)
    dfs = {}
    for json_str in response_text.splitlines():
        json_str = json_str.strip()
        if not json_str:
            continue
        try:
            data = json.loads(json_str)
            for section, records in data.items():
                if section not in dfs:
                    dfs[section] = pd.DataFrame(records)
                else:
                    # Append new records from other pages
                    dfs[section] = pd.concat([dfs[section], pd.DataFrame(records)], ignore_index=True)
        except Exception as e:
            st.warning(f"Warning: Failed to parse one JSON block: {e}")
            continue
    return dfs

def save_to_excel(dfs: dict) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dfs.items():
            clean_name = sheet_name[:31].replace("/", "_")
            df.to_excel(writer, index=False, sheet_name=clean_name)
    output.seek(0)
    return output

def main():
    st.set_page_config(page_title="📊 PDF/Image to Excel - Financial Extractor", layout="centered")
    st.title("📊 Convert Financial Report to Excel")

    uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("🧠 Convert to Excel"):
            with st.spinner("Sending to Gemini and processing..."):
                response_text = send_to_gemini(uploaded_file)

            if response_text:
                st.info("Gemini responded. Parsing into tables...")
                dfs = parse_json_to_dfs(response_text)

                if dfs:
                    excel_data = save_to_excel(dfs)
                    st.success("✅ Excel generated successfully!")

                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_data,
                        file_name="financial_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    for section, df in dfs.items():
                        st.subheader(section)
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error("No valid data extracted from Gemini.")
            else:
                st.error("No response from Gemini.")

if __name__ == "__main__":
    main()
