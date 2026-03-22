"""
En fakturapipeline per PDF: text → AI-extraktion → normalisering/validering →
dubblettkontroll mot tidigare körda fakturor → status (Approved / Needs review).

Avsikt: AI för ostrukturerad text, regler för beslut och spårbarhet (orsakskoder).
Körs enstaka fil via __main__ eller anropas från batch_eval med delad seen_invoices-lista.
"""
import json
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Projektrot ligger två nivåer upp från docs/src/
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

import pdfplumber
from openai import OpenAI

print("DEBUG: process_invoice WITH duplicate detection loaded")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------
# 1. Text från PDF
# ---------------------------
def extract_text(file_path):
    """Läser innehåll från PDF:ns textlager (pdfplumber, ingen OCR)."""
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# ---------------------------
# 2. Regex-extraktion (referens, används inte i huvudflödet)
# ---------------------------
def extract_fields(text):
    """Enkel mönsterbaserad extraktion — behålls för jämförelse eller felsökning."""

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
# 3. AI-extraktion
# ---------------------------
def extract_fields_with_ai(text):
    """Anropar LLM med fast JSON-schema; returnerar dict med fält eller null."""
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

    # Modellen kan ändå wrappa JSON i ``` — rensa bort det innan parse
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_output)


# ---------------------------
# 4. Hjälpfunktioner för jämförelse
# ---------------------------
def normalize_text(value):
    """Enhetlig sträng för dubblettregler (trim + gemener)."""
    if value is None:
        return ""
    return str(value).strip().lower()


# ---------------------------
# 5. Beloppsnormalisering
# ---------------------------
def parse_amount(value):
    """
    Gör om LLM/sträng-belopp till float. Hanterar EU/US-format och valutatecken.

    Viktigt för eval: samma logik som i validate() så att belopp blir jämförbara.
    """
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

    s = s.replace("\u00a0", " ")  # hårt mellanslag
    s = s.replace(" ", "")

    # Både punkt och komma: avgör vilket som är decimaltecken (sista förekomsten vinner)
    # 16,444.59  → tusentalskomma, decimalpunkt
    # 34.930,64  → tusentalspunkt, decimalkomma
    if "," in s and "." in s:
        if s.rfind(".") > s.rfind(","):
            s = s.replace(",", "")
        else:
            s = s.replace(".", "")
            s = s.replace(",", ".")

    # Endast komma → tolka som decimalkomma
    # 34930,64
    elif "," in s:
        s = s.replace(",", ".")

    # Strippa allt utom siffror, minus och punkt
    s = re.sub(r"[^0-9.\-]", "", s)

    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------
# 6. Validering (affärsregler)
# ---------------------------
def validate(fields):
    """
    Kontrollerar obligatoriska fält, att belopp går att parsa och en övre gräns.

    Muterar fields['total_amount'] till float vid godkänd parsning.
    """
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

    # Enkel risksignal: flagga orimligt höga belopp för manuell granskning
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
# 7. Dubblettdetektering (regelbaserad)
# ---------------------------
def detect_duplicate(current_invoice, seen_invoices):
    """
    Jämför mot tidigare bearbetade fakturor i samma batch (ordning spelar roll).

    Regel 1: samma fakturanummer (normaliserat).
    Regel 2: samma leverantör + samma belopp + samma fakturadatum (fallback).

    Returnerar (is_dup, orsak, matchande filnamn, regeltyp).
    """
    current_number = normalize_text(current_invoice.get("invoice_number"))
    current_vendor = normalize_text(current_invoice.get("vendor"))
    current_amount = current_invoice.get("total_amount")
    current_date = normalize_text(current_invoice.get("invoice_date"))

    for previous in seen_invoices:
        prev_number = normalize_text(previous.get("invoice_number"))
        prev_vendor = normalize_text(previous.get("vendor"))
        prev_amount = previous.get("total_amount")
        prev_date = normalize_text(previous.get("invoice_date"))

        # Primär signal: identiskt fakturanummer
        if current_number and prev_number and current_number == prev_number:
            return (
                True,
                "Same invoice_number as previous invoice",
                previous.get("filename", ""),
                "invoice_number",
            )

        # Sekundär: leverantör + belopp + fakturadatum (t.ex. om nummer skiljer sig)
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
# 8. Klassificering (routing)
# ---------------------------
def classify(fields, validation_result, is_duplicate=False):
    """Dubblett eller ogiltig data → manuell kö; annars auto-godkänd."""
    if is_duplicate:
        return "Needs review"

    if not validation_result["valid"]:
        return "Needs review"

    return "Approved"


# ---------------------------
# 9. Huvudflöde per fil
# ---------------------------
def process_invoice(file_path, seen_invoices=None):
    """
    Kör hela pipelinen för en PDF.

    seen_invoices: lista med dicts från tidigare filer i batchen (för dubbletter).
    Anroparen ansvarar för att lägga till filename på dicts om det behövs för spårning.
    """
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

    # Kör inte dubblettlogik på trasiga rader — undvik falska träffar
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
# 10. Snabbtest från kommandorad
# ---------------------------
if __name__ == "__main__":
    path = "../../data/generated_invoices/INV_CLEAN_001.pdf"

    result = process_invoice(path)

    print("\n--- RESULT ---")
    for k, v in result.items():
        print(f"{k}: {v}")
