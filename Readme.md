# Financial Report Extractor (PDF → Excel)

This project extracts **Income Statement**, **Balance Sheet**, and **Cash Flow Statement** data from a PDF financial report using **Google Gemini API**, then saves the results into an Excel file with the same base name as the input PDF.

---

## 📂 Project Structure
```
project/
├── main.py
├── functions.py
├── requirements.txt
├── README.md
└── input/
    └── sample_financial_report_COST-2024.pdf
```

---

## 🚀 Setup Instructions

### 1️⃣ Create and Activate a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Set Up API Key
You must have a **Google Gemini API key**.

Set it as an environment variable:

**Windows (Powershell)**
```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

**macOS/Linux**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

---

## ▶️ Run the Script
Place your PDF financial report in the `input/` folder and update the `pdf_path` in `main.py` if needed.

```bash
python main.py
```

---

## 📄 Output
The script:
1. Uploads the PDF to the Gemini API.
2. Extracts **Income Statement**, **Balance Sheet**, and **Cash Flow Statement**.
3. Cleans and formats the data.
4. Saves the extracted data to an **Excel file** with the same base name as the PDF.

Example:
```
input/sample_financial_report_COST-2024.pdf
⬇
sample_financial_report_COST-2024.xlsx
```

---

## 🛠 Requirements
- Python 3.8+
- Google Gemini API Key
- Internet connection

---

## 📦 Dependencies
See `requirements.txt`:
```
pandas
openpyxl
google-generativeai
```

---

## ⚠️ Notes
- The PDF should be machine-readable (not scanned images without OCR).
- The API might take a few seconds to process the file.
- Only **valid JSON** output from the model is parsed; if JSON decoding fails, the script will print the raw model response.

---
