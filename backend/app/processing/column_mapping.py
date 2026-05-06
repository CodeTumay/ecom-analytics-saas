from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd

from app.processing.report_catalog import get_report_definition


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
    normalized = (
        normalized.replace("ı", "i")
        .replace("İ", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
        .replace("Ä±", "i")
        .replace("Ä°", "i")
        .replace("ÄŸ", "g")
        .replace("Ã¼", "u")
        .replace("ÅŸ", "s")
        .replace("Ã¶", "o")
        .replace("Ã§", "c")
    )
    normalized = unicodedata.normalize("NFKD", normalized)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", normalized)


def detect_mapping(df: pd.DataFrame, report_type: str | None = None) -> MappingResult:
    report = get_report_definition(report_type)
    normalized_columns = {normalize_column_name(str(col)): str(col) for col in df.columns}
    mapping: dict[str, str] = {}

    for field in report.fields:
        aliases = [normalize_column_name(alias) for alias in [field.key, *field.aliases]]
        for alias in aliases:
            if alias in normalized_columns:
                mapping[field.key] = normalized_columns[alias]
                break

    missing_required = [field for field in report.required_fields if field not in mapping]
    missing_optional = [
        field.key
        for field in report.fields
        if field.key not in mapping and field.key not in missing_required
    ]
    return MappingResult(mapping, missing_required, missing_optional)


def validate_user_mapping(
    df: pd.DataFrame, mapping: dict[str, str], report_type: str | None = None
) -> MappingResult:
    report = get_report_definition(report_type)
    columns = {str(col) for col in df.columns}
    cleaned = {
        field: column
        for field, column in mapping.items()
        if field in report.field_keys and column in columns
    }
    missing_required = [field for field in report.required_fields if field not in cleaned]
    missing_optional = [
        field.key
        for field in report.fields
        if field.key not in cleaned and field.key not in missing_required
    ]
    return MappingResult(cleaned, missing_required, missing_optional)
