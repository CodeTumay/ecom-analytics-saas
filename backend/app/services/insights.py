from __future__ import annotations

def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0


def generate_insights(analysis: dict) -> list[dict[str, str | float]]:
    insights: list[dict[str, str | float]] = []
    totals = analysis.get("totals", {})
    revenue = _number(totals.get("revenue"))
    profit = _number(totals.get("profit"))
    margin = _number(totals.get("margin"))

    if revenue and margin >= 25:
        insights.append(
            {
                "severity": "success",
                "message": "Retail health is strong enough to support a growth story.",
                "recommendation": "Use the highest-margin collections as hero categories in the CEO or investor report.",
            }
        )
    elif revenue and margin < 12:
        insights.append(
            {
                "severity": "warning",
                "message": "Gross margin is below the healthy retail threshold.",
                "recommendation": "Review product cost, pricing, and markdown pressure before scaling this collection.",
            }
        )

    if profit < 0:
        insights.append(
            {
                "severity": "critical",
                "message": "The uploaded period is unprofitable overall.",
                "recommendation": "Prioritize margin repair, dead stock reduction, and high-cash inventory cleanup.",
            }
        )

    for row in analysis.get("detail_rows", [])[:200]:
        product = row.get("product_name") or "This SKU"
        collection = row.get("collection") or "this collection"
        store = row.get("store_name") or "this store"
        action = str(row.get("retail_action") or "")
        sell_through = _number(row.get("sell_through"))
        days_of_stock = _number(row.get("days_of_stock"))
        stock_turnover = _number(row.get("stock_turnover"))
        revenue_per_sqm = _number(row.get("revenue_per_sqm"))
        inventory_value = _number(row.get("inventory_value"))
        row_margin = _number(row.get("profit_margin"))

        if "Reorder" in action:
            insights.append(
                {
                    "severity": "critical",
                    "message": f"{product} is a reorder candidate.",
                    "recommendation": f"{collection} sells through quickly and may run out in about {round(days_of_stock)} days. Reproduce or transfer stock.",
                }
            )

        if "Hero" in action:
            insights.append(
                {
                    "severity": "success",
                    "message": f"{product} can be treated as a hero product.",
                    "recommendation": "Feature it in buying, merchandising, and investor story materials.",
                }
            )

        if "Markdown" in action:
            insights.append(
                {
                    "severity": "warning",
                    "message": f"{product} is tying up cash.",
                    "recommendation": "Move it to a stronger store, bundle it, or mark it down before it becomes dead stock.",
                }
            )

        if revenue_per_sqm and revenue_per_sqm < 5000:
            insights.append(
                {
                    "severity": "warning",
                    "message": f"{store} has low revenue per m².",
                    "recommendation": "Check product mix, window display, staff conversion, and local stock allocation.",
                }
            )

        if sell_through >= 70 and row_margin >= 20:
            insights.append(
                {
                    "severity": "success",
                    "message": f"{collection} has strong sell-through with healthy margin.",
                    "recommendation": "Use this as a hero collection signal for next buying and investor communication.",
                }
            )

        if inventory_value > 0 and stock_turnover < 0.5:
            insights.append(
                {
                    "severity": "warning",
                    "message": "Slow stock is locking cash.",
                    "recommendation": "Build a transfer or markdown list for SKUs with high inventory value and low turnover.",
                }
            )

        if len(insights) >= 20:
            break

    if not insights:
        insights.append(
            {
                "severity": "success",
                "message": "No critical retail health risk detected.",
                "recommendation": "Upload store, inventory, collection, and cost data together for sharper reorder and transfer recommendations.",
            }
        )

    return insights[:20]
