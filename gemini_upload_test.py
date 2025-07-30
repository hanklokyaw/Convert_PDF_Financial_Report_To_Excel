import os
from google import genai
from datetime import datetime

def upload_pdf_and_verify(pdf_path: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ GEMINI_API_KEY not found")

    client = genai.Client(api_key=api_key)

    print(f"📤 Uploading PDF: {pdf_path}")
    try:
        uploaded_file = client.files.upload(
            file=pdf_path,
            config={"mime_type": "application/pdf"}
        )
    except Exception as e:
        return {"error": f"❌ Upload failed: {e}"}

    print(f"✅ Uploaded: name={uploaded_file.name}, uri={getattr(uploaded_file, 'uri', None)}")

    files = list(client.files.list())
    found = next((f for f in files if f.name == uploaded_file.name), None)

    return {
        "source_file": os.path.basename(pdf_path),
        "timestamp": datetime.now().strftime("%Y‑%m‑%d %H:%M:%S"),
        "uploaded": {
            "name": uploaded_file.name,
            "mime_type": getattr(uploaded_file, "mime_type", None),
            "uri": getattr(uploaded_file, "uri", None),
            "state": getattr(uploaded_file, "state", None),
        },
        "found_in_list": bool(found),
        "found_info": {
            "name": found.name,
            "mime_type": found.mime_type,
            "state": getattr(found, "state", None),
        } if found else None
    }

if __name__ == "__main__":
    result = upload_pdf_and_verify("input/sample_financial_report_COST-2024.pdf")
    for k, v in result.items():
        print(k, ":", v)
