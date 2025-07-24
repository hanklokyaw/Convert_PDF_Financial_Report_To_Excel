import streamlit as st
import os
import json
import pandas as pd
from io import BytesIO
from typing import List
from pydantic import BaseModel
from PIL import Image
import base64
import google.ai.generativelanguage as glm

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set")
    st.stop()

# Initialize client
client = glm.GenerativeServiceClient(
    client_options={"api_key": api_key}
)
model_name = "models/gemini-2.0-flash"


# --- Data Models ---
class Record(BaseModel):
    Field: str
    Value: str


class DocumentOutput(BaseModel):
    income_statement: List[Record] = []
    balance_sheet: List[Record] = []
    cash_flow: List[Record] = []


# --- Image Processing ---
def process_image_to_base64(uploaded_file):
    """Convert image to base64 string"""
    img = Image.open(uploaded_file)
    buffered = BytesIO()
    img.save(buffered, format=img.format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# --- Gemini API Call ---
def extract_financial_data(image_base64, mime_type):
    prompt = """Extract these financial tables:
    - Income Statement (Field, Value)
    - Balance Sheet (Field, Value) 
    - Cash Flow (Field, Value)

    Return ONLY valid JSON:
    {
        "Income Statement": [{"Field":"...","Value":"..."}],
        "Balance Sheet": [{"Field":"...","Value":"..."}],
        "Cash Flow": [{"Field":"...","Value":"..."}]
    }"""

    try:
        # Create the content request
        content = glm.Content(
            parts=[
                glm.Part(
                    inline_data=glm.Blob(
                        mime_type=mime_type,
                        data=image_base64
                    )
                ),
                glm.Part(text=prompt)
            ]
        )

        response = client.generate_content(
            model=model_name,
            contents=[content]
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


# --- Excel Generation ---
def create_excel(all_data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for filename, data in all_data.items():
            name = os.path.splitext(filename)[0][:25]
            if data.income_statement:
                pd.DataFrame([r.dict() for r in data.income_statement]).to_excel(
                    writer, sheet_name=f"{name}_Income", index=False)
            if data.balance_sheet:
                pd.DataFrame([r.dict() for r in data.balance_sheet]).to_excel(
                    writer, sheet_name=f"{name}_Balance", index=False)
    output.seek(0)
    return output


# --- Streamlit UI ---
def main():
    st.title("📷 Financial Data Extraction (Gemini 2.0 Flash)")

    uploaded_files = st.file_uploader(
        "Upload financial statement images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process"):
        with st.spinner("Analyzing images..."):
            all_data = {}
            for file in uploaded_files:
                # Determine MIME type
                mime_type = f"image/{file.name.split('.')[-1].lower()}"
                if mime_type == "image/jpg":
                    mime_type = "image/jpeg"

                # Process image
                image_base64 = process_image_to_base64(file)

                # Get structured data
                result = extract_financial_data(image_base64, mime_type)
                if result:
                    try:
                        json_data = json.loads(result.strip())
                        all_data[file.name] = DocumentOutput(
                            income_statement=[Record(**r) for r in json_data.get("Income Statement", [])],
                            balance_sheet=[Record(**r) for r in json_data.get("Balance Sheet", [])],
                            cash_flow=[Record(**r) for r in json_data.get("Cash Flow", [])]
                        )
                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse {file.name}: {str(e)}")
                        st.code(result)  # Show raw response for debugging

            # Generate Excel if we got data
            if all_data:
                excel_file = create_excel(all_data)
                st.success("✅ Processing complete!")
                st.download_button(
                    "💾 Download Excel",
                    excel_file,
                    "financial_data.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


if __name__ == "__main__":
    main()