import os
import json
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path

def split_pdf_to_pages(input_pdf_path, output_folder, poppler_path=None, log_path="convert_pdf_log.txt"):
    """
    Split PDF into single pages and convert to JPEGs, logging the process.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_folder (str): Folder to save split pages and JPEGs.
        poppler_path (str, optional): Path to poppler binaries (Windows only).
        log_path (str): Path to log file where the result will be appended.

    Returns:
        dict: Summary including success count, total, failed list, and log path.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_filename = os.path.basename(input_pdf_path)
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    success_count = 0
    failed_pages = []
    output_files = []
    failure_reasons = {}

    for i, page in enumerate(reader.pages):
        try:
            # Save individual PDF page
            writer = PdfWriter()
            writer.add_page(page)
            page_pdf_path = os.path.join(output_folder, f"page_{i+1}.pdf")
            with open(page_pdf_path, "wb") as f:
                writer.write(f)

            # Convert to JPEG
            images = convert_from_path(
                page_pdf_path,
                dpi=200,
                poppler_path=poppler_path,
                first_page=1,
                last_page=1
            )
            jpeg_path = os.path.join(output_folder, f"page_{i+1}.jpg")
            images[0].save(jpeg_path, "JPEG")

            output_files.append((page_pdf_path, jpeg_path))
            success_count += 1
        except Exception as e:
            reason = str(e)
            print(f"❌ Error processing page {i+1}: {reason}")
            failed_pages.append(i + 1)
            failure_reasons[i + 1] = reason

    # Create log entry
    log_entry = {
        "source_file": base_filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success_count": success_count,
        "total_pages": total_pages,
        "failed_pages": failed_pages,
        "failure_reasons": failure_reasons
    }

    # Append to log file
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return {
        "log": log_entry,
        "output_files": output_files,
        "log_file": log_path
    }

# ---------- Run the function ----------
if __name__ == "__main__":
    result = split_pdf_to_pages(
        input_pdf_path="input/sample_financial_report_COST-2024.pdf",
        output_folder="output",
        poppler_path=r"C:\Program Files (x86)\poppler-24.08.0\Library\bin"  # download and install poppler https://github.com/oschwartz10612/poppler-windows/releases
    )

    log_data = result["log"]
    print(f"\n✅ Completed: {log_data['success_count']}/{log_data['total_pages']} pages succeeded.")
    if log_data["failed_pages"]:
        print(f"❌ Failed pages: {log_data['failed_pages']}")
        print(f"📄 Full log written to: {result['log_file']}")
