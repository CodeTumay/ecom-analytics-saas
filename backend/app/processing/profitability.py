from __future__ import annotations

import pandas as pd


NUMERIC_FIELDS = ["revenue", "cost", "commission", "shipping", "ads_spend"]


def _normalize_number(value: object) -> float:
    if value is None or pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().upper()
    if not text:
        return 0

    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = (
        text.replace("\u00a0", "")
        .replace(" ", "")
        .replace("TRY", "")
        .replace("TL", "")
        .replace("$", "")
        .replace("\u20ac", "")
        .replace("\u20ba", "")
        .replace("%", "")
    )

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        if len(parts[-1]) in {1, 2}:
            text = "".join(parts[:-1]).replace(".", "") + "." + parts[-1]
        else:
            text = text.replace(",", "")
    elif "." in text:
        parts = text.split(".")
        if len(parts) > 2 and len(parts[-1]) == 3:
            text = text.replace(".", "")

    try:
        number = float(text)
    except ValueError:
        return 0
    return -number if negative else number


def _series_or_zero(df: pd.DataFrame, column: str | None) -> pd.Series:
    if not column:
        return pd.Series([0] * len(df), index=df.index, dtype="float64")
    return df[column].map(_normalize_number).astype("float64")


def build_profitability_frame(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    result = pd.DataFrame()
    result["product_name"] = df[mapping["product_name"]].fillna("Unknown").astype(str).str.strip()

    for field in NUMERIC_FIELDS:
        result[field] = _series_or_zero(df, mapping.get(field))

    result["net_profit"] = (
        result["revenue"]
        - result["cost"]
        - result["commission"]
        - result["shipping"]
        - result["ads_spend"]
    )
    revenue = result["revenue"].where(result["revenue"] != 0)
    result["profit_margin"] = ((result["net_profit"] / revenue) * 100).fillna(0)
    return result


def product_level_profit(frame: pd.DataFrame) -> pd.DataFrame:
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
