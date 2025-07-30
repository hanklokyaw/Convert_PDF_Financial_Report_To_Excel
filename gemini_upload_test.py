import os
import io
from google import genai
from datetime import datetime

def upload_pdf_and_verify(pdf_path: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ GEMINI_API_KEY not found in environment variables.")

    client = genai.Client(api_key=api_key)

    print(f"📤 Uploading PDF: {pdf_path}")
    try:
        # Use either file path or file-like object
        with open(pdf_path, "rb") as f:
            mime_type = "application/pdf"
            uploaded_file = client.files.upload(
                file=f,
                config={"mime_type": mime_type}
            )
    except TypeError as e:
        return {"error": f"❌ Upload failed: {e}"}

    print(f"✅ Upload complete: name={uploaded_file.name}, uri={uploaded_file.uri}")

    # Optionally verify via list or get
    files_list = list(client.files.list())
    found = next((f for f in files_list if f.name == uploaded_file.name), None)

    result = {
        "source_file": os.path.basename(pdf_path),
        "timestamp": datetime.now().strftime("%Y‑%m‑%d %H:%M:%S"),
        "uploaded": {
            "name": uploaded_file.name,
            "uri": getattr(uploaded_file, "uri", None),
            "mime_type": getattr(uploaded_file, "mime_type", None),
            "state": getattr(uploaded_file, "state", None),
        },
        "found_in_list": bool(found),
        "found_info": {
            "name": found.name,
            "mime_type": found.mime_type,
            "state": getattr(found, "state", None),
        } if found else None
    }

    return result

if __name__ == "__main__":
    pdf_path = "input/sample_financial_report_COST-2024.pdf"
    outcome = upload_pdf_and_verify(pdf_path)
    print("\n=== Upload Report ===")
    for k, v in outcome.items():
        print(f"{k}: {v}")
