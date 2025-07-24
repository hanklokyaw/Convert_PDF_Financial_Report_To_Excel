import streamlit as st
import os
import json
import pandas as pd
from io import BytesIO
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

# -- Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set.")
    st.stop()

client = genai.Client(api_key=api_key)

# -- Define the structured output schema
class Record(BaseModel):
    Field: str
    Value: str

class DocumentOutput(BaseModel):
    income_statement: List[Record] = []
    balance_sheet: List[Record] = []
    cash_flow_statement: List[Record] = []
    owners_equity: List[Record] = []

# -- Convert structured schema to Excel
@st.cache_data
def save_to_excel(data: DocumentOutput) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([r.dict() for r in data.income_statement]).to_excel(writer, index=False, sheet_name="Income Statement")
        pd.DataFrame([r.dict() for r in data.balance_sheet]).to_excel(writer, index=False, sheet_name="Balance Sheet")
        pd.DataFrame([r.dict() for r in data.cash_flow_statement]).to_excel(writer, index=False, sheet_name="Cash Flow Statement")
        pd.DataFrame([r.dict() for r in data.owners_equity]).to_excel(writer, index=False, sheet_name="Owner's Equity")
    output.seek(0)
    return output

# -- Send PDF to Gemini and enforce structured output
@st.cache_data
def send_pdf_to_gemini(uploaded_file):
    pdf_bytes = uploaded_file.getvalue()
    part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[part],
            generation_config={
                "response_mime_type": "application/json"
            },
            tools=[{
                "function_declarations": [DocumentOutput]
            }]
        )
        return response
    except Exception as e:
        st.error(f"❌ Gemini API Error: {e}")
        return None

# -- Streamlit frontend

def main():
    st.set_page_config(page_title="📊 Financial Report to Excel", layout="centered")
    st.title("📊 Convert Financial Report to Excel")

    uploaded_file = st.file_uploader("Upload your Financial PDF", type=["pdf"])

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("🧠 Extract and Convert"):
            with st.spinner("Sending to Gemini and processing..."):
                response = send_pdf_to_gemini(uploaded_file)

            if response and hasattr(response, "function_call") and response.function_call:
                try:
                    data = DocumentOutput(**response.function_call.args)
                    excel_data = save_to_excel(data)

                    st.success("✅ Excel generated successfully!")

                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_data,
                        file_name="financial_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Display tables in app
                    st.subheader("📑 Income Statement")
                    st.dataframe(pd.DataFrame([r.dict() for r in data.income_statement]), use_container_width=True)

                    st.subheader("📑 Balance Sheet")
                    st.dataframe(pd.DataFrame([r.dict() for r in data.balance_sheet]), use_container_width=True)

                    st.subheader("📑 Cash Flow Statement")
                    st.dataframe(pd.DataFrame([r.dict() for r in data.cash_flow_statement]), use_container_width=True)

                    st.subheader("📑 Owner's Equity")
                    st.dataframe(pd.DataFrame([r.dict() for r in data.owners_equity]), use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Failed to parse Gemini response: {e}")
            else:
                st.error("❌ No valid response from Gemini.")

if __name__ == "__main__":
    main()
