from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.0-flash"

def extract_financial_data(pdf_part):
    prompt = """
You are a professional financial analyst.

Please extract the full Income Statement from the document.

Instructions:
1. Detect and return the unit of measurement (e.g., "USD", "USD in thousands", or "USD in millions") in a top-level field called `unit`. This is for informational purposes only.
2. Regardless of unit, return **fully scaled numeric values** (e.g., 249625000).
3. If there is additional information such as "(amounts in millions, except per share data)", then add the per share titles "(not in millions)".
4. Return the Income Statement as a list of dictionaries, one row per metric, under the key `"Income Statement"`.
5. Sort the years in descending order (e.g., "2024", "2023", "2022").
6. Can I spread the item into multiple columns in hierarchy form. Such as Revenue is an item in the first column, Net sales and Membership fees are sub items, Total revenue is the sum of sub items.
7. If any additional line items not included in the template appear in the financial statement, insert them into the appropriate logical position.
8. Output must be **strictly valid JSON**, with no markdown or explanation.

Example format:

{
  "Income Statement": [
    { "Metric": "Revenue", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Cost of Goods Sold (COGS)", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Gross Profit", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Operating Expenses", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Selling, General & Admin (SG&A)", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Research & Development (R&D)", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Operating Income", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Interest Income", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Interest Expense", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Other Income (Expense), net", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Income Before Tax", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Income Tax Expense", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Net Income", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Net Income Attributable to Non-Controlling Interest", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Net Income Attributable to Parent", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Earnings Per Share (EPS) - Basic", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Earnings Per Share (EPS) - Diluted", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Weighted Average Shares Outstanding - Basic", "2022": "", "2023": "", "2024": "" },
    { "Metric": "Weighted Average Shares Outstanding - Diluted", "2022": "", "2023": "", "2024": "" }
  ]
}

⚠️ Do not explain anything. Return only valid JSON.

Return **only valid JSON** and **do not add explanations**.

"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pdf_part],
        )
        return response.text
    except Exception as e:
        print(f"❌ API error: {e}")
        return None


def extract_balance_sheet(pdf_part):
    prompt = """
You are a professional financial analyst.

Please extract the full Balance Sheet from the document.

Instructions:
1. Detect and return the unit of measurement (e.g., "USD", "USD in thousands", or "USD in millions") in a top-level field called `unit`. This is for informational purposes only.
2. Regardless of unit, return **fully scaled numeric values** (e.g., 249625000).
3. Present the Balance Sheet as a hierarchy where high-level groups (Assets, Liabilities, Equity) contain sub-items like Current Assets, Non-Current Assets, etc.
4. Return the Balance Sheet as a list of dictionaries, one row per line item, under the key `"Balance Sheet"`.
5. Sort the years in descending order (e.g., "2024", "2023", "2022").
6. If any additional line items not included in the template appear in the financial statement, insert them into the appropriate logical position.
7. Output must be **strictly valid JSON**, with no markdown or explanation.

Example format:
{
  "Balance Sheet": [
    { "Metric": "Assets", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Current Assets", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Cash and Cash Equivalents", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Accounts Receivable", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Inventories", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Non-Current Assets", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Property, Plant & Equipment", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Liabilities", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Current Liabilities", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Accounts Payable", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Short-Term Debt", "2022": "", "2023": "", "2024": "" },

    { "Metric": "  Non-Current Liabilities", "2022": "", "2023": "", "2024": "" },
    { "Metric": "    Long-Term Debt", "2022": "", "2023": "", "2024": "" },

    { "Metric": "Equity", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Common Stock", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Retained Earnings", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Treasury Stock", "2022": "", "2023": "", "2024": "" },
    { "Metric": "  Total Equity", "2022": "", "2023": "", "2024": "" }
  ]
}

⚠️ Return only valid JSON. No markdown or explanation.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, pdf_part],
        )
        return response.text
    except Exception as e:
        print(f"❌ API error (balance sheet): {e}")
        return None
