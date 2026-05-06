import pandas as pd

from app.processing.column_mapping import detect_mapping
from app.processing.processor import process_file, read_retail_file
from app.processing.report_analysis import build_report_analysis


def test_detects_retail_health_columns() -> None:
    df = pd.DataFrame(
        {
            "\u00dcr\u00fcn Ad\u0131": ["A"],
            "Koleksiyon": ["Pearl"],
            "Ma\u011faza": ["Nisantasi"],
            "Sat\u0131\u015f Adedi": [8],
            "Ciro": [100],
            "Maliyet": [55],
            "Stok": [12],
        }
    )

    result = detect_mapping(df)

    assert not result.needs_user_mapping
    assert result.mapping["product_name"] == "\u00dcr\u00fcn Ad\u0131"
    assert result.mapping["collection"] == "Koleksiyon"
    assert result.mapping["store_name"] == "Ma\u011faza"
    assert result.mapping["stock"] == "Stok"


def test_retail_health_generates_reorder_and_markdown_actions() -> None:
    df = pd.DataFrame(
        {
            "Product": ["Pearl Necklace", "Stone Bracelet"],
            "Collection": ["Pearl", "Natural Stone"],
            "Revenue": [1200, 120],
            "Cost": [450, 80],
            "Units Sold": [60, 1],
            "Stock": [8, 50],
        }
    )
    mapping = detect_mapping(df).mapping

    analysis = build_report_analysis(df, mapping, "retail_health")
    actions = {row["product_name"]: row["retail_action"] for row in analysis["detail_rows"]}

    assert analysis["report_type"] == "retail_health"
    assert actions["Pearl Necklace"] == "Reorder / yeniden uret"
    assert actions["Stone Bracelet"] == "Markdown veya transfer"


def test_reads_semicolon_csv_and_decimal_comma(tmp_path) -> None:
    csv_path = tmp_path / "retail_health.csv"
    csv_path.write_text(
        "Product;Collection;Store;Revenue;Cost;Units Sold;Stock\n"
        "Pearl Necklace;Pearl;Nisantasi;1.234,56;500,10;24;6\n"
        "Stone Bracelet;Natural Stone;Kadikoy;40,00;50,00;1;30\n",
        encoding="utf-8",
    )

    df = read_retail_file(csv_path)
    mapping = detect_mapping(df).mapping
    analysis = build_report_analysis(df, mapping, "retail_health")

    assert list(df.columns) == ["Product", "Collection", "Store", "Revenue", "Cost", "Units Sold", "Stock"]
    assert round(float(analysis["totals"]["revenue"]), 2) == 1274.56
    assert round(float(analysis["totals"]["profit"]), 2) == 724.46


def test_process_file_defaults_to_retail_health(tmp_path) -> None:
    csv_path = tmp_path / "upload.csv"
    csv_path.write_text(
        "Product,Revenue,Cost,Units Sold,Stock\n"
        "Pearl Ring,900,320,18,5\n",
        encoding="utf-8",
    )

    result = process_file(csv_path)

    assert result["status"] == "completed"
    assert result["report_type"] == "retail_health"
