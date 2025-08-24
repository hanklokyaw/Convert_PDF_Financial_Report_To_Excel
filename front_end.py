# import required libraries
import streamlit as st
import os
import pandas as pd
import datetime as dt
# import from main.py
from main import process_pdf_to_excel

st.set_page_config(page_title="PDF to Excel Converter", page_icon="📂")

# Show today's date
today = dt.date.today().strftime("%B %d, %Y")  # Example: January 18, 2025
st.markdown(f"#### 📅 {today}")  # H4 size

st.title("📂 Convert PDF Financial Report to Excel")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)
    save_path = os.path.join("uploads", uploaded_file.name)

    # Save uploaded file temporarily to check size
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    uploaded_size = os.path.getsize(save_path)

    # Expected Excel output file path (same name but .xlsx)
    excel_path = os.path.splitext(save_path)[0] + ".xlsx"

    # 🔹 Check if Excel already exists and matches file size
    processed_before = False
    size_record_path = excel_path + ".size"  # store original PDF size for comparison

    if os.path.exists(excel_path) and os.path.exists(size_record_path):
        with open(size_record_path, "r") as sf:
            recorded_size = int(sf.read().strip())
        if recorded_size == uploaded_size:
            processed_before = True

    if processed_before:
        st.info(f"ℹ️ File '{uploaded_file.name}' was already processed before. Skipping reprocessing.")

        # Preview existing Excel
        try:
            df = pd.read_excel(excel_path)
            st.subheader("📊 Preview of Extracted Data (Cached Result)")
            st.dataframe(df.head(50))
        except Exception as e:
            st.warning(f"⚠ Could not preview Excel file: {e}")

        # Provide download button
        with open(excel_path, "rb") as f:
            st.download_button(
                label="📥 Download Excel file",
                data=f,
                file_name=os.path.basename(excel_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")

        with st.spinner("Processing file... Please wait"):
            try:
                excel_path = process_pdf_to_excel(save_path)

                # Save file size record for future cache check
                with open(size_record_path, "w") as sf:
                    sf.write(str(uploaded_size))

                st.success("✅ Conversion completed!")

                # Preview Excel
                try:
                    df = pd.read_excel(excel_path)
                    st.subheader("📊 Preview of Extracted Data")
                    st.dataframe(df.head(50))
                except Exception as e:
                    st.warning(f"⚠ Could not preview Excel file: {e}")

                # Download button
                with open(excel_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Excel file",
                        data=f,
                        file_name=os.path.basename(excel_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"❌ Error: {e}")
