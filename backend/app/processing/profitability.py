import pandas as pd


NUMERIC_FIELDS = ["revenue", "cost", "commission", "shipping", "ads_spend"]


def _series_or_zero(df: pd.DataFrame, column: str | None) -> pd.Series:
    if not column:
        return pd.Series([0] * len(df), index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


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
