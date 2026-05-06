from pathlib import Path

import pandas as pd

from app.processing.column_mapping import detect_mapping, validate_user_mapping
from app.processing.report_analysis import build_report_analysis
from app.processing.report_catalog import get_report_definition
from app.services.insights import generate_insights

CSV_ENCODINGS = ("utf-8-sig", "utf-8", "cp1254", "latin1")
CSV_SEPARATORS = (None, ";", ",", "\t", "|")


def _score_dataframe(df: pd.DataFrame) -> int:
    column_count = len(df.columns)
    filled_cells = int(
        df.astype(str)
        .apply(lambda column: column.str.strip().ne("").sum())
        .sum()
    )
    one_column_penalty = 500 if column_count <= 1 else 0
    return (column_count * 100) + filled_cells - one_column_penalty


def _read_csv_auto(path: Path) -> pd.DataFrame:
    candidates: list[tuple[int, pd.DataFrame]] = []
    last_error: Exception | None = None

    for encoding in CSV_ENCODINGS:
        for separator in CSV_SEPARATORS:
            try:
                df = pd.read_csv(
                    path,
                    sep=separator,
                    engine="python",
                    encoding=encoding,
                    dtype=str,
                    keep_default_na=False,
                )
            except Exception as exc:
                last_error = exc
                continue

            if len(df.columns) > 0:
                candidates.append((_score_dataframe(df), df))

    if not candidates:
        raise ValueError(f"Could not read CSV file: {last_error}")

    return max(candidates, key=lambda candidate: candidate[0])[1]


def read_marketplace_file(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if file_path.suffix.lower() == ".csv":
        return _read_csv_auto(file_path)
    if file_path.suffix.lower() == ".xlsx":
        return pd.read_excel(file_path)
    raise ValueError("Unsupported file type")


def _mapping_report_type(user_mapping: dict[str, str] | None, report_type: str | None) -> str:
    if report_type:
        return report_type
    if user_mapping:
        return str(user_mapping.get("__report_type") or "profitability")
    return "profitability"


def process_file(
    path: str | Path,
    user_mapping: dict[str, str] | None = None,
    report_type: str | None = None,
) -> dict:
    df = read_marketplace_file(path)
    if df.empty:
        raise ValueError("Uploaded file has no rows")

    selected_report_type = _mapping_report_type(user_mapping, report_type)
    report = get_report_definition(selected_report_type)
    clean_user_mapping = {
        key: value for key, value in (user_mapping or {}).items() if not key.startswith("__")
    }
    mapping_result = (
        validate_user_mapping(df, clean_user_mapping, selected_report_type)
        if clean_user_mapping
        else detect_mapping(df, selected_report_type)
    )
    if mapping_result.needs_user_mapping:
        return {
            "status": "needs_mapping",
            "report_type": report.id,
            "report_label_tr": report.label_tr,
            "report_label_en": report.label_en,
            "mapping": {"__report_type": report.id, **mapping_result.mapping},
            "columns": [str(column) for column in df.columns],
            "missing_required": mapping_result.missing_required,
            "missing_optional": mapping_result.missing_optional,
        }

    analysis = build_report_analysis(df, mapping_result.mapping, report.id)
    analysis["insights"] = generate_insights(analysis)

    return {
        "status": "completed",
        "report_type": report.id,
        "report_label_tr": report.label_tr,
        "report_label_en": report.label_en,
        "mapping": {"__report_type": report.id, **mapping_result.mapping},
        "analysis": analysis,
    }
