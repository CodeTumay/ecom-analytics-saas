import pandas as pd

from app.processing.column_mapping import detect_mapping
from app.processing.processor import read_marketplace_file
from app.processing.profitability import build_profitability_frame, product_level_profit


def test_detects_marketplace_columns() -> None:
    df = pd.DataFrame(
        {
            "\u00dcr\u00fcn Ad\u0131": ["A"],
            "Sat\u0131\u015f": [100],
            "Maliyet": [55],
            "Komisyon": [10],
            "Kargo": [5],
            "Reklam": [8],
        }
    )

    result = detect_mapping(df)

    assert not result.needs_user_mapping
    assert result.mapping["product_name"] == "\u00dcr\u00fcn Ad\u0131"
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


def test_reads_semicolon_csv_and_decimal_comma(tmp_path) -> None:
    csv_path = tmp_path / "marketplace.csv"
    csv_path.write_text(
        "Product;Revenue;Cost;Commission;Shipping;Ads\n"
        "A;1.234,56;500,10;100,20;25,00;50,00\n"
        "B;40,00;50,00;5,00;5,00;0,00\n",
        encoding="utf-8",
    )

    df = read_marketplace_file(csv_path)
    mapping = detect_mapping(df).mapping
    orders = build_profitability_frame(df, mapping)

    assert list(df.columns) == ["Product", "Revenue", "Cost", "Commission", "Shipping", "Ads"]
    assert round(float(orders.iloc[0]["revenue"]), 2) == 1234.56
    assert round(float(orders.iloc[0]["net_profit"]), 2) == 559.26
    assert round(float(orders.iloc[1]["net_profit"]), 2) == -20
