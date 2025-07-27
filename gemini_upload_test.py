import os
from google import genai
from datetime import datetime

api_key = os.getenv("GEMINI_API_KEY")

def upload_pdf_and_verify(path_to_pdf):
    """
    Uploads a PDF file and verifies its presence via listing.

    Args:
        path_to_pdf (str): Path to the PDF file to upload.

    Returns:
        dict: Details including upload result and listing verification.
    """
    client = genai.Client()

    print(f"Uploading file: {path_to_pdf} …")
    myfile = client.files.upload(
        file=path_to_pdf,
        config={"mime_type": "application/pdf"}
    )
    print(f"Upload complete: name={myfile.name}, state={getattr(myfile, 'state', None)}")

    # Now list files to check presence
    print("Listing recent files …")
    files_list = list(client.files.list())
    # Each f has f.name, f.display_name, f.mime_type, f.state, f.create_time, etc.

    found = None
    for f in files_list:
        if f.name == myfile.name:
            found = f
            break

    result = {
        "uploaded": {
            "name": myfile.name,
            "display_name": getattr(myfile, "display_name", None),
            "mime_type": myfile.mime_type,
            "state": getattr(myfile, "state", None),
            "create_time": getattr(myfile, "create_time", None),
        },
        "listing_checked": bool(found),
        "found_details": None
    }

    if found:
        result["found_details"] = {
            "name": found.name,
            "display_name": getattr(found, "display_name", None),
            "mime_type": found.mime_type,
            "state": getattr(found, "state", None),
            "create_time": getattr(found, "create_time", None),
        }

    return result

if __name__ == "__main__":
    pdf_path = "path/to/your/document.pdf"
    outcome = upload_pdf_and_verify(pdf_path)

    print("\n=== Upload Outcome ===")
    print(f"Uploaded: {outcome['uploaded']}")
    print(f"Found in list? {outcome['listing_checked']}")
    if outcome['found_details']:
        print(f"File state: {outcome['found_details']['state']}")
