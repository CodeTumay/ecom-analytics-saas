from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Product, Upload, User
from app.services.usage import monthly_upload_count

router = APIRouter()


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict:
    upload_ids_query = select(Upload.id).where(Upload.user_id == current_user.id)
    totals = db.execute(
        select(
            func.coalesce(func.sum(Product.revenue), 0),
            func.coalesce(func.sum(Product.cost), 0),
            func.coalesce(func.sum(Product.commission), 0),
            func.coalesce(func.sum(Product.shipping), 0),
            func.coalesce(func.sum(Product.ads_spend), 0),
            func.coalesce(func.sum(Product.profit), 0),
        ).where(Product.upload_id.in_(upload_ids_query))
    ).one()

    recent_uploads = db.scalars(
        select(Upload)
        .where(Upload.user_id == current_user.id)
        .order_by(Upload.created_at.desc())
        .limit(10)
    ).all()

    return {
        "plan": current_user.plan,
        "usage": {"uploads_this_month": monthly_upload_count(db, current_user.id)},
        "totals": {
            "revenue": round(float(totals[0]), 2),
            "cost": round(float(totals[1]), 2),
            "commission": round(float(totals[2]), 2),
            "shipping": round(float(totals[3]), 2),
            "ads_spend": round(float(totals[4]), 2),
            "profit": round(float(totals[5]), 2),
        },
        "recent_uploads": [
            {
                "id": upload.id,
                "filename": upload.original_filename,
                "status": upload.status,
                "report_type": (upload.mapping or {}).get("__report_type", "retail_health"),
                "created_at": upload.created_at,
            }
            for upload in recent_uploads
        ],
    }
