from __future__ import annotations

import base64
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TRENDYOL_ORDERS_URL = "https://apigw.trendyol.com/integration/order/sellers/{seller_id}/orders"


@dataclass(frozen=True)
class TrendyolCredentials:
    seller_id: str
    api_key: str
    api_secret: str


class TrendyolApiError(RuntimeError):
    pass


def fetch_shipment_packages(
    credentials: TrendyolCredentials,
    *,
    start_date: int | None = None,
    end_date: int | None = None,
    page: int = 0,
    size: int = 200,
    status: str | None = None,
) -> dict[str, Any]:
    params: dict[str, str | int] = {
        "page": page,
        "size": min(size, 200),
        "orderByField": "PackageLastModifiedDate",
        "orderByDirection": "DESC",
    }
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    if status:
        params["status"] = status

    url = TRENDYOL_ORDERS_URL.format(seller_id=credentials.seller_id)
    auth = base64.b64encode(
        f"{credentials.api_key}:{credentials.api_secret}".encode("utf-8")
    ).decode("ascii")
    request = Request(
        f"{url}?{urlencode(params)}",
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "User-Agent": "ecom-analytics-saas/0.1",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise TrendyolApiError(f"Trendyol API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise TrendyolApiError(f"Could not reach Trendyol API: {exc.reason}") from exc


def packages_to_profitability_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for package in payload.get("content", []):
        package_shipping = _number(package.get("cargoPrice") or package.get("cargoAmount"))
        lines = package.get("lines") or package.get("items") or []
        for line in lines:
            quantity = _number(line.get("quantity") or line.get("amount") or 1) or 1
            unit_price = _number(
                line.get("price")
                or line.get("amount")
                or line.get("salePrice")
                or line.get("discountedPrice")
            )
            revenue = _number(line.get("totalPrice")) or unit_price * quantity
            rows.append(
                {
                    "product_name": (
                        line.get("productName")
                        or line.get("product_name")
                        or line.get("barcode")
                        or line.get("sku")
                        or "Trendyol product"
                    ),
                    "revenue": round(revenue, 2),
                    "cost": 0,
                    "commission": _number(
                        line.get("commission") or line.get("commissionAmount")
                    ),
                    "shipping": (
                        round(package_shipping / len(lines), 2)
                        if lines and package_shipping
                        else 0
                    ),
                    "ads_spend": 0,
                }
            )
    return rows


def write_profitability_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "product_name",
                "revenue",
                "cost",
                "commission",
                "shipping",
                "ads_spend",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(rows)


def _number(value: Any) -> float:
    if value is None or value == "":
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    normalized = str(value).strip()
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return 0
