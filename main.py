import streamlit as st
from google import genai
import os
from io import BytesIO
import pandas as pd
from PIL import Image
import json

# Configure the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set.")
    st.stop()

client = genai.Client(api_key=api_key)

# Gemini prompt
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

def send_to_gemini(uploaded_file):
    file_data = uploaded_file.getvalue()
    file_type = uploaded_file.type

    contents = [
        EXTRACTION_PROMPT,
        {
            "mime_type": file_type,
            "data": file_data
        }
    ]

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

def parse_json_to_dfs(response_text):
    try:
        data = json.loads(response_text)
        dfs = {}
        for section, records in data.items():
            dfs[section] = pd.DataFrame(records)
        return dfs
    except Exception as e:
        st.error(f"❌ Failed to parse Gemini JSON response: {e}")
        return {}

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
            with st.spinner("Sending to Gemini..."):
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
