import pandas as pd

from app.processing.analytics import build_analysis
from app.processing.profitability import _normalize_number
from app.processing.report_catalog import get_report_definition


COMMON_TOTAL_FIELDS = ["revenue", "cost", "commission", "shipping", "ads_spend"]


def _numeric(df: pd.DataFrame, mapping: dict[str, str], field: str) -> pd.Series:
    column = mapping.get(field)
    if not column:
        return pd.Series([0] * len(df), index=df.index, dtype="float64")
    return df[column].map(_normalize_number).astype("float64")


def _text(df: pd.DataFrame, mapping: dict[str, str], field: str, fallback: str) -> pd.Series:
    column = mapping.get(field)
    if not column:
        return pd.Series([fallback] * len(df), index=df.index, dtype="object")
    return df[column].fillna(fallback).astype(str).str.strip().replace("", fallback)


def _base_frame(df: pd.DataFrame, label: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame(index=df.index)
    frame["product_name"] = label
    for field in COMMON_TOTAL_FIELDS:
        frame[field] = 0.0
    return frame


def _finish_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame["net_profit"] = (
        frame["revenue"]
        - frame["cost"]
        - frame["commission"]
        - frame["shipping"]
        - frame["ads_spend"]
    )
    revenue = frame["revenue"].where(frame["revenue"] != 0)
    frame["profit_margin"] = ((frame["net_profit"] / revenue) * 100).fillna(0)
    return frame


def _product_level_profit(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        frame.groupby("product_name", dropna=False)[
            ["revenue", "cost", "commission", "shipping", "ads_spend", "net_profit"]
        ]
        .sum()
        .reset_index()
    )
    revenue = grouped["revenue"].where(grouped["revenue"] != 0)
    grouped["profit_margin"] = ((grouped["net_profit"] / revenue) * 100).fillna(0)
    return grouped.sort_values("net_profit", ascending=False)


def build_report_analysis(df: pd.DataFrame, mapping: dict[str, str], report_type: str) -> dict:
    report = get_report_definition(report_type)

    if report.id == "profitability":
        from app.processing.profitability import build_profitability_frame, product_level_profit

        order_frame = build_profitability_frame(df, mapping)
        product_frame = product_level_profit(order_frame)
    elif report.id == "income_expense":
        label = _text(df, mapping, "category", "Income / Expense")
        order_frame = _base_frame(df, label)
        income = _numeric(df, mapping, "income")
        expense = _numeric(df, mapping, "expense")
        amount = _numeric(df, mapping, "amount")
        type_text = _text(df, mapping, "type", "").str.lower()
        income_mask = type_text.str.contains("income|gelir|revenue|ciro", regex=True)
        expense_mask = type_text.str.contains("expense|gider|cost|maliyet", regex=True)
        order_frame["revenue"] = income.where(income != 0, amount.where(income_mask | (amount > 0), 0))
        order_frame["cost"] = expense.where(expense != 0, amount.abs().where(expense_mask | (amount < 0), 0))
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    elif report.id == "ads_performance":
        label = _text(df, mapping, "product_name", "").replace("", pd.NA).fillna(
            _text(df, mapping, "campaign", "Campaign")
        )
        order_frame = _base_frame(df, label)
        order_frame["revenue"] = _numeric(df, mapping, "revenue")
        order_frame["ads_spend"] = _numeric(df, mapping, "ads_spend")
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    elif report.id == "sales_performance":
        order_frame = _base_frame(df, _text(df, mapping, "product_name", "Product"))
        order_frame["revenue"] = _numeric(df, mapping, "revenue")
        order_frame["cost"] = _numeric(df, mapping, "discount")
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    elif report.id == "shipping_logistics":
        order_frame = _base_frame(df, _text(df, mapping, "product_name", "Shipping"))
        order_frame["revenue"] = _numeric(df, mapping, "revenue")
        order_frame["shipping"] = _numeric(df, mapping, "shipping")
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    elif report.id == "returns_cancellations":
        order_frame = _base_frame(df, _text(df, mapping, "product_name", "Returns"))
        order_frame["revenue"] = _numeric(df, mapping, "revenue")
        order_frame["cost"] = _numeric(df, mapping, "return_amount")
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    elif report.id == "inventory":
        order_frame = _base_frame(df, _text(df, mapping, "product_name", "Inventory"))
        stock = _numeric(df, mapping, "stock")
        unit_cost = _numeric(df, mapping, "unit_cost")
        inventory_value = _numeric(df, mapping, "inventory_value")
        order_frame["cost"] = inventory_value.where(inventory_value != 0, stock * unit_cost)
        order_frame = _finish_frame(order_frame)
        product_frame = _product_level_profit(order_frame)
    else:
        raise ValueError(f"Unsupported report type: {report_type}")

    analysis = build_analysis(order_frame, product_frame)
    analysis["report_type"] = report.id
    analysis["report_label_tr"] = report.label_tr
    analysis["report_label_en"] = report.label_en
    analysis["row_count"] = int(len(df))
    return analysis
