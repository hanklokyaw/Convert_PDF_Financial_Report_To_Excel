# 📊 Financial Report Extractor (PDF/Image → Excel) with Gemini

A Streamlit web app that converts PDFs or images of financial reports into structured multi-sheet Excel files using Google Gemini's GenAI multimodal capabilities.

---

## 🔧 Features

- Validates presence of `GEMINI_API_KEY` environment variable.
- Converts PDF pages to images using `pdf2image` + Poppler.
- Uses `google-genai` SDK with `types.Part.from_bytes()` for Gemini inputs.
- Parses JSON responses from Gemini.
- Outputs an Excel workbook with separate sheets for **Income Statement**, **Balance Sheet**, **Cash Flow Statement**.
- Preview data in-app and download the result.

---

## ⚙️ Setup Instructions

### 1. Clone & install dependencies
```bash
git clone <repo-url>
cd <project-folder>
pip install -r requirements.txt
```

### 2. Install Poppler (required by pdf2image)
Windows:
Download Poppler from Poppler releases, extract, and add the Library\bin folder to your System PATH.

macOS:
```bash
brew install poppler
```

Linux:
```bash
sudo apt-get install poppler-utils
```

3. Obtain and set your Gemini API key
Set the environment variable:

macOS/Linux:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Windows (PowerShell):
```bash
$Env:GEMINI_API_KEY = "your_api_key_here"
```

Ensure your key has access to Gemini multimodal model (gemini-2.5-flash or newer).

---

## 🚀 Run the App

```bash
streamlit run main.py
```

---

## 🧩 Code Example (Multimodal Part Input)

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

part = types.Part.from_bytes(
    data=uploaded_file.getvalue(),
    mime_type=uploaded_file.type
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[EXTRACTION_PROMPT, part]
)
```

---

## 📌 Notes & Tips

- PDFs are converted to images page-by-page, allowing Gemini to process each page separately.
- Expect one JSON response per page—even if it means merging results.
- Ensure GEMINI_API_KEY remains secret; avoid pushing it to source control.
- Files over 20 MB should be handled with caution as requests may fail.

---

## 🧪 Testing

Drop in various report formats and verify:

- JSON structure correctness.
- Excel sheets creation.
- Preview looks accurate.

---

## 📖 License

MIT © Hank Kyaw