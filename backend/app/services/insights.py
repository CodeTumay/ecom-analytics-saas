def generate_insights(analysis: dict) -> list[dict[str, str | float]]:
    totals = analysis["totals"]
    insights: list[dict[str, str | float]] = []

    revenue = totals.get("revenue", 0) or 0
    profit = totals.get("profit", 0) or 0
    ads_spend = totals.get("ads_spend", 0) or 0
    margin = totals.get("margin", 0) or 0

    if revenue and ads_spend / revenue > 0.18:
        insights.append(
            {
                "severity": "warning",
                "message": "Your ad spend is high versus revenue.",
                "recommendation": "Review campaigns above 18% ad-to-sales ratio and pause low-return products.",
            }
        )

    if profit < 0:
        insights.append(
            {
                "severity": "critical",
                "message": "This upload is unprofitable overall.",
                "recommendation": "Reduce variable costs or increase prices before scaling sales volume.",
            }
        )

    for product in analysis.get("loss_making_products", [])[:5]:
        product_name = product.get("product_name") or product.get("name") or "This product"
        revenue_value = product.get("revenue", 0) or 0
        profit_gap = abs(product.get("profit", 0) or 0)
        price_increase = round((profit_gap / revenue_value) * 100 + 5, 1) if revenue_value else 0
        insights.append(
            {
                "severity": "critical",
                "message": f"{product_name} is unprofitable.",
                "recommendation": f"Increase price by about {price_increase}% or reduce costs to target a positive margin.",
            }
        )

    if margin < 10 and revenue > 0:
        insights.append(
            {
                "severity": "warning",
                "message": "Your profit margin is thin.",
                "recommendation": "Aim for a 10-20% margin buffer after commission, shipping, and ads.",
            }
        )

    if not insights:
        insights.append(
            {
                "severity": "success",
                "message": "Profitability looks healthy in this upload.",
                "recommendation": "Monitor ad spend and shipping costs as sales volume grows.",
            }
        )

    return insights
