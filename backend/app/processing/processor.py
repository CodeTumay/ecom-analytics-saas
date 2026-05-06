from pathlib import Path

import pandas as pd

from app.processing.analytics import build_analysis
from app.processing.column_mapping import detect_mapping, validate_user_mapping
from app.processing.profitability import build_profitability_frame, product_level_profit
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


def process_file(path: str | Path, user_mapping: dict[str, str] | None = None) -> dict:
    df = read_marketplace_file(path)
    if df.empty:
        raise ValueError("Uploaded file has no rows")

    mapping_result = (
        validate_user_mapping(df, user_mapping) if user_mapping else detect_mapping(df)
    )
    if mapping_result.needs_user_mapping:
        return {
            "status": "needs_mapping",
            "mapping": mapping_result.mapping,
            "columns": [str(column) for column in df.columns],
            "missing_required": mapping_result.missing_required,
            "missing_optional": mapping_result.missing_optional,
        }

    order_frame = build_profitability_frame(df, mapping_result.mapping)
    products = product_level_profit(order_frame)
    analysis = build_analysis(order_frame, products)
    analysis["insights"] = generate_insights(analysis)

    return {
        "status": "completed",
        "mapping": mapping_result.mapping,
        "analysis": analysis,
    }
