#!/usr/bin/env python3
"""
generate_invoices.py

Generate synthetic invoice PDFs plus a ground-truth CSV for an AI/automation
invoice-processing demo case.

Features
--------
- Creates realistic-looking fictional invoices
- Generates line items, subtotal, tax, total, dates and invoice IDs
- Saves PDF files into a target folder
- Saves a ground-truth CSV with expected values
- Supports a configurable number of invoices
- Uses only fictional company data

Dependencies
------------
- reportlab

Install if needed:
    pip install reportlab

Examples
--------
Generate 10 clean invoices:
    python generate_invoices.py

Generate 25 invoices to a custom output folder:
    python generate_invoices.py --count 25 --output-dir ./data/generated_invoices

Generate with a fixed random seed:
    python generate_invoices.py --seed 123
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import List

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: reportlab\n"
        "Install it with: pip install reportlab"
    ) from exc


@dataclass(frozen=True)
class Vendor:
    name: str
    street: str
    city: str
    country: str
    vat_number: str
    iban: str
    bic: str
    currency: str


VENDORS: List[Vendor] = [
    Vendor(
        name="Nordisk Kontorsservice AB",
        street="Klarabergsgatan 12",
        city="111 21 Stockholm",
        country="Sweden",
        vat_number="SE556712345601",
        iban="SE4550000000058398257466",
        bic="ESSESESS",
        currency="SEK",
    ),
    Vendor(
        name="Svea Teknikpartner AB",
        street="Östra Hamngatan 44",
        city="411 09 Göteborg",
        country="Sweden",
        vat_number="SE556823456701",
        iban="SE3550000000054910000003",
        bic="SWEDSESS",
        currency="SEK",
    ),
    Vendor(
        name="MälarData Solutions AB",
        street="Kungsgatan 18",
        city="722 11 Västerås",
        country="Sweden",
        vat_number="SE556934567801",
        iban="SE9250000000052023456789",
        bic="HANDSESS",
        currency="SEK",
    ),
    Vendor(
        name="GreenGrid Logistics AB",
        street="Stora Nygatan 7",
        city="211 37 Malmö",
        country="Sweden",
        vat_number="SE556845678901",
        iban="SE1450000000057865432109",
        bic="NDEASESS",
        currency="SEK",
    ),
    Vendor(
        name="Altura Consulting AB",
        street="Drottninggatan 55",
        city="602 32 Norrköping",
        country="Sweden",
        vat_number="SE556756789012",
        iban="SE6650000000051122334455",
        bic="SWEDSESS",
        currency="SEK",
    ),
    Vendor(
        name="Baltic Cloud Services OÜ",
        street="Pärnu mnt 22",
        city="10141 Tallinn",
        country="Estonia",
        vat_number="EE102345678",
        iban="EE382200221020145685",
        bic="HABAEE2X",
        currency="EUR",
    ),
    Vendor(
        name="NorthPeak Software Oy",
        street="Mannerheimintie 14",
        city="00100 Helsinki",
        country="Finland",
        vat_number="FI23456789",
        iban="FI2112345600000785",
        bic="NDEAFIHH",
        currency="EUR",
    ),
]

CUSTOMERS = [
    ("VASS Demo Client AB", "Ringvägen 101", "118 60 Stockholm", "Sweden"),
    ("Scandic Retail Group AB", "Torsgatan 6", "113 21 Stockholm", "Sweden"),
    ("Aurora Operations AB", "Kungsportsavenyen 3", "411 36 Göteborg", "Sweden"),
    ("BlueHarbor Manufacturing AB", "Skeppsbron 24", "211 20 Malmö", "Sweden"),
]

ITEM_CATALOG = [
    "Managed services support",
    "Cloud hosting fee",
    "Software subscription",
    "Implementation workshop",
    "Advisory hours",
    "On-site consulting",
    "Integration maintenance",
    "Project coordination",
    "Service desk package",
    "Data processing support",
    "License renewal",
    "Automation design session",
]

PAYMENT_TERMS = [10, 15, 20, 30]
VAT_RATES = [0.06, 0.12, 0.25]


def format_amount(value: float, currency: str) -> str:
    if currency == "SEK":
        return f"{value:,.2f} SEK".replace(",", " ").replace(".", ",")
    return f"{value:,.2f} EUR"


def random_invoice_date(rng: random.Random) -> date:
    today = date.today()
    return today - timedelta(days=rng.randint(5, 120))


def make_invoice_id(rng: random.Random, idx: int) -> str:
    return f"INV-{date.today().year}-{idx:03d}-{rng.randint(1000, 9999)}"


def make_po_number(rng: random.Random) -> str:
    return f"PO-{rng.randint(10000, 99999)}"


def generate_line_items(rng: random.Random) -> list[dict]:
    items = []
    item_count = rng.randint(2, 5)
    for _ in range(item_count):
        description = rng.choice(ITEM_CATALOG)
        qty = rng.randint(1, 8)
        unit_price = round(rng.uniform(350, 4200), 2)
        line_total = round(qty * unit_price, 2)
        items.append(
            {
                "description": description,
                "qty": qty,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )
    return items


def wrap_text(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, font="Helvetica", font_size=10, line_gap=12):
    words = text.split()
    current = ""
    lines = []
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    c.setFont(font, font_size)
    current_y = y
    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= line_gap
    return current_y


def draw_invoice_pdf(output_path: Path, payload: dict) -> None:
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    left = 18 * mm
    right = width - 18 * mm
    top = height - 18 * mm

    c.setTitle(payload["invoice_id"])
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left, top, "INVOICE")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, top - 18, payload["vendor_name"])
    c.setFont("Helvetica", 10)
    c.drawString(left, top - 34, payload["vendor_street"])
    c.drawString(left, top - 48, payload["vendor_city"])
    c.drawString(left, top - 62, payload["vendor_country"])
    c.drawString(left, top - 76, f"VAT No: {payload['vendor_vat_number']}")
    c.drawString(left, top - 90, f"IBAN: {payload['iban']}")
    c.drawString(left, top - 104, f"BIC: {payload['bic']}")

    box_x = right - 70 * mm
    box_y = top - 8
    c.rect(box_x, box_y - 52 * mm, 70 * mm, 52 * mm)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(box_x + 6, box_y - 16, "Invoice details")
    c.setFont("Helvetica", 9)
    detail_lines = [
        f"Invoice ID: {payload['invoice_id']}",
        f"Invoice date: {payload['invoice_date']}",
        f"Due date: {payload['due_date']}",
        f"PO number: {payload['po_number']}",
        f"Currency: {payload['currency']}",
    ]
    detail_y = box_y - 30
    for line in detail_lines:
        c.drawString(box_x + 6, detail_y, line)
        detail_y -= 12

    bill_y = top - 135
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, bill_y, "Bill to")
    c.setFont("Helvetica", 10)
    c.drawString(left, bill_y - 16, payload["customer_name"])
    c.drawString(left, bill_y - 30, payload["customer_street"])
    c.drawString(left, bill_y - 44, payload["customer_city"])
    c.drawString(left, bill_y - 58, payload["customer_country"])

    table_top = bill_y - 90
    c.setLineWidth(0.8)
    c.rect(left, table_top - 8 * mm, right - left, 10 * mm, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left + 4, table_top - 4, "Description")
    c.drawString(left + 95 * mm, table_top - 4, "Qty")
    c.drawString(left + 115 * mm, table_top - 4, "Unit price")
    c.drawString(left + 150 * mm, table_top - 4, "Line total")

    y = table_top - 16
    c.setFont("Helvetica", 9)
    for item in payload["line_items"]:
        y = wrap_text(c, item["description"], left + 4, y, max_width=88 * mm, font_size=9, line_gap=10)
        c.drawRightString(left + 108 * mm, y + 10, str(item["qty"]))
        c.drawRightString(left + 146 * mm, y + 10, format_amount(item["unit_price"], payload["currency"]))
        c.drawRightString(right - 8, y + 10, format_amount(item["line_total"], payload["currency"]))
        y -= 8

    summary_y = max(y - 10, 55 * mm)
    summary_x = right - 62 * mm
    c.rect(summary_x, summary_y - 28 * mm, 62 * mm, 28 * mm)

    c.setFont("Helvetica", 10)
    c.drawString(summary_x + 6, summary_y - 14, "Subtotal")
    c.drawRightString(right - 8, summary_y - 14, format_amount(payload["subtotal"], payload["currency"]))
    c.drawString(summary_x + 6, summary_y - 28, f"VAT ({payload['vat_rate_pct']}%)")
    c.drawRightString(right - 8, summary_y - 28, format_amount(payload["tax"], payload["currency"]))

    c.setFont("Helvetica-Bold", 11)
    c.drawString(summary_x + 6, summary_y - 46, "Total")
    c.drawRightString(right - 8, summary_y - 46, format_amount(payload["total"], payload["currency"]))

    footer_y = 22 * mm
    c.setFont("Helvetica", 9)
    c.drawString(left, footer_y + 18, "Payment instructions")
    c.drawString(left, footer_y + 6, "Please include the invoice ID as payment reference.")
    c.drawString(left, footer_y - 6, f"Payment terms: Net {payload['payment_terms_days']} days")
    c.drawString(left, footer_y - 18, "Thank you for your business.")

    c.showPage()
    c.save()


def build_invoice_payload(rng: random.Random, idx: int) -> dict:
    vendor = rng.choice(VENDORS)
    customer_name, customer_street, customer_city, customer_country = rng.choice(CUSTOMERS)

    invoice_dt = random_invoice_date(rng)
    payment_terms_days = rng.choice(PAYMENT_TERMS)
    due_dt = invoice_dt + timedelta(days=payment_terms_days)
    line_items = generate_line_items(rng)

    subtotal = round(sum(item["line_total"] for item in line_items), 2)
    vat_rate = rng.choice(VAT_RATES)
    tax = round(subtotal * vat_rate, 2)
    total = round(subtotal + tax, 2)

    payload = {
        "vendor_name": vendor.name,
        "vendor_street": vendor.street,
        "vendor_city": vendor.city,
        "vendor_country": vendor.country,
        "vendor_vat_number": vendor.vat_number,
        "iban": vendor.iban,
        "bic": vendor.bic,
        "customer_name": customer_name,
        "customer_street": customer_street,
        "customer_city": customer_city,
        "customer_country": customer_country,
        "invoice_id": make_invoice_id(rng, idx),
        "invoice_date": invoice_dt.isoformat(),
        "due_date": due_dt.isoformat(),
        "payment_terms_days": payment_terms_days,
        "po_number": make_po_number(rng),
        "currency": vendor.currency,
        "line_items": line_items,
        "subtotal": subtotal,
        "vat_rate_pct": int(vat_rate * 100),
        "tax": tax,
        "total": total,
        "category": "clean",
        "expected_outcome": "Approved",
        "notes": "Clean synthetic invoice for baseline extraction tests.",
    }
    return payload


def write_ground_truth(csv_path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "file_name",
        "expected_vendor_name",
        "expected_invoice_id",
        "expected_invoice_date",
        "expected_due_date",
        "expected_currency",
        "expected_subtotal",
        "expected_tax",
        "expected_total",
        "expected_vat_number",
        "expected_category",
        "expected_outcome",
        "notes",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_invoices(output_dir: Path, csv_path: Path, count: int, seed: int | None = None) -> None:
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for idx in range(1, count + 1):
        payload = build_invoice_payload(rng, idx)
        file_name = f"INV_CLEAN_{idx:03d}.pdf"
        output_path = output_dir / file_name
        draw_invoice_pdf(output_path, payload)

        rows.append(
            {
                "file_name": file_name,
                "expected_vendor_name": payload["vendor_name"],
                "expected_invoice_id": payload["invoice_id"],
                "expected_invoice_date": payload["invoice_date"],
                "expected_due_date": payload["due_date"],
                "expected_currency": payload["currency"],
                "expected_subtotal": f"{payload['subtotal']:.2f}",
                "expected_tax": f"{payload['tax']:.2f}",
                "expected_total": f"{payload['total']:.2f}",
                "expected_vat_number": payload["vendor_vat_number"],
                "expected_category": payload["category"],
                "expected_outcome": payload["expected_outcome"],
                "notes": payload["notes"],
            }
        )

    write_ground_truth(csv_path, rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic invoice PDFs and a ground-truth CSV.")
    parser.add_argument("--count", type=int, default=10, help="Number of invoices to generate. Default: 10")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/generated_invoices"),
        help="Directory where PDF invoices are written. Default: data/generated_invoices",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=Path("data/expected_outputs/invoice_ground_truth_clean.csv"),
        help="Path to the output ground-truth CSV. Default: data/expected_outputs/invoice_ground_truth_clean.csv",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible output. Default: 42")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be at least 1")
    generate_invoices(
        output_dir=args.output_dir,
        csv_path=args.csv_path,
        count=args.count,
        seed=args.seed,
    )
    print(f"Generated {args.count} invoice PDFs in: {args.output_dir}")
    print(f"Ground truth CSV written to: {args.csv_path}")


if __name__ == "__main__":
    main()
