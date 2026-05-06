from typing import Any

import pandas as pd

from app.processing.analytics import build_analysis
from app.processing.profitability import _normalize_number
from app.processing.report_catalog import get_report_definition


COMMON_TOTAL_FIELDS = ["revenue", "cost", "commission", "shipping", "ads_spend"]


def _numeric(df: pd.DataFrame, mapping: dict[str, str], field: str) -> pd.Series:
    column = mapping.get(field)
    if not column or column not in df.columns:
        return pd.Series([0.0] * len(df), index=df.index, dtype="float64")
    return df[column].map(_normalize_number).astype("float64").fillna(0)


def _text(df: pd.DataFrame, mapping: dict[str, str], field: str, fallback: str) -> pd.Series:
    column = mapping.get(field)
    if not column or column not in df.columns:
        return pd.Series([fallback] * len(df), index=df.index, dtype="object")
    return df[column].fillna(fallback).astype(str).str.strip().replace("", fallback)


def _safe_divide(numerator: pd.Series, denominator: pd.Series, multiplier: float = 1.0) -> pd.Series:
    clean_denominator = denominator.where(denominator != 0)
    return ((numerator / clean_denominator) * multiplier).replace([float("inf"), -float("inf")], 0).fillna(0)


def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0


def _base_frame(df: pd.DataFrame, label: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame(index=df.index)
    frame["product_name"] = label.fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    for field in COMMON_TOTAL_FIELDS:
        frame[field] = 0.0
    return frame


def _finish_frame(frame: pd.DataFrame) -> pd.DataFrame:
    for field in COMMON_TOTAL_FIELDS:
        if field not in frame:
            frame[field] = 0.0
        frame[field] = frame[field].astype("float64").fillna(0)

    frame["net_profit"] = (
        frame["revenue"]
        - frame["cost"]
        - frame["commission"]
        - frame["shipping"]
        - frame["ads_spend"]
    )
    frame["profit_margin"] = _safe_divide(frame["net_profit"], frame["revenue"], 100)
    return frame


def _product_level_profit(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        frame.groupby("product_name", dropna=False)[
            ["revenue", "cost", "commission", "shipping", "ads_spend", "net_profit"]
        ]
        .sum()
        .reset_index()
    )
    grouped["profit_margin"] = _safe_divide(grouped["net_profit"], grouped["revenue"], 100)
    return grouped.sort_values("net_profit", ascending=False)


def _first_non_zero(primary: pd.Series, fallback: pd.Series) -> pd.Series:
    return primary.where(primary != 0, fallback)


def _detail_records(frame: pd.DataFrame, limit: int = 500) -> list[dict[str, Any]]:
    clean = frame.head(limit).copy()
    clean = clean.replace([float("inf"), -float("inf")], 0).fillna("")
    for column in clean.select_dtypes(include="number").columns:
        clean[column] = clean[column].round(2)
    return clean.to_dict(orient="records")


def _add_common_metadata(analysis: dict, report_id: str, df: pd.DataFrame, detail: pd.DataFrame) -> dict:
    report = get_report_definition(report_id)
    analysis["report_type"] = report.id
    analysis["report_label_tr"] = report.label_tr
    analysis["report_label_en"] = report.label_en
    analysis["row_count"] = int(len(df))
    analysis["detail_rows"] = _detail_records(detail)
    analysis["logic_tr"] = list(report.logic_tr)
    analysis["logic_en"] = list(report.logic_en)
    return analysis


def _retail_intelligence(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "product_name", "Product"))
    revenue = _numeric(df, mapping, "revenue")
    cost = _numeric(df, mapping, "cost")
    units_sold = _numeric(df, mapping, "units_sold")
    stock = _numeric(df, mapping, "stock")
    store_sqm = _numeric(df, mapping, "store_sqm")
    inventory_value = _numeric(df, mapping, "inventory_value")

    frame["revenue"] = revenue
    frame["cost"] = cost
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["date"] = _text(df, mapping, "date", "")
    detail["store_name"] = _text(df, mapping, "store_name", "")
    detail["channel"] = _text(df, mapping, "channel", "")
    detail["sku"] = _text(df, mapping, "sku", "")
    detail["collection"] = _text(df, mapping, "collection", "")
    detail["category"] = _text(df, mapping, "category", "")
    detail["material"] = _text(df, mapping, "material", "")
    detail["units_sold"] = units_sold
    detail["selling_price"] = _first_non_zero(_numeric(df, mapping, "selling_price"), _safe_divide(revenue, units_sold))
    detail["stock"] = stock
    detail["footfall"] = _numeric(df, mapping, "footfall")
    detail["conversion_rate"] = _first_non_zero(
        _numeric(df, mapping, "conversion_rate"),
        _safe_divide(units_sold, detail["footfall"], 100),
    )
    detail["sell_through"] = _first_non_zero(
        _numeric(df, mapping, "sell_through"),
        _safe_divide(units_sold, units_sold + stock, 100),
    )
    detail["stock_turnover"] = _safe_divide(units_sold, stock)
    detail["days_of_stock"] = _safe_divide(stock, units_sold / 30)
    detail["store_sqm"] = store_sqm
    detail["revenue_per_sqm"] = _safe_divide(revenue, store_sqm)
    detail["inventory_value"] = _first_non_zero(inventory_value, stock * cost)
    detail["retail_action"] = detail.apply(_retail_action, axis=1)
    return frame, _product_level_profit(frame), detail


def _retail_action(row: pd.Series) -> str:
    margin = _number(row.get("profit_margin"))
    sell_through = _number(row.get("sell_through"))
    days_of_stock = _number(row.get("days_of_stock"))
    stock_turnover = _number(row.get("stock_turnover"))
    inventory_value = _number(row.get("inventory_value"))
    revenue = _number(row.get("revenue"))

    if sell_through >= 70 and (days_of_stock <= 14 or days_of_stock == 0) and margin >= 20:
        return "Reorder / yeniden uret"
    if inventory_value > 0 and stock_turnover < 0.5:
        return "Markdown veya transfer"
    if revenue > 0 and margin >= 25:
        return "Hero product / buyut"
    if revenue > 0 and margin < 10:
        return "Marj kontrolu"
    return "Takip et"


REPORT_BUILDERS = {
    "retail_health": _retail_intelligence,
    "ceo_dashboard": _retail_intelligence,
    "store_performance": _retail_intelligence,
    "product_collection": _retail_intelligence,
    "reorder_transfer": _retail_intelligence,
    "investor_board": _retail_intelligence,
}


def build_report_analysis(df: pd.DataFrame, mapping: dict[str, str], report_type: str) -> dict:
    report = get_report_definition(report_type)
    builder = REPORT_BUILDERS.get(report.id)
    if builder is None:
        raise ValueError(f"Unsupported report type: {report_type}")

    order_frame, product_frame, detail = builder(df, mapping)
    analysis = build_analysis(order_frame, product_frame)
    return _add_common_metadata(analysis, report.id, df, detail)
