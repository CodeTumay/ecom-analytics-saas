from pathlib import Path

import pandas as pd

from app.processing.analytics import build_analysis
from app.processing.column_mapping import detect_mapping, validate_user_mapping
from app.processing.profitability import build_profitability_frame, product_level_profit
from app.services.insights import generate_insights


def read_marketplace_file(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)
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
