import pandas as pd

from app.processing.column_mapping import detect_mapping
from app.processing.profitability import build_profitability_frame, product_level_profit


def test_detects_marketplace_columns() -> None:
    df = pd.DataFrame(
        {
            "Ürün Adı": ["A"],
            "Satış": [100],
            "Maliyet": [55],
            "Komisyon": [10],
            "Kargo": [5],
            "Reklam": [8],
        }
    )

    result = detect_mapping(df)

    assert not result.needs_user_mapping
    assert result.mapping["product_name"] == "Ürün Adı"
    assert result.mapping["ads_spend"] == "Reklam"


def test_profitability_calculation() -> None:
    df = pd.DataFrame(
        {
            "Product": ["A", "A", "B"],
            "Revenue": [100, 50, 40],
            "Cost": [30, 20, 50],
            "Commission": [10, 5, 4],
            "Shipping": [5, 5, 5],
            "Ads": [15, 5, 0],
        }
    )
    mapping = detect_mapping(df).mapping

    orders = build_profitability_frame(df, mapping)
    products = product_level_profit(orders)

    assert orders["net_profit"].tolist() == [40, 15, -19]
    assert products.iloc[0]["product_name"] == "A"
    assert products.iloc[-1]["net_profit"] == -19
