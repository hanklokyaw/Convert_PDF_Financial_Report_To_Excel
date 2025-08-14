import streamlit as st
import os

st.set_page_config(page_title="File Upload", page_icon="📂")

st.title("📂 File Upload Example")

# Choose a file
uploaded_file = st.file_uploader("Choose a file", type=None)

if uploaded_file is not None:
    # Save file locally
    save_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
    st.write(f"📁 Saved at: `{save_path}`")

    # Optional: Show file details
    st.write("**File details:**")
    st.write({
        "name": uploaded_file.name,
        "type": uploaded_file.type,
        "size (KB)": round(len(uploaded_file.getbuffer()) / 1024, 2)
    })
