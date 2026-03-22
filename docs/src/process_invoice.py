import json
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

import pdfplumber
from openai import OpenAI

print("DEBUG: process_invoice WITH duplicate detection loaded")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------
# 1. Extract text from PDF
# ---------------------------
def extract_text(file_path):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# ---------------------------
# 2. Old regex extraction (keep for reference)
# ---------------------------
def extract_fields(text):
    def find(pattern, group=1):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(group).strip() if match else None

    return {
        "invoice_number": find(r"invoice\s*(?:number|id)[:\s]*([A-Z0-9\-]+)"),
        "vendor": find(r"^\s*([^\n]+)", group=1),
        "invoice_date": find(r"invoice\s*date[:\s]*([\d\-\/]+)"),
        "due_date": find(r"due\s*date[:\s]*([\d\-\/]+)"),
        "total_amount": find(r"total[:\s]*([\d\.,\s]+)")
    }


# ---------------------------
# 3. AI extraction
# ---------------------------
def extract_fields_with_ai(text):
    prompt = f"""
Extract invoice data and return ONLY valid JSON.

Schema:
{{
  "invoice_number": null,
  "vendor": null,
  "invoice_date": null,
  "due_date": null,
  "total_amount": null
}}

Rules:
- Get invoice number
- Get vendor name (the company issuing the invoice, usually at the top)
- Get invoice date in YYYY-MM-DD if present
- Get due date in YYYY-MM-DD if present
- Get FINAL total only (not subtotal, not VAT)
- total_amount can be a number or string, but should represent the final invoice total
- Return valid JSON only
- Do not use markdown code fences
- If unsure, return null

Invoice text:
{text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    raw_output = response.output_text.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_output)


# ---------------------------
# 4. Helpers
# ---------------------------
def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


# ---------------------------
# 5. Amount parsing
# ---------------------------
def parse_amount(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()

    if not s:
        return None

    s = s.replace("EUR", "").replace("SEK", "").replace("USD", "")
    s = s.replace("€", "").replace("$", "")
    s = s.strip()

    s = s.replace("\u00a0", " ")  # non-breaking space
    s = s.replace(" ", "")

    # Ex:
    # 16,444.59  -> comma thousands, dot decimals
    # 34.930,64  -> dot thousands, comma decimals
    if "," in s and "." in s:
        if s.rfind(".") > s.rfind(","):
            s = s.replace(",", "")
        else:
            s = s.replace(".", "")
            s = s.replace(",", ".")

    # Ex:
    # 34930,64 -> comma decimals
    elif "," in s:
        s = s.replace(",", ".")

    # Only keep digits, minus, and dot
    s = re.sub(r"[^0-9.\-]", "", s)

    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------
# 6. Validation
# ---------------------------
def validate(fields):
    missing_fields = []

    required_fields = [
        "invoice_number",
        "vendor",
        "invoice_date",
        "due_date",
        "total_amount",
    ]

    for key in required_fields:
        value = fields.get(key)
        if value is None or str(value).strip() == "":
            missing_fields.append(key)

    if missing_fields:
        return {
            "valid": False,
            "reason": f"Missing fields: {missing_fields}"
        }

    amount = parse_amount(fields.get("total_amount"))

    if amount is None:
        return {
            "valid": False,
            "reason": "Invalid amount format"
        }

    fields["total_amount"] = amount

    if amount > 50000:
        return {
            "valid": False,
            "reason": "Amount too high"
        }

    return {
        "valid": True,
        "reason": "OK"
    }


# ---------------------------
# 7. Duplicate detection
# ---------------------------
def detect_duplicate(current_invoice, seen_invoices):
    current_number = normalize_text(current_invoice.get("invoice_number"))
    current_vendor = normalize_text(current_invoice.get("vendor"))
    current_amount = current_invoice.get("total_amount")
    current_date = normalize_text(current_invoice.get("invoice_date"))

    for previous in seen_invoices:
        prev_number = normalize_text(previous.get("invoice_number"))
        prev_vendor = normalize_text(previous.get("vendor"))
        prev_amount = previous.get("total_amount")
        prev_date = normalize_text(previous.get("invoice_date"))

        # Strong rule: same invoice number
        if current_number and prev_number and current_number == prev_number:
            return (
                True,
                "Same invoice_number as previous invoice",
                previous.get("filename", ""),
                "invoice_number",
            )

        # Fallback rule: same vendor + amount + invoice date
        if (
            current_vendor
            and prev_vendor
            and current_vendor == prev_vendor
            and current_amount is not None
            and prev_amount is not None
            and abs(float(current_amount) - float(prev_amount)) < 0.01
            and current_date
            and prev_date
            and current_date == prev_date
        ):
            return (
                True,
                "Same vendor, total_amount, and invoice_date as previous invoice",
                previous.get("filename", ""),
                "vendor_amount_date",
            )

    return False, "", "", None


# ---------------------------
# 8. Classification
# ---------------------------
def classify(fields, validation_result, is_duplicate=False):
    if is_duplicate:
        return "Needs review"

    if not validation_result["valid"]:
        return "Needs review"

    return "Approved"


# ---------------------------
# 9. Main pipeline
# ---------------------------
def process_invoice(file_path, seen_invoices=None):
    if seen_invoices is None:
        seen_invoices = []

    text = extract_text(file_path)

    print("\n--- RAW TEXT ---\n")
    print(text)

    fields = extract_fields_with_ai(text)

    validation_result = validate(fields)

    is_duplicate = False
    duplicate_reason = ""
    duplicate_match_file = ""
    duplicate_rule_type = None

    if validation_result["valid"]:
        (
            is_duplicate,
            duplicate_reason,
            duplicate_match_file,
            duplicate_rule_type,
        ) = detect_duplicate(fields, seen_invoices)

    status = classify(fields, validation_result, is_duplicate=is_duplicate)

    validation_reason = validation_result["reason"]
    if is_duplicate:
        validation_reason = "Duplicate invoice detected"

    return {
        **fields,
        "status": status,
        "validation_reason": validation_reason,
        "is_duplicate": is_duplicate,
        "duplicate_reason": duplicate_reason,
        "duplicate_match_file": duplicate_match_file,
        "duplicate_rule_type": duplicate_rule_type,
    }


# ---------------------------
# 10. Test run
# ---------------------------
if __name__ == "__main__":
    path = "../../data/generated_invoices/INV_CLEAN_001.pdf"

    result = process_invoice(path)

    print("\n--- RESULT ---")
    for k, v in result.items():
        print(f"{k}: {v}")