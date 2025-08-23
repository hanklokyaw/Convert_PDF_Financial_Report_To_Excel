# 📂 PDF to Excel Financial Report Converter

This project extracts **Income Statement**, **Balance Sheet**, and **Cash Flow Statement** from PDF financial reports using **Google Gemini API** and converts them into a clean **Excel file** with multiple sheets.

It also provides a **Streamlit web interface** to upload PDFs, preview extracted data, and download the resulting Excel file.

---

## 🚀 Features
- Upload **PDF financial reports**
- Extract:
  - 📊 Income Statement
  - 📑 Balance Sheet
  - 💵 Cash Flow Statement
- Save data into **Excel (.xlsx)** with separate sheets
- Preview extracted data in the web app
- Conversion log stored in `convert_pdf_log.txt`

---

## 🛠 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/pdf-to-excel-financial.git
cd pdf-to-excel-financial
```

### 2. Create Virtual Environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Set your **Gemini API Key** as an environment variable:

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (Powershell):**
```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

---

## ▶️ Usage

### Run the Streamlit Web App
```bash
streamlit run front_end.py
```

This will start a local server and open the app in your browser.

---

## 📂 Project Structure

```
pdf-to-excel-financial/
│── front_end.py        # Streamlit web app for PDF upload & preview
│── main.py             # Core processing: PDF → JSON → Excel
│── functions.py        # Extraction functions using Gemini API
│── requirements.txt    # Python dependencies
│── convert_pdf_log.txt # Log of conversions
│── output/             # Generated Excel files
│── uploads/            # Uploaded PDF files
```

---

## 📝 Log File (`convert_pdf_log.txt`)
Each conversion is logged with:
- Source file name & size
- Conversion status (succeed/failed)
- Destination file name & size
- Conversion datetime

---

## ⚠️ Notes
- Requires **Google Gemini API access**.
- Large PDFs may take longer to process.
- Excel preview in the app shows only first 50 rows.

---

## 📜 License
MIT License. Free to use and modify.
