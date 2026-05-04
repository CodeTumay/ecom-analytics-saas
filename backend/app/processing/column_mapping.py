import re
from dataclasses import dataclass

import pandas as pd


CANONICAL_FIELDS = [
    "product_name",
    "revenue",
    "cost",
    "commission",
    "shipping",
    "ads_spend",
]

REQUIRED_FIELDS = ["product_name", "revenue", "cost"]

ALIASES = {
    "product_name": [
        "product",
        "productname",
        "item",
        "itemname",
        "sku",
        "title",
        "urun",
        "urunadi",
        "ürün",
        "ürünadı",
        "name",
    ],
    "revenue": [
        "revenue",
        "sales",
        "grosssales",
        "total",
        "price",
        "amount",
        "satis",
        "satış",
        "ciro",
        "gelir",
    ],
    "cost": ["cost", "cogs", "unitcost", "buyingprice", "maliyet", "urunmaliyeti"],
    "commission": ["commission", "marketplacefee", "referralfee", "komisyon"],
    "shipping": ["shipping", "shipment", "delivery", "cargo", "kargo", "nakliye"],
    "ads_spend": ["adspend", "ads", "advertising", "marketing", "ppc", "reklam", "reklamgideri"],
}


@dataclass(frozen=True)
class MappingResult:
    mapping: dict[str, str]
    missing_required: list[str]
    missing_optional: list[str]

    @property
    def needs_user_mapping(self) -> bool:
        return bool(self.missing_required)


def normalize_column_name(value: str) -> str:
    normalized = value.lower().strip()
    normalized = normalized.replace("ı", "i").replace("İ", "i")
    normalized = normalized.replace("ğ", "g").replace("ü", "u")
    normalized = normalized.replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return re.sub(r"[^a-z0-9]+", "", normalized)


def detect_mapping(df: pd.DataFrame) -> MappingResult:
    normalized_columns = {normalize_column_name(str(col)): str(col) for col in df.columns}
    mapping: dict[str, str] = {}

    for field in CANONICAL_FIELDS:
        aliases = [normalize_column_name(alias) for alias in [field, *ALIASES[field]]]
        for alias in aliases:
            if alias in normalized_columns:
                mapping[field] = normalized_columns[alias]
                break

    missing_required = [field for field in REQUIRED_FIELDS if field not in mapping]
    missing_optional = [
        field
        for field in CANONICAL_FIELDS
        if field not in mapping and field not in missing_required
    ]
    return MappingResult(mapping, missing_required, missing_optional)


def validate_user_mapping(df: pd.DataFrame, mapping: dict[str, str]) -> MappingResult:
    columns = {str(col) for col in df.columns}
    cleaned = {
        field: column
        for field, column in mapping.items()
        if field in CANONICAL_FIELDS and column in columns
    }
    missing_required = [field for field in REQUIRED_FIELDS if field not in cleaned]
    missing_optional = [
        field
        for field in CANONICAL_FIELDS
        if field not in cleaned and field not in missing_required
    ]
    return MappingResult(cleaned, missing_required, missing_optional)
