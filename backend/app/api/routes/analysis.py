from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Product, Upload, UploadStatus, User
from app.processing.report_catalog import serialize_report_catalog
from app.schemas.uploads import AnalysisOut, CombinedReportRequest, MappingRequest, UploadOut
from app.services.insights import generate_insights
from app.worker.tasks import process_upload

router = APIRouter()


def _get_owned_upload(db: Session, upload_id: int, user_id: int) -> Upload:
    upload = db.scalar(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == user_id)
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload


@router.get("/analysis/{upload_id}", response_model=AnalysisOut)
def get_analysis(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisOut:
    upload = _get_owned_upload(db, upload_id, current_user.id)
    return AnalysisOut(
        upload_id=upload.id,
        status=upload.status,
        report_type=(upload.mapping or {}).get("__report_type", "profitability"),
        mapping=upload.mapping,
        analysis=upload.analysis,
        error_message=upload.error_message,
    )


@router.get("/report-types")
def report_types() -> dict:
    return {"reports": serialize_report_catalog()}


def _empty_totals() -> dict[str, float]:
    return {
        "revenue": 0,
        "cost": 0,
        "commission": 0,
        "shipping": 0,
        "ads_spend": 0,
        "profit": 0,
        "margin": 0,
    }


def _round_totals(totals: dict[str, float]) -> dict[str, float]:
    revenue = totals.get("revenue", 0) or 0
    profit = totals.get("profit", 0) or 0
    totals["margin"] = (profit / revenue * 100) if revenue else 0
    return {key: round(float(value), 2) for key, value in totals.items()}


def _merge_products(analyses: list[dict]) -> list[dict]:
    products: dict[str, dict[str, float | str]] = {}
    for analysis in analyses:
        for row in analysis.get("products", []):
            name = str(row.get("product_name") or row.get("name") or "Unknown")
            current = products.setdefault(
                name,
                {
                    "product_name": name,
                    "revenue": 0,
                    "cost": 0,
                    "commission": 0,
                    "shipping": 0,
                    "ads_spend": 0,
                    "net_profit": 0,
                    "profit_margin": 0,
                },
            )
            for field in ["revenue", "cost", "commission", "shipping", "ads_spend", "net_profit"]:
                current[field] = float(current[field]) + float(row.get(field, 0) or 0)

    for row in products.values():
        revenue = float(row["revenue"])
        profit = float(row["net_profit"])
        row["profit_margin"] = round((profit / revenue * 100) if revenue else 0, 2)
        for field in ["revenue", "cost", "commission", "shipping", "ads_spend", "net_profit"]:
            row[field] = round(float(row[field]), 2)
    return sorted(products.values(), key=lambda row: float(row["net_profit"]), reverse=True)


@router.post("/reports/combined")
def combined_report(
    payload: CombinedReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    if not payload.upload_ids:
        raise HTTPException(status_code=400, detail="Select at least one report")

    uploads = db.scalars(
        select(Upload).where(
            Upload.id.in_(payload.upload_ids),
            Upload.user_id == current_user.id,
            Upload.status == UploadStatus.COMPLETED,
        )
    ).all()
    if len(uploads) != len(set(payload.upload_ids)):
        raise HTTPException(status_code=400, detail="Some reports are missing or not completed")

    analyses = [upload.analysis or {} for upload in uploads]
    totals = _empty_totals()
    for analysis in analyses:
        analysis_totals = analysis.get("totals", {})
        for field in ["revenue", "cost", "commission", "shipping", "ads_spend", "profit"]:
            totals[field] += float(analysis_totals.get(field, 0) or 0)

    products = _merge_products(analyses)
    rounded_totals = _round_totals(totals)
    combined = {
        "report_type": "combined",
        "totals": rounded_totals,
        "products": products,
        "top_profitable_products": products[:10],
        "loss_making_products": [row for row in reversed(products) if float(row["net_profit"]) < 0][:10],
        "cost_breakdown": [
            {"name": "Product cost", "value": rounded_totals["cost"]},
            {"name": "Commission", "value": rounded_totals["commission"]},
            {"name": "Shipping", "value": rounded_totals["shipping"]},
            {"name": "Ads", "value": rounded_totals["ads_spend"]},
        ],
        "included_reports": [
            {
                "id": upload.id,
                "filename": upload.original_filename,
                "report_type": (upload.mapping or {}).get("__report_type", "profitability"),
                "totals": (upload.analysis or {}).get("totals", {}),
            }
            for upload in uploads
        ],
    }
    combined["insights"] = generate_insights(combined)
    return combined


@router.post("/analysis/{upload_id}/mapping", response_model=UploadOut)
def update_mapping(
    upload_id: int,
    payload: MappingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Upload:
    upload = _get_owned_upload(db, upload_id, current_user.id)
    upload.mapping = payload.mapping
    upload.status = UploadStatus.QUEUED
    upload.error_message = None
    upload.analysis = None
    db.execute(delete(Product).where(Product.upload_id == upload.id))
    db.commit()
    db.refresh(upload)

    try:
        report_type = payload.mapping.get("__report_type") or (upload.mapping or {}).get("__report_type")
        process_upload.delay(upload.id, payload.mapping, report_type)
    except Exception as exc:
        upload.status = UploadStatus.FAILED
        upload.error_message = f"Could not enqueue processing job: {exc}"
        db.commit()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=upload.error_message) from exc

    return upload
