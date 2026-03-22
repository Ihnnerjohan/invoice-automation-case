# 04 – Test Results

## 1. Purpose

The purpose of this testing phase is to validate the correctness and reliability of the invoice processing pipeline.

Specifically, the evaluation focuses on:

- field extraction accuracy
- data normalization and validation
- duplicate detection logic
- end-to-end pipeline behavior

The system is evaluated as a **rule-based baseline**, where correctness, explainability, and traceability are prioritized over complexity.

---

## 2. Test Setup

### Input Data

Invoices are stored in:

```text
data/generated_invoices/
```

The dataset includes the following file groups:

- `INV_CLEAN_*` → standard valid invoices
- `INV_DUP_*` → exact duplicate cases
- `INV_SUSP_*` → suspicious / edge duplicate scenarios
- `INV_NONDUP_*` → negative control case

### Ground Truth

Expected outputs are defined in:

```text
data/expected_outputs/invoice_ground_truth_clean.csv
```

### Execution

Batch processing is executed through:

```text
src/batch_eval.py
```

The batch evaluation script processes all invoice PDFs sequentially and generates:

- `predictions.csv`
- `comparison_results.csv`

---

## 3. Dataset Description

The evaluation dataset contains **16 invoices** in total.

### Dataset composition

- 10 clean invoices
- 3 exact duplicates detected by invoice number
- 1 hidden duplicate detected by fallback rule
- 1 negative control invoice
- 2 suspicious scenario invoices

The dataset is intentionally small but fully controlled, making it suitable for validating correctness and expected system behavior.

---

## 4. Extraction Results

The extraction pipeline achieved the following results:

| Metric | Score |
|---|---:|
| invoice_number_accuracy | 100% |
| vendor_accuracy | 100% |
| invoice_date_accuracy | 100% |
| due_date_accuracy | 100% |
| total_amount_accuracy | 100% |
| overall_document_accuracy | 100% |

### Interpretation

The extraction component correctly retrieved all required fields for all invoices in the evaluation set.

This indicates that:

- PDF text extraction worked reliably for the current invoice set
- the AI-based field extraction step returned correct structured values
- normalization handled supported amount formats correctly

---

## 5. Validation Results

Validation is applied after extraction and normalization.

### Validation rules

An invoice is considered valid only if:

- all required fields are present
- `total_amount` can be parsed successfully
- `total_amount` is not greater than 50,000

### Validation outcome

The validation layer worked as expected within the evaluated dataset and correctly supported downstream duplicate detection and final classification.

---

## 6. Duplicate Detection Results

Duplicate detection performance on the dataset:

| Metric | Value |
|---|---:|
| Precision | 100% |
| Recall | 100% |
| Accuracy | 100% |

Confusion matrix counts:

| Category | Count |
|---|---:|
| True Positives | 4 |
| False Positives | 0 |
| False Negatives | 0 |
| True Negatives | 12 |

### Interpretation

The duplicate detection logic performed perfectly on the controlled test dataset.

This means:

- no duplicate invoices were missed
- no valid non-duplicate invoices were incorrectly flagged
- the rule-based approach behaved consistently and conservatively

---

## 7. Duplicate Rule Breakdown

Detected duplicates by rule type:

| Rule Type | Count |
|---|---:|
| invoice_number | 3 |
| vendor_amount_date | 1 |

### Rule Definitions

**Strong rule**
- same `invoice_number`

**Fallback rule**
- same `vendor`
- same `total_amount` (±0.01 tolerance)
- same `invoice_date`

### Interpretation

Most duplicate cases were detected using the strong identifier rule.

One duplicate case was correctly detected through the fallback rule, demonstrating that the system can identify hidden duplicates even when the invoice number differs.

This improves robustness while keeping the logic simple and explainable.

---

## 8. Test Scenarios Covered

The system was explicitly tested against positive, fallback, and negative scenarios.

### Positive cases

- exact duplicates with the same invoice number
- hidden duplicate case with different invoice number but matching vendor, amount, and invoice date

### Fallback validation case

A duplicate with a different invoice number was correctly identified using the fallback rule:

- same vendor
- same invoice date
- same total amount

### Negative control case

A control invoice was included with:

- same vendor
- same invoice date
- different total amount

This invoice was correctly **not flagged** as a duplicate.

### Behavioral checks

The system was also validated for the following behavior:

- only valid invoices are considered for duplicate detection
- only previously processed invoices are used for comparison
- first occurrence is treated as non-duplicate
- later occurrence is treated as duplicate

---

## 9. End-to-End Classification Behavior

Final document classification is based on validation and duplicate detection:

```python
if duplicate:
    status = "Needs review"
elif not valid:
    status = "Needs review"
else:
    status = "Approved"
```

### Observed behavior

- valid non-duplicate invoices were classified as **Approved**
- duplicate invoices were classified as **Needs review**
- invalid invoices were classified as **Needs review**

This confirms that the full processing pipeline behaves consistently from input document to final status decision.

---

## 10. Limitations

The current system is intentionally simple and has known limitations.

### No vendor normalization

Vendor names must match exactly.  
For example, `IBM` and `IBM AB` would currently be treated as different vendors.

### Batch-order dependency

Duplicate detection only compares the current invoice with invoices already processed in the same batch.  
This means results depend on processing order.

### No persistence layer

Seen invoices are stored only in memory during runtime.  
Duplicates cannot currently be detected across separate runs.

### No fuzzy matching

Matching is rule-based and exact, except for a small tolerance in amount comparison.

### Small controlled dataset

The current results are based on a small and intentionally structured dataset.  
Additional testing would be required to confirm performance on noisy real-world invoices.

---

## 11. Future Improvements

Potential future enhancements include:

- vendor normalization
- fuzzy matching for vendor names
- persistence for cross-batch duplicate detection
- OCR support for scanned invoices
- larger and more diverse evaluation datasets
- anomaly or fraud detection extensions
- optional ML-based duplicate detection for more complex cases

These improvements were intentionally excluded from the baseline version in order to keep the solution simple, testable, and explainable.

---

## 12. Conclusion

The invoice automation system has been validated as a **tested baseline solution** for invoice extraction, validation, and duplicate detection.

The evaluation demonstrates:

- 100% field extraction accuracy
- 100% duplicate detection precision
- 100% duplicate detection recall
- clear and explainable duplicate rules
- successful handling of both positive and negative test scenarios

This confirms that the current system is not just a prototype, but a validated baseline that is strong enough to document, present, extend, and discuss in an interview setting.
