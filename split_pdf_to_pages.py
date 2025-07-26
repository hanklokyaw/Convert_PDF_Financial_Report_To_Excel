from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf_to_pages(input_pdf_path, output_folder):
    """
    Split a PDF file into individual pages and save them as separate PDF files.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_folder (str): Folder where split pages will be saved.

    Returns:
        List[str]: List of output file paths for the split pages.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    reader = PdfReader(input_pdf_path)
    output_files = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        output_path = os.path.join(output_folder, f"page_{i+1}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

        output_files.append(output_path)

    return output_files
