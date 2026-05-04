from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Product, Upload, UploadStatus, User
from app.schemas.uploads import AnalysisOut, MappingRequest, UploadOut
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
        mapping=upload.mapping,
        analysis=upload.analysis,
        error_message=upload.error_message,
    )


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
        process_upload.delay(upload.id, payload.mapping)
    except Exception as exc:
        upload.status = UploadStatus.FAILED
        upload.error_message = f"Could not enqueue processing job: {exc}"
        db.commit()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=upload.error_message) from exc

    return upload
