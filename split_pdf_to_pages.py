import os
from google import genai
from datetime import datetime

def upload_pdf_and_verify(pdf_path):
    """
    Uploads a PDF to Gemini API and verifies its presence in the uploaded file list.

    Args:
        pdf_path (str): Path to the local PDF file.

    Returns:
        dict: Upload status and verification info.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

    # Configure Gemini client
    genai.configure(api_key=api_key)
    client = genai.Client()

    print(f"Uploading PDF: {pdf_path}")
    try:
        uploaded_file = client.files.upload(
            file=pdf_path,
            config={"mime_type": "application/pdf"}
        )
    except Exception as e:
        return {"error": f"Upload failed: {e}"}

    print(f"✅ Upload complete: {uploaded_file.name}")

    # Check file presence via listing
    files_list = list(client.files.list())
    found_file = next((f for f in files_list if f.name == uploaded_file.name), None)

    result = {
        "source_file": os.path.basename(pdf_path),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uploaded_file": {
            "name": uploaded_file.name,
            "display_name": getattr(uploaded_file, "display_name", None),
            "mime_type": uploaded_file.mime_type,
            "state": getattr(uploaded_file, "state", None),
            "create_time": getattr(uploaded_file, "create_time", None),
        },
        "found_in_list": bool(found_file),
        "verified_file_info": {
            "name": found_file.name,
            "state": getattr(found_file, "state", None),
            "mime_type": found_file.mime_type,
            "create_time": getattr(found_file, "create_time", None),
        } if found_file else None
    }

    return result

# ---------- Run it ----------
if __name__ == "__main__":
    pdf_path = "input/sample_financial_report_COST-2024.pdf"
    result = upload_pdf_and_verify(pdf_path)

    print("\n=== Upload Report ===")
    for k, v in result.items():
        print(f"{k}: {v}")
