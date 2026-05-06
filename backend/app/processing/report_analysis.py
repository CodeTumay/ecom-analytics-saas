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


def _profitability(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "product_name", "Product"))
    frame["revenue"] = _numeric(df, mapping, "revenue")
    frame["cost"] = _numeric(df, mapping, "cost") + _numeric(df, mapping, "other_expenses")

    commission_amount = _numeric(df, mapping, "commission")
    commission_rate = _numeric(df, mapping, "commission_rate")
    frame["commission"] = _first_non_zero(commission_amount, frame["revenue"] * commission_rate / 100)
    frame["shipping"] = _numeric(df, mapping, "shipping")
    frame = _finish_frame(frame)

    uploaded_profit = _numeric(df, mapping, "net_income")
    if mapping.get("net_income"):
        frame["net_profit"] = uploaded_profit
        frame["profit_margin"] = _safe_divide(frame["net_profit"], frame["revenue"], 100)

    detail = frame.copy()
    detail["date"] = _text(df, mapping, "date", "")
    detail["order_id"] = _text(df, mapping, "order_id", "")
    detail["commission_rate"] = commission_rate
    detail["other_expenses"] = _numeric(df, mapping, "other_expenses")
    return frame, _product_level_profit(frame), detail


def _income_expense(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "period", "Period"))
    gross_sales = _numeric(df, mapping, "gross_sales")
    returns = _numeric(df, mapping, "returns")
    net_sales = _numeric(df, mapping, "net_sales")
    revenue = _first_non_zero(net_sales, gross_sales - returns)

    product_costs = _numeric(df, mapping, "product_costs")
    marketplace_commissions = _numeric(df, mapping, "marketplace_commissions")
    shipping_expenses = _numeric(df, mapping, "shipping_expenses")
    ads_expenses = _numeric(df, mapping, "ads_expenses")
    operational_expenses = _numeric(df, mapping, "operational_expenses")
    total_expense = _numeric(df, mapping, "total_expense")
    detailed_expense = (
        product_costs + marketplace_commissions + shipping_expenses + ads_expenses + operational_expenses
    )

    frame["revenue"] = revenue
    frame["commission"] = marketplace_commissions
    frame["shipping"] = shipping_expenses
    frame["ads_spend"] = ads_expenses
    frame["cost"] = product_costs + operational_expenses
    frame["cost"] = frame["cost"].where(detailed_expense != 0, total_expense)
    frame = _finish_frame(frame)

    net_profit = _numeric(df, mapping, "net_profit")
    if mapping.get("net_profit"):
        frame["net_profit"] = net_profit
        frame["profit_margin"] = _safe_divide(frame["net_profit"], frame["revenue"], 100)

    detail = frame.copy()
    detail["gross_sales"] = gross_sales
    detail["returns"] = returns
    detail["total_expense"] = total_expense.where(total_expense != 0, detailed_expense)
    detail["ebitda"] = _numeric(df, mapping, "ebitda")
    return frame, _product_level_profit(frame), detail


def _pricing_analysis(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "product_name", "Product"))
    current_price = _numeric(df, mapping, "current_price")
    cost = _numeric(df, mapping, "cost")
    competitor_1 = _numeric(df, mapping, "competitor_price_1")
    competitor_2 = _numeric(df, mapping, "competitor_price_2")
    uploaded_market_avg = _numeric(df, mapping, "market_avg_price")
    calculated_market_avg = (competitor_1 + competitor_2) / 2
    market_avg = _first_non_zero(uploaded_market_avg, calculated_market_avg)
    min_price = _first_non_zero(_numeric(df, mapping, "min_price"), cost * 1.25)

    frame["revenue"] = current_price
    frame["cost"] = cost
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["sku"] = _text(df, mapping, "sku", "")
    detail["competitor_price_1"] = competitor_1
    detail["competitor_price_2"] = competitor_2
    detail["market_avg_price"] = market_avg
    detail["price_gap_pct"] = _first_non_zero(
        _numeric(df, mapping, "price_gap_pct"),
        _safe_divide(current_price - market_avg, market_avg, 100),
    )
    detail["min_price"] = min_price
    detail["suggested_price"] = _first_non_zero(_numeric(df, mapping, "suggested_price"), market_avg)
    detail["price_status"] = _text(df, mapping, "price_status", "")
    return frame, _product_level_profit(frame), detail


def _cash_flow(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "category", "Cash Flow"))
    cash_in = _numeric(df, mapping, "cash_in")
    cash_out = _numeric(df, mapping, "cash_out")
    frame["revenue"] = cash_in
    frame["cost"] = cash_out
    frame = _finish_frame(frame)

    running_balance = (cash_in - cash_out).cumsum()
    detail = frame.copy()
    detail["date"] = _text(df, mapping, "date", "")
    detail["transaction_type"] = _text(df, mapping, "transaction_type", "")
    detail["description"] = _text(df, mapping, "description", "")
    detail["daily_balance"] = _first_non_zero(_numeric(df, mapping, "daily_balance"), running_balance)
    detail["cumulative_balance"] = _first_non_zero(
        _numeric(df, mapping, "cumulative_balance"),
        detail["daily_balance"],
    )
    detail["expected_collection"] = _numeric(df, mapping, "expected_collection")
    detail["expected_payment"] = _numeric(df, mapping, "expected_payment")
    return frame, _product_level_profit(frame), detail


def _sales_performance(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    label = _text(df, mapping, "month", "").replace("", pd.NA).fillna(_text(df, mapping, "date", "Sales"))
    frame = _base_frame(df, label)
    revenue = _numeric(df, mapping, "revenue")
    order_count = _numeric(df, mapping, "order_count")
    target = _numeric(df, mapping, "target")
    previous = _numeric(df, mapping, "previous_year_same_day")
    frame["revenue"] = revenue
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["date"] = _text(df, mapping, "date", "")
    detail["day"] = _text(df, mapping, "day", "")
    detail["week"] = _numeric(df, mapping, "week")
    detail["order_count"] = order_count
    detail["average_basket"] = _first_non_zero(_numeric(df, mapping, "average_basket"), _safe_divide(revenue, order_count))
    detail["growth_pct"] = _first_non_zero(_numeric(df, mapping, "growth_pct"), _safe_divide(revenue - previous, previous, 100))
    detail["target"] = target
    detail["target_completion_pct"] = _first_non_zero(_numeric(df, mapping, "target_completion_pct"), _safe_divide(revenue, target, 100))
    return frame, _product_level_profit(frame), detail


def _product_analysis(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "product_name", "Product"))
    revenue = _numeric(df, mapping, "revenue")
    units_sold = _numeric(df, mapping, "units_sold")
    return_units = _numeric(df, mapping, "return_units")
    average_price = _first_non_zero(_numeric(df, mapping, "average_price"), _safe_divide(revenue, units_sold))
    frame["revenue"] = revenue
    frame["cost"] = average_price * return_units
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["sku"] = _text(df, mapping, "sku", "")
    detail["category"] = _text(df, mapping, "category", "")
    detail["units_sold"] = units_sold
    detail["return_units"] = return_units
    detail["return_rate"] = _first_non_zero(_numeric(df, mapping, "return_rate"), _safe_divide(return_units, units_sold, 100))
    detail["average_price"] = average_price
    detail["stock"] = _numeric(df, mapping, "stock")
    detail["stock_turnover"] = _first_non_zero(
        _numeric(df, mapping, "stock_turnover"),
        _safe_divide(units_sold, detail["stock"]),
    )
    total_revenue = pd.Series([float(revenue.sum())] * len(df), index=df.index)
    detail["revenue_share"] = _first_non_zero(_numeric(df, mapping, "revenue_share"), _safe_divide(revenue, total_revenue, 100))
    detail["abc_class"] = _text(df, mapping, "abc_class", "")
    return frame, _product_level_profit(frame), detail


def _trends(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "period", "Period"))
    revenue = _numeric(df, mapping, "revenue")
    moving_average = _first_non_zero(_numeric(df, mapping, "moving_average"), revenue.rolling(4, min_periods=1).mean())
    upper_limit = _first_non_zero(_numeric(df, mapping, "upper_limit"), moving_average * 1.2)
    lower_limit = _first_non_zero(_numeric(df, mapping, "lower_limit"), moving_average * 0.8)
    frame["revenue"] = revenue
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["moving_average"] = moving_average
    detail["trend_direction"] = _text(df, mapping, "trend_direction", "")
    detail["seasonality_index"] = _numeric(df, mapping, "seasonality_index")
    detail["forecast"] = _numeric(df, mapping, "forecast")
    detail["upper_limit"] = upper_limit
    detail["lower_limit"] = lower_limit
    return frame, _product_level_profit(frame), detail


def _commissions(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    marketplace = _text(df, mapping, "marketplace", "Marketplace")
    category = _text(df, mapping, "category", "")
    frame = _base_frame(df, marketplace.where(category == "", marketplace + " / " + category))
    revenue = _numeric(df, mapping, "revenue")
    commission_rate = _numeric(df, mapping, "commission_rate")
    commission = _first_non_zero(_numeric(df, mapping, "commission"), revenue * commission_rate / 100)
    additional_fees = _numeric(df, mapping, "additional_fees")
    frame["revenue"] = revenue
    frame["commission"] = commission
    frame["cost"] = additional_fees
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["marketplace"] = marketplace
    detail["category"] = category
    detail["commission_rate"] = commission_rate
    detail["additional_fees"] = additional_fees
    detail["platform_cost"] = _first_non_zero(_numeric(df, mapping, "platform_cost"), commission + additional_fees)
    detail["cost_sales_ratio"] = _first_non_zero(_numeric(df, mapping, "cost_sales_ratio"), _safe_divide(detail["platform_cost"], revenue, 100))
    return frame, _product_level_profit(frame), detail


def _shipping_logistics(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    carrier = _text(df, mapping, "carrier", "Carrier")
    region = _text(df, mapping, "region", "")
    frame = _base_frame(df, carrier.where(region == "", carrier + " / " + region))
    revenue = _numeric(df, mapping, "revenue")
    shipping = _numeric(df, mapping, "shipping")
    frame["revenue"] = revenue
    frame["shipping"] = shipping
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["order_id"] = _text(df, mapping, "order_id", "")
    detail["carrier"] = carrier
    detail["delivery_city"] = _text(df, mapping, "delivery_city", "")
    detail["region"] = region
    detail["weight_kg"] = _numeric(df, mapping, "weight_kg")
    detail["desi"] = _numeric(df, mapping, "desi")
    detail["shipping_revenue_ratio"] = _first_non_zero(
        _numeric(df, mapping, "shipping_revenue_ratio"),
        _safe_divide(shipping, revenue, 100),
    )
    detail["delivery_days"] = _numeric(df, mapping, "delivery_days")
    detail["damaged_lost"] = _text(df, mapping, "damaged_lost", "")
    return frame, _product_level_profit(frame), detail


def _ads_performance(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = _base_frame(df, _text(df, mapping, "campaign", "Campaign"))
    revenue = _numeric(df, mapping, "revenue")
    ads_spend = _numeric(df, mapping, "ads_spend")
    clicks = _numeric(df, mapping, "clicks")
    impressions = _numeric(df, mapping, "impressions")
    conversions = _numeric(df, mapping, "conversions")
    frame["revenue"] = revenue
    frame["ads_spend"] = ads_spend
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["platform"] = _text(df, mapping, "platform", "")
    detail["start_date"] = _text(df, mapping, "start_date", "")
    detail["impressions"] = impressions
    detail["clicks"] = clicks
    detail["ctr"] = _first_non_zero(_numeric(df, mapping, "ctr"), _safe_divide(clicks, impressions, 100))
    detail["conversions"] = conversions
    detail["conversion_rate"] = _first_non_zero(_numeric(df, mapping, "conversion_rate"), _safe_divide(conversions, clicks, 100))
    detail["roas"] = _first_non_zero(_numeric(df, mapping, "roas"), _safe_divide(revenue, ads_spend))
    detail["cpa"] = _first_non_zero(_numeric(df, mapping, "cpa"), _safe_divide(ads_spend, conversions))
    return frame, _product_level_profit(frame), detail


def _risk_alerts(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    risk_type = _text(df, mapping, "risk_type", "Risk")
    scope = _text(df, mapping, "scope", "Scope")
    frame = _base_frame(df, risk_type + " / " + scope)
    estimated_impact = _numeric(df, mapping, "estimated_impact")
    frame["cost"] = estimated_impact
    frame = _finish_frame(frame)

    detail = frame.copy()
    detail["risk_type"] = risk_type
    detail["scope"] = scope
    detail["risk_level"] = _text(df, mapping, "risk_level", "")
    detail["current_value"] = _numeric(df, mapping, "current_value")
    detail["threshold_value"] = _numeric(df, mapping, "threshold_value")
    detail["difference"] = _first_non_zero(
        _numeric(df, mapping, "difference"),
        detail["current_value"] - detail["threshold_value"],
    )
    detail["risk_score"] = _numeric(df, mapping, "risk_score")
    detail["estimated_impact"] = estimated_impact
    detail["mitigation_status"] = _text(df, mapping, "mitigation_status", "")
    detail["last_check_date"] = _text(df, mapping, "last_check_date", "")
    return frame, _product_level_profit(frame), detail


REPORT_BUILDERS = {
    "profitability": _profitability,
    "income_expense": _income_expense,
    "pricing_analysis": _pricing_analysis,
    "cash_flow": _cash_flow,
    "sales_performance": _sales_performance,
    "product_analysis": _product_analysis,
    "trends": _trends,
    "commissions": _commissions,
    "shipping_logistics": _shipping_logistics,
    "ads_performance": _ads_performance,
    "risk_alerts": _risk_alerts,
}


def build_report_analysis(df: pd.DataFrame, mapping: dict[str, str], report_type: str) -> dict:
    report = get_report_definition(report_type)
    builder = REPORT_BUILDERS.get(report.id)
    if builder is None:
        raise ValueError(f"Unsupported report type: {report_type}")

    order_frame, product_frame, detail = builder(df, mapping)
    analysis = build_analysis(order_frame, product_frame)
    return _add_common_metadata(analysis, report.id, df, detail)
