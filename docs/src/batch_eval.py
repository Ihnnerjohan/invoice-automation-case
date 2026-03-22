from pathlib import Path
import math
import pandas as pd

from process_invoice import process_invoice


BASE_DIR = Path(__file__).resolve().parents[2]
INVOICE_DIR = BASE_DIR / "data" / "generated_invoices"
GROUND_TRUTH_PATH = BASE_DIR / "data" / "expected_outputs" / "invoice_ground_truth_clean.csv"
PREDICTIONS_PATH = BASE_DIR / "data" / "expected_outputs" / "predictions.csv"
COMPARISON_RESULTS_PATH = BASE_DIR / "data" / "expected_outputs" / "comparison_results.csv"


def run_invoice_pipeline(pdf_path: Path, seen_invoices=None) -> dict:
    result = process_invoice(str(pdf_path), seen_invoices=seen_invoices)
    result["filename"] = pdf_path.name
    return result


def batch_process_invoices(invoice_dir: Path) -> pd.DataFrame:
    """
    Kör pipeline på alla PDF-filer i katalogen.
    Returnerar DataFrame med predictions.
    """
    results = []
    seen_invoices = []

    pdf_files = sorted(invoice_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"Inga PDF-filer hittades i {invoice_dir}")

    for pdf_path in pdf_files:
        try:
            result = run_invoice_pipeline(pdf_path, seen_invoices=seen_invoices)
            results.append(result)

            # Lägg bara till invoices som har tillräckligt med data för duplicate check
            if (
                result.get("invoice_number")
                and result.get("vendor")
                and result.get("total_amount") is not None
            ):
                seen_invoices.append(result)

            print(f"[OK] {pdf_path.name}")
        except Exception as e:
            print(f"[ERROR] {pdf_path.name}: {e}")
            results.append({
                "filename": pdf_path.name,
                "invoice_number": None,
                "vendor": None,
                "invoice_date": None,
                "due_date": None,
                "total_amount": None,
                "status": "Needs review",
                "validation_reason": "Processing failed",
                "is_duplicate": False,
                "duplicate_reason": "",
                "duplicate_match_file": "",
                "duplicate_rule_type": None,
                "processing_error": str(e),
            })

    return pd.DataFrame(results)


def load_ground_truth(csv_path: Path) -> pd.DataFrame:
    """
    Läser ground truth CSV och mappar kolumnnamn till eval-format.
    """
    df = pd.read_csv(csv_path)

    print("\n=== GROUND TRUTH COLUMNS ===")
    print(df.columns.tolist())

    rename_map = {
        "file_name": "filename",
        "expected_vendor_name": "vendor",
        "expected_invoice_id": "invoice_number",
        "expected_invoice_date": "invoice_date",
        "expected_due_date": "due_date",
        "expected_total": "total_amount",
    }

    df = df.rename(columns=rename_map)

    required_columns = [
        "filename",
        "invoice_number",
        "vendor",
        "invoice_date",
        "due_date",
        "total_amount",
        "expected_is_duplicate",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"ground truth CSV saknar kolumner efter rename: {missing}. "
            f"Tillgängliga kolumner: {df.columns.tolist()}"
        )

    return df[required_columns]


def normalize_ground_truth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliserar ground truth så att jämförelsen blir rättvis.
    """
    df = df.copy()

    for col in ["invoice_number", "vendor", "invoice_date", "due_date"]:
        df[col] = df[col].astype(str).str.strip()

    df["vendor"] = df["vendor"].str.lower()

    for col in ["invoice_date", "due_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df["expected_is_duplicate"] = (
        df["expected_is_duplicate"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
        })
    )

    if df["expected_is_duplicate"].isna().any():
        invalid_rows = df[df["expected_is_duplicate"].isna()]["filename"].tolist()
        raise ValueError(
            "Ogiltiga värden i expected_is_duplicate för filer: "
            f"{invalid_rows}. Använd True/False eller true/false."
        )

    return df


def normalize_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliserar predictions inför jämförelse.
    """
    df = df.copy()

    for col in ["invoice_number", "vendor", "invoice_date", "due_date"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "vendor" in df.columns:
        df["vendor"] = df["vendor"].str.lower()

    for col in ["invoice_date", "due_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    if "total_amount" in df.columns:
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

    if "is_duplicate" in df.columns:
        df["is_duplicate"] = df["is_duplicate"].fillna(False).astype(bool)

    if "duplicate_rule_type" not in df.columns:
        df["duplicate_rule_type"] = None

    return df


def compare_amounts(a, b, tolerance: float = 0.01) -> bool:
    """
    Jämför float-belopp med liten tolerans.
    """
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), abs_tol=tolerance)


def label_duplicate_eval(row) -> str:
    predicted = bool(row["is_duplicate"])
    expected = bool(row["expected_is_duplicate"])

    if predicted and expected:
        return "TP"
    if predicted and not expected:
        return "FP"
    if not predicted and expected:
        return "FN"
    return "TN"


def compare_predictions(pred_df: pd.DataFrame, gt_df: pd.DataFrame) -> pd.DataFrame:
    """
    Joinar predictions med ground truth och skapar match-kolumner.
    """
    pred_df = normalize_predictions(pred_df)
    gt_df = normalize_ground_truth(gt_df)

    merged = pred_df.merge(
        gt_df,
        on="filename",
        how="outer",
        suffixes=("_pred", "_true"),
        indicator=True,
    )

    merged["invoice_number_match"] = (
        merged["invoice_number_pred"] == merged["invoice_number_true"]
    )
    merged["vendor_match"] = (
        merged["vendor_pred"] == merged["vendor_true"]
    )
    merged["invoice_date_match"] = (
        merged["invoice_date_pred"] == merged["invoice_date_true"]
    )
    merged["due_date_match"] = (
        merged["due_date_pred"] == merged["due_date_true"]
    )

    merged["total_amount_match"] = merged.apply(
        lambda row: compare_amounts(row["total_amount_pred"], row["total_amount_true"]),
        axis=1,
    )

    merged["all_fields_match"] = (
        merged["invoice_number_match"]
        & merged["vendor_match"]
        & merged["invoice_date_match"]
        & merged["due_date_match"]
        & merged["total_amount_match"]
    )

    merged["is_duplicate"] = merged["is_duplicate"].fillna(False).astype(bool)
    merged["expected_is_duplicate"] = merged["expected_is_duplicate"].fillna(False).astype(bool)
    merged["duplicate_match"] = merged["is_duplicate"] == merged["expected_is_duplicate"]
    merged["duplicate_eval_label"] = merged.apply(label_duplicate_eval, axis=1)

    return merged


def compute_accuracy_report(comparison_df: pd.DataFrame) -> dict:
    """
    Räknar accuracy per fält och overall.
    """
    matched_rows = comparison_df[comparison_df["_merge"] == "both"]

    if matched_rows.empty:
        raise ValueError("Inga matchande filename mellan predictions och ground truth.")

    report = {
        "num_compared": len(matched_rows),
        "invoice_number_accuracy": matched_rows["invoice_number_match"].mean(),
        "vendor_accuracy": matched_rows["vendor_match"].mean(),
        "invoice_date_accuracy": matched_rows["invoice_date_match"].mean(),
        "due_date_accuracy": matched_rows["due_date_match"].mean(),
        "total_amount_accuracy": matched_rows["total_amount_match"].mean(),
        "overall_document_accuracy": matched_rows["all_fields_match"].mean(),
    }

    return report


def compute_duplicate_report(comparison_df: pd.DataFrame) -> dict:
    """
    Räknar duplicate detection metrics.
    """
    matched_rows = comparison_df[comparison_df["_merge"] == "both"]

    if matched_rows.empty:
        raise ValueError("Inga matchande filename mellan predictions och ground truth.")

    tp = int((matched_rows["duplicate_eval_label"] == "TP").sum())
    fp = int((matched_rows["duplicate_eval_label"] == "FP").sum())
    fn = int((matched_rows["duplicate_eval_label"] == "FN").sum())
    tn = int((matched_rows["duplicate_eval_label"] == "TN").sum())

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    accuracy = (tp + tn) / len(matched_rows) if len(matched_rows) else 0.0

    return {
        "duplicate_precision": precision,
        "duplicate_recall": recall,
        "duplicate_accuracy": accuracy,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
    }


def print_report(report: dict) -> None:
    print("\n=== ACCURACY REPORT ===")
    print(f"Documents compared:        {report['num_compared']}")
    print(f"invoice_number accuracy:   {report['invoice_number_accuracy']:.2%}")
    print(f"vendor accuracy:           {report['vendor_accuracy']:.2%}")
    print(f"invoice_date accuracy:     {report['invoice_date_accuracy']:.2%}")
    print(f"due_date accuracy:         {report['due_date_accuracy']:.2%}")
    print(f"total_amount accuracy:     {report['total_amount_accuracy']:.2%}")
    print(f"overall document accuracy: {report['overall_document_accuracy']:.2%}")


def print_duplicate_report(report: dict) -> None:
    print("\n=== DUPLICATE DETECTION REPORT ===")
    print(f"duplicate precision:       {report['duplicate_precision']:.2%}")
    print(f"duplicate recall:          {report['duplicate_recall']:.2%}")
    print(f"duplicate accuracy:        {report['duplicate_accuracy']:.2%}")
    print(f"true positives:            {report['true_positives']}")
    print(f"false positives:           {report['false_positives']}")
    print(f"false negatives:           {report['false_negatives']}")
    print(f"true negatives:            {report['true_negatives']}")


def print_duplicate_rule_breakdown(comparison_df: pd.DataFrame) -> None:
    matched_rows = comparison_df[comparison_df["_merge"] == "both"].copy()

    print("\n=== DUPLICATE RULE BREAKDOWN ===")

    if "duplicate_rule_type" not in matched_rows.columns:
        print("duplicate_rule_type saknas i comparison_df")
        return

    duplicate_rows = matched_rows[matched_rows["is_duplicate"] == True].copy()

    if duplicate_rows.empty:
        print("Inga duplicates att analysera.")
        return

    rule_counts = duplicate_rows["duplicate_rule_type"].fillna("None").value_counts(dropna=False)
    print(rule_counts.to_string())


def main():
    pred_df = batch_process_invoices(INVOICE_DIR)
    gt_df = load_ground_truth(GROUND_TRUTH_PATH)

    comparison_df = compare_predictions(pred_df, gt_df)
    extraction_report = compute_accuracy_report(comparison_df)
    duplicate_report = compute_duplicate_report(comparison_df)

    print_report(extraction_report)
    print_duplicate_report(duplicate_report)
    print_duplicate_rule_breakdown(comparison_df)

    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pred_df.to_csv(PREDICTIONS_PATH, index=False)
    comparison_df.to_csv(COMPARISON_RESULTS_PATH, index=False)

    print("\nSparade:")
    print(f"- {PREDICTIONS_PATH}")
    print(f"- {COMPARISON_RESULTS_PATH}")


if __name__ == "__main__":
    main()