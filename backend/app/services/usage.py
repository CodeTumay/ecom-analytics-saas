from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Plan, Upload, User


def monthly_upload_count(db: Session, user_id: int) -> int:
    now = datetime.now(timezone.utc)
    count = db.scalar(
        select(func.count(Upload.id)).where(
            Upload.user_id == user_id,
            extract("year", Upload.created_at) == now.year,
            extract("month", Upload.created_at) == now.month,
        )
    )
    return int(count or 0)


def assert_upload_allowed(db: Session, user: User) -> None:
    if user.plan == Plan.PRO:
        return

    if monthly_upload_count(db, user.id) >= settings.free_uploads_per_month:
        raise HTTPException(
            status_code=402,
            detail="Free plan limit reached. Upgrade to Pro for unlimited uploads.",
        )
