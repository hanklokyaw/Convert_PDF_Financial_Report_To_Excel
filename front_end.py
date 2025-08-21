# import required libraries
import streamlit as st
import os
import pandas as pd
# import from main.py
from main import process_pdf_to_excel
import datetime as dt

st.set_page_config(page_title="PDF to Excel Converter", page_icon="📂")

# Show today's date
today = dt.date.today().strftime("%B %d, %Y")  # Example: January 18, 2025
st.markdown(f"#### 📅 {today}")  # H4 size

st.title("📂 Convert PDF Financial Report to Excel")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    save_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")

    with st.spinner("Processing file... Please wait"):
        try:
            excel_path = process_pdf_to_excel(save_path)
            st.success("✅ Conversion completed!")

            # 🔹 Preview Excel in DataFrame
            try:
                df = pd.read_excel(excel_path)
                st.subheader("📊 Preview of Extracted Data")
                st.dataframe(df.head(50))  # show first 50 rows
            except Exception as e:
                st.warning(f"⚠ Could not preview Excel file: {e}")

            # 🔹 Download button
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📥 Download Excel file",
                    data=f,
                    file_name=os.path.basename(excel_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")
