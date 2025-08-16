# 📂 PDF Financial Report to Excel Converter

This project converts PDF-based **financial statements** (Income
Statement, Balance Sheet, and Cash Flow Statement) into **structured
Excel files** using the **Google Gemini API**.\
It provides both a **command-line backend** (`main.py`) and a
**Streamlit-based web frontend** (`front_end.py`).

------------------------------------------------------------------------

## 🚀 Features

-   Upload financial report PDFs.
-   Extract **Income Statement, Balance Sheet, and Cash Flow
    Statement**.
-   Normalize units (millions, thousands, billions, etc.).
-   Export results into **Excel with multiple sheets**.
-   Maintain a **conversion log file** (`convert_pdf_log.txt`).
-   Interactive **web UI** using Streamlit.

------------------------------------------------------------------------

## 📦 Installation

1.  Clone the repository:

    ``` bash
    git clone https://github.com/your-repo/pdf-to-excel.git
    cd pdf-to-excel
    ```

2.  Create a virtual environment (recommended):

    ``` bash
    python -m venv venv
    source venv/bin/activate   # macOS/Linux
    venv\Scripts\activate      # Windows
    ```

3.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

------------------------------------------------------------------------

## 🔑 Setup Google Gemini API

This project uses the **Google Gemini API**.

1.  Get an API key from [Google AI
    Studio](https://aistudio.google.com/).

2.  Set the environment variable:

    ``` bash
    export GEMINI_API_KEY="your_api_key_here"   # macOS/Linux
    set GEMINI_API_KEY=your_api_key_here        # Windows PowerShell
    ```

------------------------------------------------------------------------

## ▶️ Usage

### 1. Command-Line Mode

Run conversion directly:

``` bash
python main.py
```

(Modify `main.py` to pass the PDF path if running standalone.)

### 2. Web App Mode

Run Streamlit UI:

``` bash
streamlit run front_end.py
```

Then open the browser at <http://localhost:8501>.

------------------------------------------------------------------------

## 📁 File Structure

    project/
    │── main.py              # Backend PDF processing & Excel export
    │── front_end.py         # Streamlit frontend
    │── functions.py         # Gemini API extraction functions
    │── requirements.txt     # Dependencies
    │── README.md            # Documentation
    │── output/              # Generated Excel files
    │── uploads/             # Uploaded PDF files
    │── convert_pdf_log.txt  # Conversion log

------------------------------------------------------------------------

## 📝 Log File Format

The log file `convert_pdf_log.txt` keeps a record of each conversion
with:

    SourceFileName   SourceFileSize   Status   DestinationFileName   DestinationFileSize   ConvertedDatetime

Example:

    sample_report.pdf   204800   succeed   sample_report.xlsx   50432   2025-08-15 10:32:45

------------------------------------------------------------------------

## ⚠️ Notes

-   Requires a valid **Google Gemini API key**.
-   Excel output includes **separate sheets** for each financial
    statement.
-   Units are automatically normalized (e.g., USD in millions → numbers
    fully scaled).

------------------------------------------------------------------------

## 📌 License

MIT License
