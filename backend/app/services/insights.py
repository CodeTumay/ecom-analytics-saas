def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0


def generate_insights(analysis: dict) -> list[dict[str, str | float]]:
    totals = analysis["totals"]
    insights: list[dict[str, str | float]] = []
    report_type = analysis.get("report_type", "profitability")

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
        revenue_value = _number(product.get("revenue"))
        profit_gap = abs(_number(product.get("net_profit", product.get("profit"))))
        price_increase = round((profit_gap / revenue_value) * 100 + 5, 1) if revenue_value else 0
        insights.append(
            {
                "severity": "critical",
                "message": f"{product_name} is unprofitable.",
                "recommendation": f"Increase price by about {price_increase}% or reduce costs to target a positive margin.",
            }
        )

    for row in analysis.get("detail_rows", [])[:100]:
        if report_type == "pricing_analysis":
            name = row.get("product_name") or "Product"
            current_price = _number(row.get("revenue"))
            min_price = _number(row.get("min_price"))
            price_gap = _number(row.get("price_gap_pct"))
            if min_price and current_price < min_price:
                insights.append(
                    {
                        "severity": "critical",
                        "message": f"{name} is priced below minimum profitable price.",
                        "recommendation": "Raise the selling price or lower product cost before scaling this SKU.",
                    }
                )
            elif price_gap > 10:
                insights.append(
                    {
                        "severity": "warning",
                        "message": f"{name} is more expensive than the market average.",
                        "recommendation": "Review competitor prices and conversion rate before increasing ad spend.",
                    }
                )
            elif price_gap < -10:
                insights.append(
                    {
                        "severity": "success",
                        "message": f"{name} has room for a price increase.",
                        "recommendation": "Test a controlled price increase to improve margin.",
                    }
                )

        if report_type == "cash_flow":
            if _number(row.get("daily_balance")) < 0:
                insights.append(
                    {
                        "severity": "critical",
                        "message": "A cash balance row is negative.",
                        "recommendation": "Delay non-essential spend or accelerate collections for this period.",
                    }
                )
            if _number(row.get("expected_collection")) - _number(row.get("expected_payment")) < 0:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Expected payments exceed expected collections.",
                        "recommendation": "Prepare a cash buffer for the upcoming period.",
                    }
                )

        if report_type == "sales_performance":
            if _number(row.get("target_completion_pct")) and _number(row.get("target_completion_pct")) < 80:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Sales performance is below target.",
                        "recommendation": "Review traffic, conversion, and campaign support for this period.",
                    }
                )
            if _number(row.get("growth_pct")) < 0:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Negative growth detected.",
                        "recommendation": "Compare this period with product availability, ads, and pricing changes.",
                    }
                )

        if report_type == "product_analysis":
            name = row.get("product_name") or "Product"
            if _number(row.get("return_rate")) > 10:
                insights.append(
                    {
                        "severity": "warning",
                        "message": f"{name} has a high return rate.",
                        "recommendation": "Check product quality, listing accuracy, and packaging.",
                    }
                )
            if row.get("stock_turnover") not in ("", None) and _number(row.get("stock_turnover")) < 2:
                insights.append(
                    {
                        "severity": "warning",
                        "message": f"{name} is slow-moving stock.",
                        "recommendation": "Consider a bundle, campaign, or purchasing pause.",
                    }
                )

        if report_type == "trends":
            sales = _number(row.get("revenue"))
            if _number(row.get("upper_limit")) and sales > _number(row.get("upper_limit")):
                insights.append(
                    {
                        "severity": "success",
                        "message": "Sales exceeded the upper trend limit.",
                        "recommendation": "Check stock and fulfillment capacity before demand increases further.",
                    }
                )
            if _number(row.get("lower_limit")) and sales < _number(row.get("lower_limit")):
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Sales fell below the lower trend limit.",
                        "recommendation": "Review campaigns, pricing, and marketplace visibility.",
                    }
                )

        if report_type == "commissions" and _number(row.get("cost_sales_ratio")) > 20:
            insights.append(
                {
                    "severity": "warning",
                    "message": "Platform cost is high versus sales.",
                    "recommendation": "Compare marketplace commission, fulfillment fees, and alternative channels.",
                }
            )

        if report_type == "shipping_logistics":
            if _number(row.get("delivery_days")) > 5:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Late delivery risk detected.",
                        "recommendation": "Review carrier SLA and regional delivery performance.",
                    }
                )
            if _number(row.get("shipping_revenue_ratio")) > 15:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Shipping cost is high versus sales.",
                        "recommendation": "Check free-shipping threshold, desi, and carrier pricing.",
                    }
                )

        if report_type == "ads_performance":
            roas = _number(row.get("roas"))
            if roas and roas < 2:
                insights.append(
                    {
                        "severity": "critical",
                        "message": "ROAS is below the profitability threshold.",
                        "recommendation": "Pause or optimize this campaign before increasing budget.",
                    }
                )
            elif roas > 4:
                insights.append(
                    {
                        "severity": "success",
                        "message": "ROAS is strong.",
                        "recommendation": "Consider increasing budget gradually while monitoring margin.",
                    }
                )
            if _number(row.get("ctr")) and _number(row.get("ctr")) < 0.5:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "CTR is low.",
                        "recommendation": "Refresh creative, title, audience, or keyword targeting.",
                    }
                )

        if report_type == "risk_alerts":
            score = _number(row.get("risk_score"))
            if score >= 8:
                insights.append(
                    {
                        "severity": "critical",
                        "message": "Critical risk score detected.",
                        "recommendation": "Prioritize this risk and assign an owner immediately.",
                    }
                )
            elif score >= 5:
                insights.append(
                    {
                        "severity": "warning",
                        "message": "Medium risk score detected.",
                        "recommendation": "Monitor this risk and define a mitigation date.",
                    }
                )

    insights = insights[:20]

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
