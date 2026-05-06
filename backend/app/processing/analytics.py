import pandas as pd


def _round_records(frame: pd.DataFrame) -> list[dict]:
    rounded = frame.copy()
    for column in rounded.select_dtypes(include="number").columns:
        rounded[column] = rounded[column].round(2)
    return rounded.to_dict(orient="records")


def build_analysis(order_frame: pd.DataFrame, product_frame: pd.DataFrame) -> dict:
    totals = {
        "revenue": round(float(order_frame["revenue"].sum()), 2),
        "cost": round(float(order_frame["cost"].sum()), 2),
        "commission": round(float(order_frame["commission"].sum()), 2),
        "shipping": round(float(order_frame["shipping"].sum()), 2),
        "ads_spend": round(float(order_frame["ads_spend"].sum()), 2),
        "profit": round(float(order_frame["net_profit"].sum()), 2),
    }
    totals["margin"] = round(
        (totals["profit"] / totals["revenue"] * 100) if totals["revenue"] else 0, 2
    )

    order_frame = order_frame.reset_index().rename(columns={"index": "order"})
    order_frame["order"] = order_frame["order"] + 1

    cost_breakdown = [
        {"name": "Product cost", "value": totals["cost"]},
        {"name": "Store area signal", "value": totals["commission"]},
        {"name": "Stock signal", "value": totals["shipping"]},
        {"name": "Inventory value", "value": totals["ads_spend"]},
    ]

    revenue_trends = (
        order_frame.assign(bucket=(order_frame.index // max(len(order_frame) // 8, 1)) + 1)
        .groupby("bucket")[["revenue", "net_profit"]]
        .sum()
        .reset_index()
        .rename(columns={"bucket": "period", "net_profit": "profit"})
    )

    loss_making = product_frame[product_frame["net_profit"] < 0].sort_values("net_profit")

    return {
        "totals": totals,
        "top_profitable_products": _round_records(product_frame.head(10)),
        "loss_making_products": _round_records(loss_making.head(10)),
        "revenue_trends": _round_records(revenue_trends),
        "cost_breakdown": cost_breakdown,
        "products": _round_records(product_frame),
        "orders": _round_records(order_frame.head(100)),
    }
