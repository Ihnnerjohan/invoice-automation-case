# Invoice Automation Case

A Python-based invoice automation pipeline for extracting structured data from PDF invoices, validating data, detecting duplicates, and evaluating results against ground truth.

This project represents a **validated baseline system** with fully tested behavior and measurable results.

---

## Project Overview

The system processes invoice PDFs and performs:

1. Text extraction from PDF invoices
2. AI-based field extraction
3. Data normalization and validation
4. Rule-based duplicate detection
5. End-to-end evaluation against ground truth

---

## Key Features

- PDF text extraction using `pdfplumber`
- AI-based structured field extraction
- Amount normalization across formats
- Validation rules for invoice correctness
- Explainable rule-based duplicate detection
- Batch processing and evaluation pipeline
- Ground truth comparison with metrics

---

## Pipeline

### 1. Text Extraction
Extract raw text from invoice PDFs.

### 2. AI Field Extraction
Extract:
- invoice_number
- vendor
- invoice_date
- due_date
- total_amount

### 3. Normalization
Handles formats like:
- 16,444.59
- 34 930,64
- currency strings

### 4. Validation
Rules:
- all fields must exist
- amount must be parseable
- amount <= 50,000

### 5. Duplicate Detection

Strong rule:
- same invoice_number

Fallback rule:
- same vendor
- same invoice_date
- same total_amount (±0.01)

### 6. Classification

if duplicate → Needs review  
if invalid → Needs review  
else → Approved  

---

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the environment template and add your API key (the `.env` file is gitignored):

```bash
cp .env.example .env
```

3. Set `OPENAI_API_KEY` in `.env` (loaded automatically via `python-dotenv`), or export it in your shell.

4. From project root:

```bash
python docs/src/batch_eval.py
```

This processes:

```text
data/generated_invoices/
```

And generates:

```text
data/expected_outputs/predictions.csv
data/expected_outputs/comparison_results.csv
```

---

## Results

### Extraction Accuracy

- invoice_number: 100%
- vendor: 100%
- invoice_date: 100%
- due_date: 100%
- total_amount: 100%
- overall: 100%

### Duplicate Detection

- precision: 100%
- recall: 100%
- accuracy: 100%

- true positives: 4
- false positives: 0
- false negatives: 0
- true negatives: 12

### Rule Breakdown

- invoice_number: 3
- vendor_amount_date: 1

---

## Dataset

- 16 invoices total
- clean invoices
- duplicates
- fallback duplicate case
- negative control case
- suspicious cases

---

## Limitations

- no vendor normalization
- no fuzzy matching
- no persistence across batches
- batch-order dependent
- small controlled dataset

---

## Future Improvements

- vendor normalization
- fuzzy matching
- persistence layer
- OCR support
- larger datasets
- fraud detection extensions

---

## Summary

This project demonstrates:

- a complete invoice processing pipeline
- fully validated behavior
- explainable duplicate detection
- measurable evaluation results

It is designed to be **simple, testable, and interview-ready**.
